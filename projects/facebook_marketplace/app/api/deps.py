from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.user import UserDB
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except InvalidTokenError:
        raise credentials_exception

    user = session.exec(select(UserDB).where(UserDB.username == username)).first()

    if not user:
        raise credentials_exception

    return user


UserDep = Annotated[UserDB, Depends(get_current_user)]