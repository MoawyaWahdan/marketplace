from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
    UploadFile,
    Query,
)

import logging


from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func, select, delete
from typing import Annotated

from app.db.database import get_session
from app.models.listing import ListingDB
from app.schemas.listing import (
    ListingCreate,
    ListingPublic,
    ListingUpdate,
    ListingImagePublic,
    ListingMark,
    ListingPage,
)
from app.models.listing_image import ListingImageDB
from app.api.deps import UserDep, SessionDep
from app.utils.utils import upload_image_to_s3, get_image_url, delete_image_from_s3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post(
    "/{listing_id}/upload_images",
    response_model=list[ListingImagePublic],
    summary="Upload listing images",
    description="Upload images to the listing with id = listing_id",
)
async def upload_listing_images(
    listing_id: Annotated[int, Path(ge=1)],
    user: UserDep,
    session: SessionDep,
    images: list[UploadFile],
):
    images_public = []
    uploaded_images = []

    listing = session.get(ListingDB, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.seller_id != user.id:
        raise HTTPException(403, "Not authorized")

    try:
        for file in images:
            object_key = upload_image_to_s3(file)
            db_image = ListingImageDB(listing_id=listing_id, object_key=object_key)

            session.add(db_image)
            session.flush()

            images_public.append(
                ListingImagePublic(id=db_image.id, url=get_image_url(object_key))
            )

            uploaded_images.append(object_key)

        session.commit()

    except Exception as e:
        logger.exception("Error while uploading image")
        for image in uploaded_images:
            delete_image_from_s3(image)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't upload images",
        )

    return images_public


@router.get(
    "/{listing_id}/images_ids",
    response_model=list[int],
    summary="Get list of images_ids for given listing_id",
    description="Get list of images_ids for given listing_id",
)
def get_listing_imgaes_ids(user: UserDep, session: SessionDep, listing_id: int):
    return (
        session.execute(
            select(ListingImageDB.id).where(ListingImageDB.listing_id == listing_id)
        )
        .scalars()
        .all()
    )


@router.post(
    "/",
    response_model=ListingPublic,
    summary="Create new listing",
    description="The user can use this to create new listing, the listing is part of the seller listings",
)
async def create_listing(
    user: UserDep,
    session: SessionDep,
    listing: ListingCreate,
):

    db_listing = ListingDB(**listing.model_dump(), seller_id=user.id)

    session.add(db_listing)

    try:
        session.commit()
        session.refresh(db_listing)
    except IntegrityError as e:
        session.rollback()
        logger.exception("Database constraint error")

        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Database constraint error"
        )
    return db_listing


def get_listing_public(listing_db: ListingDB, images_db: list[ListingImageDB]):
    listing_public = ListingPublic.model_validate(listing_db)
    for image_db in images_db:
        listing_public.images.append(
            ListingImagePublic(id=image_db.id, url=get_image_url(image_db.object_key))
        )
    return listing_public


def get_listings_public(listings_db: list[ListingDB], session):
    listings_public = []
    for listing_db in listings_db:
        images_db = (
            session.execute(
                select(ListingImageDB).where(ListingImageDB.listing_id == listing_db.id)
            )
            .scalars()
            .all()
        )
        listings_public.append(get_listing_public(listing_db, images_db))
    return listings_public


@router.get(
    "/",
    response_model=ListingPage,
    summary="Get all listings",
    description="Return all listings in the marketplace (excluding sold items).",
)
async def get_all_listings(
    user: UserDep,
    session=Depends(get_session),
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=10, le=100)] = 10,
):
    logger.info("get_all_listings called")
    count = session.execute(select(func.count(ListingDB.id))).scalar()

    listings_db = (
        session.execute(
            select(ListingDB)
            .where(ListingDB.is_sold == False)
            .order_by(ListingDB.id.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    public_listings = get_listings_public(listings_db, session)
    return {"listings": public_listings, "total": count}


@router.get(
    "/my/selling/",
    summary="Get listings created by user",
    description="Get all the listings created by the user",
    response_model=ListingPage,
)
async def get_my_selling_listings(
    user: UserDep,
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=10, le=100)] = 10,
):

    count = session.execute(
        select(func.count(ListingDB.id)).where(ListingDB.seller_id == user.id)
    ).scalar()
    listings = (
        session.execute(
            select(ListingDB)
            .where(ListingDB.seller_id == user.id)
            .order_by(ListingDB.id.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    public_listings = get_listings_public(listings, session)

    return {"listings": public_listings, "total": count}


async def get_my_purchases(user: UserDep, session: SessionDep):

    listings = (
        session.execute(select(ListingDB).where(ListingDB.buyer_id == user.id))
        .scalars()
        .all()
    )

    return listings


@router.patch(
    "/{listing_id}/status",
    summary="Mark listing to availble/sold",
    description="Mark listing with id=listing_id to availble/sold. The user can mark his own listings only",
)
async def update_listing_status(
    listing_id: int, listing_mark: ListingMark, user: UserDep, session: SessionDep
):
    listing = session.get(ListingDB, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.seller_id != user.id:
        raise HTTPException(400, "You can mark your own listing only")
    if listing.is_sold and listing_mark.is_sold:
        raise HTTPException(400, "Listing already sold")
    if not listing.is_sold and not listing_mark.is_sold:
        raise HTTPException(400, "Listing already availble")

    listing.is_sold = listing_mark.is_sold
    session.add(listing)
    session.commit()

    return {"message": "Listing status updated successfully"}


@router.get(
    "/{listing_id}/",
    summary="Get specific listing",
    description="Return the listing with id = listing_id",
    response_model=ListingPublic,
)
async def get_listing(listing_id: int, user: UserDep, session: SessionDep):
    listing_db = session.get(ListingDB, listing_id)

    if listing_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    images_db = (
        session.execute(
            select(ListingImageDB).where(ListingImageDB.listing_id == listing_id)
        )
        .scalars()
        .all()
    )

    return get_listing_public(listing_db, images_db)


@router.patch(
    "/{listing_id}",
    response_model=ListingPublic,
    summary="Partially update your listing",
    description="Update one or more fields of a listing you own. Only provided fields are changed.",
)
async def update_listing(
    listing_id: Annotated[int, Path(ge=1)],
    listing_update: ListingUpdate,
    current_user: UserDep,
    session: SessionDep,
):
    # Find listing in database
    db_listing = session.get(ListingDB, listing_id)

    if db_listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if db_listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own listings",
        )

    # Duplicate title check (if title is being updated)
    if listing_update.title is not None:
        listing = (
            session.execute(
                select(ListingDB).where(
                    and_(
                        ListingDB.title == listing_update.title,
                        ListingDB.id != listing_id,
                    )
                )
            )
            .scalars()
            .first()
        )
        if listing is not None:
            raise HTTPException(
                status_code=400, detail="A listing with this title already exists"
            )

    # Perform the update
    update_data = listing_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_listing, key, value)
    session.add(db_listing)
    session.commit()
    session.refresh(db_listing)

    return db_listing


@router.delete(
    "/{listing_id}",
    summary="Delete listing",
    description="Delete the listing with id = listing_id created by current user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_listing(
    listing_id: int,
    user: UserDep,
    session: SessionDep,
):
    listing = session.get(ListingDB, listing_id)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if listing.seller_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own listings",
        )

    # 1- delete the listing images
    images_ids = (
        session.execute(
            select(ListingImageDB.id).where(ListingImageDB.listing_id == listing_id)
        )
        .scalars()
        .all()
    )
    for id in images_ids:
        db_image = session.get(ListingImageDB, id)
        object_key = db_image.object_key
        delete_image_from_s3(object_key)

    session.execute(
        delete(ListingImageDB).where(ListingImageDB.listing_id == listing_id)
    )

    # 2- delete the listing
    session.delete(listing)
    session.commit()


@router.delete(
    "/{listing_id}/images",
    summary="Delete listing images",
    description="Delete the images of listing with id = listing_id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_listing_images(
    listing_id: int,
    user: UserDep,
    session: SessionDep,
):
    listing = session.get(ListingDB, listing_id)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    if listing.seller_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own listings",
        )

    images_ids = (
        session.execute(
            select(ListingImageDB.id).where(ListingImageDB.listing_id == listing_id)
        )
        .scalars()
        .all()
    )
    for id in images_ids:
        db_image = session.get(ListingImageDB, id)
        object_key = db_image.object_key
        delete_image_from_s3(object_key)

    session.execute(
        delete(ListingImageDB).where(ListingImageDB.listing_id == listing_id)
    )

    session.commit()


@router.get(
    "/search/my",
    summary="search my listings",
    description="reurn listings with title containing given words in the query",
    response_model=ListingPage,
)
def search_my_listings(
    title: Annotated[str, Query()],
    user: UserDep,
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=10, le=100)] = 10,
):

    words = title.strip().split()
    conditions = [ListingDB.title.ilike(f"%{word}%") for word in words]

    count = session.execute(
        select(func.count(ListingDB.id)).where(
            ListingDB.seller_id == user.id, *conditions
        )
    ).scalar()

    listings = (
        session.execute(
            select(ListingDB)
            .where(ListingDB.seller_id == user.id, *conditions)
            .order_by(ListingDB.id.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    listings_public = get_listings_public(listings, session)

    return {"listings": listings_public, "total": count}


@router.get(
    "/search",
    summary="search my listings",
    description="reurn listings with title containing given words in the query",
    response_model=ListingPage,
)
def search_all_listings(
    title: Annotated[str, Query()],
    user: UserDep,
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=10, le=100)] = 10,
):

    words = title.strip().split()
    conditions = [ListingDB.title.ilike(f"%{word}%") for word in words]

    count = session.execute(
        select(func.count(ListingDB.id)).where(*conditions)
    ).scalar()

    listings = (
        session.execute(
            select(ListingDB)
            .where(*conditions)
            .order_by(ListingDB.id.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    listings_public = get_listings_public(listings, session)

    return {"listings": listings_public, "total": count}
