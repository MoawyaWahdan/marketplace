from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey
from app.db.database import Base


class ListingImageDB(Base):
    __tablename__ = "listing_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    name: Mapped[str] = mapped_column()
