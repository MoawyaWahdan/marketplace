from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from typing import Annotated
from app.api.deps import SessionDep
from app.db.database import get_session
from app.models.user import UserDB
from app.schemas.user import UserCreate, UserPublic
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    existing = session.exec(
        select(UserDB).where(UserDB.username == user.username)
    ).first()
    if existing:
        raise HTTPException(400, "Username taken")

    db_user = UserDB(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


from fastapi import APIRouter, Query
from typing import Annotated
from sqlmodel import select


@router.get(
    "/",
    response_model=list[UserPublic],
    summary="Return list of users",
    description="Return list (limit) of available users starting at offset",
)
def get_users(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    users = session.exec(select(UserDB).offset(offset).limit(limit)).all()

    return users
