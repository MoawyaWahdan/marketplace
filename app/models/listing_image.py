from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String
from app.db.database import Base


from sqlalchemy import UniqueConstraint


class ListingImageDB(Base):
    __tablename__ = "listing_images"

    __table_args__ = (
        UniqueConstraint("object_key", name="uq_listing_images_object_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    listing_id: Mapped[int] = mapped_column(
        ForeignKey(
            "listings.id", ondelete="CASCADE", name="fk_listing_images_listing_id"
        ),
        nullable=False,
        index=True,
    )

    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
