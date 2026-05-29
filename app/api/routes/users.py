from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from typing import Annotated
from app.api.deps import SessionDep
from app.db.database import get_session
from app.models.user import UserDB
from app.schemas.user import UserCreate, UserPublic
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):

    db_user = UserDB(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    return db_user


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
    users = session.execute(select(UserDB).offset(offset).limit(limit)).scalars().all()

    return users
