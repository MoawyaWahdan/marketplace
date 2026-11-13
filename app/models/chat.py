from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, func, UniqueConstraint
from app.db.database import Base
from datetime import datetime


class ChatDB(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE")
    )

    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (UniqueConstraint("listing_id", "buyer_id"),)
