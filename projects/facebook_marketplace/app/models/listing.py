from sqlmodel import SQLModel, Field
from enum import Enum
from sqlalchemy import UniqueConstraint


class ListingCategory(str, Enum):
    HOME_ESSENTIALS = "home_essentials"
    FURNITURES = "furnitures"
    ELECTRONICS = "electronics"
    TOYS = "toys"


class ListingCondition(str, Enum):
    NEW = "new"
    USED_LIKE_NEW = "used_like_new"
    USED_GOOD = "used_good"
    USED_FAIR = "used_fair"


class ListingBase(SQLModel):
    title: str = Field(..., min_length=5, max_length=150)
    price: float = Field(..., ge=0)
    description: str = Field(..., min_length=5, max_length=3000)
    condition: ListingCondition
    category: ListingCategory
    is_sold: bool = Field(default=False)


class ListingDB(ListingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seller_id: int | None = Field(default=None, foreign_key="userdb.id")
    buyer_id: int | None = Field(default=None, foreign_key="userdb.id")
    sku: str | None = None

    __table_args__ = (UniqueConstraint("seller_id", "title"),)
