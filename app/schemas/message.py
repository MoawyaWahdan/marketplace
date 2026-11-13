from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class MessagePublic(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
