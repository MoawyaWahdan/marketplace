from pydantic import BaseModel, Field
from app.models.listing import ListingCategory, ListingCondition
from typing import Annotated


class ListingCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=150)
    price: float = Field(..., ge=0)
    description: str
    condition: ListingCondition
    category: ListingCategory
    sku: str | None = None


class ListingImagePublic(BaseModel):
    id: int
    url: str


class ListingPublic(ListingCreate):
    id: int
    seller_id: int
    buyer_id: int | None = None
    is_sold: bool
    images: list[ListingImagePublic] = Field(default_factory=list)


class ListingUpdate(BaseModel):
    title: str | None = None
    price: float | None = None
    description: str | None = None
    condition: ListingCondition | None = None
    category: ListingCategory | None = None
    sku: str | None = None
