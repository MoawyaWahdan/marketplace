from sqlmodel import SQLModel, Field
from enum import Enum
from sqlalchemy import UniqueConstraint


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


class ListingDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=5, max_length=150)
    price: float = Field(ge=0)
    description: str = Field(min_length=5, max_length=3000)
    condition: ListingCondition
    category: ListingCategory
    is_sold: bool = Field(default=False)
    seller_id: int = Field(foreign_key="userdb.id")
    buyer_id: int | None = Field(default=None, foreign_key="userdb.id")
    sku: str | None = None

    __table_args__ = (UniqueConstraint("seller_id", "title"),)
