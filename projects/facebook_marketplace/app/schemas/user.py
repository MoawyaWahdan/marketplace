from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=3)


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr