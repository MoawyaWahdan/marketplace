from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.db.database import get_session
from app.models.user import UserDB
from app.core.security import verify_password, create_access_token, DUMMY_HASH

router = APIRouter()


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    user = session.exec(select(UserDB).where(UserDB.username == form_data.username)).first()

    if not user:
        verify_password(form_data.password, DUMMY_HASH)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}