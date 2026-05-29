from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(password, hash_password):
    return password_hash.verify(password, hash_password)


def create_access_token(sub: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": expire}

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
