from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class UserBase(SQLModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserDB(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str