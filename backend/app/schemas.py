from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ListingIn(BaseModel):
    business_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=50)
    source: str = Field(min_length=1, max_length=120)

class BulkListingsIn(BaseModel):
    listings: list[ListingIn] = Field(min_length=1, max_length=5000)

class ListingOut(ListingIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class CountItem(BaseModel):
    label: str
    count: int

class DashboardSummary(BaseModel):
    total_listings: int
    distinct_cities: int
    distinct_categories: int
    distinct_sources: int
