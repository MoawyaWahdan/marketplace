from sqlmodel import SQLModel, Field
from enum import Enum
from sqlalchemy import UniqueConstraint


class ListingCategory(Enum):
    HOME_ESSENTIALS = 1
    FURNITURES = 2
    ELECTRONICS = 3
    TOYS = 4


class ListingCondition(Enum):
    NEW = 1
    USED_LIKE_NEW = 2
    USED_GOOD = 3
    USED_FAIR = 4


class ListingBase(SQLModel):
    title: str = Field(..., min_length=5, max_length=30)
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