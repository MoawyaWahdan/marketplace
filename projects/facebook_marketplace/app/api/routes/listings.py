from fastapi import APIRouter, Depends, HTTPException, status, Path, BackgroundTasks
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from typing import Annotated

from app.db.database import get_session
from app.models.listing import ListingDB
from app.schemas.listing import ListingCreate, ListingPublic, ListingUpdate
from app.api.deps import UserDep, SessionDep
import asyncio

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post(
    "/",
    response_model=ListingPublic,
    summary="Create new listing",
    description="The user can use this to create new listing, the listing is part of the seller dashboard",
)
def create_listing(listing: ListingCreate, user: UserDep, session: SessionDep):
    db_listing = ListingDB.model_validate(listing)
    db_listing.seller_id = user.id
    session.add(db_listing)
    try:
        session.commit()
        session.refresh(db_listing)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicate listing")
    return db_listing


@router.get(
    "/",
    response_model=list[ListingPublic],
    summary="Get all listings",
    description="Return all listings in the marketplace (excluding sold items).",
)
def get_listings(session=Depends(get_session)):
    return session.exec(select(ListingDB).where(ListingDB.is_sold == False)).all()


@router.get(
    "/my/selling/",
    summary="Get listings created by user",
    description="Get all the listings created by the user",
    response_model=list[ListingPublic],
)
async def get_my_selling_listings(user: UserDep, session: SessionDep):

    listings = session.exec(
        select(ListingDB).where(ListingDB.seller_id == user.id)
    ).all()
    return listings


async def get_my_purchases(user: UserDep, session: SessionDep):

    listings = session.exec(
        select(ListingDB).where(ListingDB.buyer_id == user.id)
    ).all()

    return listings


@router.post(
    "/{listing_id}/buy",
    description="The current user but the listing with id=listing_id",
    summary="Buy listing",
)
async def buy_listing(listing_id: int, user: UserDep, session: SessionDep):
    listing = session.get(ListingDB, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.seller_id == user.id:
        raise HTTPException(400, "You cannot buy your own listing")
    if listing.is_sold:
        raise HTTPException(400, "Listing already sold")

    listing.is_sold = True
    listing.buyer_id = user.id
    session.add(listing)
    session.commit()
    session.refresh(listing)

    return {"message": "Listing purchased successfully"}


@router.get(
    "/{listing_id}/",
    summary="Get specific listing",
    description="Return the listing belongs to this user which has id = listing_id",
    response_model=ListingPublic,
)
async def get_listing(listing_id: int, session: SessionDep):
    listing = session.get(ListingDB, listing_id)

    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )
    return listing


@router.patch(
    "/{listing_id}/",
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


async def background_task(message: str):
    await asyncio.sleep(5)
    print(message)


@router.delete(
    "/{listing_id}",
    summary="Delete listing",
    description="Delete the listing with id = listing_id created by current user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_listing(
    background_tasks: BackgroundTasks,
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
    session.delete(listing)
    session.commit()

    background_tasks.add_task(background_task, f"listing {listing_id} deleted")
