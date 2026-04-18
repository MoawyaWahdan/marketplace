from datetime import datetime, timedelta, timezone
from typing import Annotated
from enum import Enum
import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field, EmailStr
import itertools
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy import UniqueConstraint, and_
from sqlalchemy.exc import IntegrityError


class ListingCategory(Enum):
    HOME_ESSENTIALS = 1
    FURNITURES = 2
    ELECTRONICS = 3
    TOYS = 4


class ListingCondition(Enum):
    NEW = 1
    USED_LIKE_NEW = 2
    USED_GOOD = 3
    USED_FAIR = 4


class ListingBase(SQLModel):
    title: str = Field(..., min_length=5, max_length=30)
    price: float = Field(..., ge=0)
    description: str = Field(..., min_length=5, max_length=3000)
    condition: ListingCondition
    category: ListingCategory
    is_sold: bool = Field(default=False)


class ListingCreate(ListingBase):
    sku: str | None = Field(
        default=None, description="Optional SKU (like on Facebook Marketplace)"
    )


class ListingDB(ListingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seller_id: int | None = Field(default=None, foreign_key="userdb.id")
    sku: str | None = Field(
        default=None, description="Optional SKU (like on Facebook Marketplace)"
    )
    buyer_id: int | None = Field(default=None, foreign_key="userdb.id")
    __table_args__ = (UniqueConstraint("seller_id", "title"),)


class ListingPublic(ListingBase):
    id: int
    seller_id: int
    buyer_id: int | None = None
    sku: str | None = None


class ListingUpdate(BaseModel):
    buyer_id: int | None = None
    title: str | None = Field(default=None, min_length=5, max_length=30)
    price: float | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, min_length=5, max_length=3000)
    condition: ListingCondition | None = None
    category: ListingCategory | None = None
    sku: str | None = Field(
        default=None, description="Optional SKU (like on Facebook Marketplace)"
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(SQLModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserDB(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    password: str = Field(..., min_length=3)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_user_by_username(username: str, session: Session) -> UserDB | None:
    statement = select(UserDB).where(UserDB.username == username)
    result = session.exec(statement).first()
    return result


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(password, hash_password):
    return password_hash.verify(password, hash_password)


def authenticate_user(username: str, password: str, session: Session):
    user = get_user_by_username(username, session)
    if not user:
        # Prevent timing attacks
        verify_password(password, DUMMY_HASH)
        return False

    if verify_password(password, user.hashed_password):
        return user
    return False


def create_access_token(sub: str, expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": sub,
        "exp": expire,
    }

    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expire_time_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(form_data.username, token_expire_time_delta)
    return Token(access_token=access_token, token_type="bearer")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> UserPublic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(username, session)
    if user is None:
        raise credentials_exception

    return user  # Now returns UserDB which is fine (or convert to User if needed)


######
UserDep = Annotated[UserPublic, Depends(get_current_user)]
######


@app.post(
    "/users/",
    summary="Create new account",
    description="Create new account, given username, password, email.",
    tags=["Users"],
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
def create_new_account(user_create: UserCreate, session: SessionDep):
    # Check if email already exists
    existing_email = session.exec(
        select(UserDB).where(UserDB.email == user_create.email)
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already used"
        )

    # Check if username already exists
    existing_username = session.exec(
        select(UserDB).where(UserDB.username == user_create.username)
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="username already used"
        )

    # Hash the password and create new user
    hash_password = get_password_hash(user_create.password)

    new_user = UserDB(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hash_password,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Return public version (without hashed_password)
    return UserPublic.model_validate(new_user)


@app.get(
    "/listings/my/selling/",
    tags=["Listings"],
    summary="Get listings created by user",
    description="Get all the listings created by the user",
    response_model=list[ListingPublic],
)
async def get_my_selling_listings(user: UserDep, session: SessionDep):

    listings = session.exec(
        select(ListingDB).where(ListingDB.seller_id == user.id)
    ).all()
    return listings


@app.post(
    "/listings/",
    status_code=status.HTTP_201_CREATED,
    response_model=ListingPublic,
    tags=["Listings"],
    description="Create new listing",
    summary="The user can use this to create new listing, the listing is part of the seller dashboard",
)
async def create_seller_listing(
    user: Annotated[UserPublic, Depends(get_current_user)],
    listing: ListingCreate,
    session: SessionDep,
):

    db_listing = ListingDB.model_validate(listing)
    db_listing.seller_id = user.id
    session.add(db_listing)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Duplicate listing")
    session.refresh(db_listing)
    return db_listing


@app.get(
    "/listings/my/purchases/",
    tags=["Listings"],
    description="Return all the listings that the user bought",
    summary="Get user purchases",
    response_model=list[ListingPublic],
)
async def get_my_purchases(user: UserDep, session: SessionDep):

    listings = session.exec(
        select(ListingDB).where(ListingDB.buyer_id == user.id)
    ).all()

    return listings


@app.post(
    "/listings/{listing_id}/buy",
    tags=["Listings"],
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


@app.get(
    "/listings/",
    tags=["Listings"],
    response_model=list[ListingPublic],
    summary="Get all listings",
    description="Return all listings in the marketplace (including sold items).",
)
async def get_all_listings(session: SessionDep):
    listings = session.exec(select(ListingDB).where(ListingDB.is_sold == False)).all()
    return listings


@app.get(
    "/listings/{listing_id}",
    tags=["Listings"],
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


@app.patch(
    "/listings/{listing_id}/",
    tags=["Listings"],
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


@app.delete(
    "/listings/{listing_id}",
    summary="Delete listing",
    description="Delete the listing with id = listing_id created by current user",
    tags=["Listings"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_listing(listing_id: int, user: UserDep, session: SessionDep):
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
