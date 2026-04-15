from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class ReviewCreateModel(BaseModel):
    book_uid: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewResponseModel(BaseModel):
    uid: uuid.UUID
    book_uid: uuid.UUID
    user_uid: uuid.UUID
    rating: int
    comment: str | None = None
    created_at: datetime
    updated_at: datetime


class ReviewUpdateModel(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None
