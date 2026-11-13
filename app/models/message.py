from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, func, String
from app.db.database import Base
from datetime import datetime


class MessageDB(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    content: Mapped[str] = mapped_column(String(5000))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
