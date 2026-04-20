from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.db.database import get_session
from app.models.user import UserDB
from app.schemas.user import UserCreate, UserPublic
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, session=Depends(get_session)):
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
