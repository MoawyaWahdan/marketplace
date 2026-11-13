from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.message import MessagePublic


class ChatPublic(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    created_at: datetime
    messages: list[MessagePublic] = []
