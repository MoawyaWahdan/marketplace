from enum import Enum
from sqlalchemy import (
    String,
    UniqueConstraint,
    Numeric,
    Enum as SQLEnum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from decimal import Decimal
from datetime import datetime


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

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (UniqueConstraint("seller_id", "title"),)
