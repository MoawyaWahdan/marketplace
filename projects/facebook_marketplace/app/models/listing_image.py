from sqlmodel import SQLModel, Field


class ListingImageDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listingdb.id")
    name: str
