from datetime import datetime

from pydantic import BaseModel


class JobListingResponse(BaseModel):
    id: int
    site: str | None
    job_url: str | None
    title: str | None
    company: str | None
    location: str | None
    date_posted: datetime | None
    description: str | None
    applied: bool | None
    favourite: bool | None
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True  #
