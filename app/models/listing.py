from enum import Enum


class ListingCategory(str, Enum):
    HOME_ESSENTIALS = "Home essentials"
    FURNITURES = "Furnitures"
    ELECTRONICS = "Electronics"
    TOYS = "Toys"


class ListingCondition(str, Enum):
    NEW = "New"
    USED_LIKE_NEW = "Used like new"
    USED_GOOD = "Used good"
    USED_FAIR = "Used fair"


from sqlalchemy import String, UniqueConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from sqlalchemy import Enum as SQLEnum, ForeignKey
from decimal import Decimal


class ListingDB(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    description: Mapped[str] = mapped_column(String(30000))
    category: Mapped[ListingCategory] = mapped_column(SQLEnum(ListingCategory))
    condition: Mapped[ListingCondition] = mapped_column(SQLEnum(ListingCondition))
    is_sold: Mapped[bool] = mapped_column(default=False)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    buyer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
    )
    sku: Mapped[str | None] = mapped_column()

    __table_args__ = (UniqueConstraint("seller_id", "title"),)
