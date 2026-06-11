from pydantic import BaseModel, Field


class ListingImagePublic(BaseModel):
    id: int | None = Field(default=None, primary_key=True)
    object_key: str
    listing_id: int = Field(foreign_key="listingdb.id")
