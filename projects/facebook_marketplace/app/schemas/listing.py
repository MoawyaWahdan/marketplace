from pydantic import BaseModel, Field
from app.models.listing import ListingCategory, ListingCondition


class ListingCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=30)
    price: float = Field(..., ge=0)
    description: str
    condition: ListingCondition
    category: ListingCategory
    sku: str | None = None


class ListingPublic(ListingCreate):
    id: int
    seller_id: int
    buyer_id: int | None = None
    is_sold: bool


class ListingUpdate(BaseModel):
    title: str | None = None
    price: float | None = None
    description: str | None = None
    condition: ListingCondition | None = None
    category: ListingCategory | None = None
    sku: str | None = None