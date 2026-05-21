from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
    BackgroundTasks,
    UploadFile,
    File,
    Request,
    Form,
    Query,
)
import asyncio
from pathlib import Path
import time
import os
import logging
import uuid


from sqlmodel import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func
from typing import Annotated
from pydantic import Field

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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["Listings"])

IMAGES_PATH = "app/static/images/listing_images"
IMAGES_URL_PATH = "/static/images/listing_images"


def generate_image_name(client_image_name):
    ext = Path(client_image_name).suffix
    return f"{uuid.uuid4()}{ext}"


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
    saved_images = []

    listing = session.get(ListingDB, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.seller_id != user.id:
        raise HTTPException(403, "Not authorized")

    try:
        for file in images:
            image_name = generate_image_name(file.filename)
            image_full_path = Path(IMAGES_PATH) / image_name
            db_image = ListingImageDB(listing_id=listing_id, name=image_name)
            with open(image_full_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            saved_images.append(image_full_path)
            session.add(db_image)
            session.flush()
            images_public.append(
                ListingImagePublic(
                    id=db_image.id, url=f"{IMAGES_URL_PATH}/{image_name}"
                )
            )

        session.commit()

    except Exception as e:
        logger.exception("Error while saving image")
        for image_path in saved_images:
            if os.path.exists(image_path):
                os.remove(image_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't save images",
        )

    return images_public


@router.get(
    "/{listing_id}/images_ids",
    response_model=list[int],
    summary="Get list of images_ids for given listing_id",
    description="Get list of images_ids for given listing_id",
)
def get_listing_imgaes_ids(user: UserDep, session: SessionDep, listing_id: int):
    return session.exec(
        select(ListingImageDB.id).where(ListingImageDB.listing_id == listing_id)
    ).all()


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
        session.flush()
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.exception("Database constraint error")

        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Database constraint error"
        )
    return db_listing


def get_listing_public(listing_db: ListingDB, images_db: list[ListingImageDB]):
    listing_public = ListingPublic(**listing_db.model_dump())
    for image_db in images_db:
        listing_public.images.append(
            ListingImagePublic(id=image_db.id, url=f"{IMAGES_URL_PATH}/{image_db.name}")
        )
    return listing_public


def get_listings_public(listings_db: list[ListingDB], session):
    listings_public = []
    for listing_db in listings_db:
        images_db = session.exec(
            select(ListingImageDB).where(ListingImageDB.listing_id == listing_db.id)
        ).all()
        listings_public.append(get_listing_public(listing_db, images_db))
    return listings_public


@router.get(
    "/",
    response_model=list[ListingPublic],
    summary="Get all listings",
    description="Return all listings in the marketplace (excluding sold items).",
)
async def get_listings(session=Depends(get_session)):
    listings_db = session.exec(
        select(ListingDB).where(ListingDB.is_sold == False)
    ).all()
    return get_listings_public(listings_db, session)


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

    count = session.exec(
        select(func.count(ListingDB.id)).where(ListingDB.seller_id == user.id)
    ).one()
    listings = session.exec(
        select(ListingDB)
        .where(ListingDB.seller_id == user.id)
        .order_by(ListingDB.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    public_listings = get_listings_public(listings, session)

    return {"listings": public_listings, "total": count}


async def get_my_purchases(user: UserDep, session: SessionDep):

    listings = session.exec(
        select(ListingDB).where(ListingDB.buyer_id == user.id)
    ).all()

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
    description="Return the listing belongs to this user which has id = listing_id",
    response_model=ListingPublic,
)
async def get_listing(listing_id: int, session: SessionDep):
    listing_db = session.get(ListingDB, listing_id)

    if listing_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    images_db = session.exec(
        select(ListingImageDB).where(ListingImageDB.listing_id == listing_id)
    ).all()

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
        listing = session.exec(
            select(ListingDB).where(
                and_(
                    ListingDB.title == listing_update.title, ListingDB.id != listing_id
                )
            )
        ).first()
        if listing is not None:
            raise HTTPException(
                status_code=400, detail="A listing with this title already exists"
            )

    # Perform the update
    update_data = listing_update.model_dump(exclude_unset=True)
    db_listing.sqlmodel_update(update_data)
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
    images_ids = session.exec(
        select(ListingImageDB.id).where(ListingImageDB.listing_id == listing_id)
    ).all()
    for id in images_ids:
        db_image = session.get(ListingImageDB, id)
        image_name = db_image.name
        image_full_path = os.path.join(IMAGES_PATH, image_name)
        os.remove(image_full_path)

    session.exec(delete(ListingImageDB).where(ListingImageDB.listing_id == listing_id))

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

    images_ids = session.exec(
        select(ListingImageDB.id).where(ListingImageDB.listing_id == listing_id)
    ).all()
    for id in images_ids:
        db_image = session.get(ListingImageDB, id)
        image_name = db_image.name
        image_full_path = os.path.join(IMAGES_PATH, image_name)
        os.remove(image_full_path)

    session.exec(delete(ListingImageDB).where(ListingImageDB.listing_id == listing_id))

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

    count = session.exec(
        select(func.count(ListingDB.id)).where(
            ListingDB.seller_id == user.id, *conditions
        )
    ).one()

    listings = session.exec(
        select(ListingDB)
        .where(ListingDB.seller_id == user.id, *conditions)
        .order_by(ListingDB.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    listings_public = get_listings_public(listings, session)

    return {"listings": listings_public, "total": count}
