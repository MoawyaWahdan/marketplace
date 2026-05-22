from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from sqlalchemy import UniqueConstraint


class UserBase(SQLModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserDB(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    __table_args__ = (
        UniqueConstraint("username"),
        UniqueConstraint("email"),
    )
