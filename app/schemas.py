from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=120)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=1)


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=1, max_length=120)
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, min_length=1)


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ReviewAnalysisRequest(BaseModel):
    comment: str = Field(..., min_length=1, description="Customer review text")
    rating: int = Field(..., ge=1, le=5)
    customer_name: str = Field(default="Anonymous", min_length=1, max_length=120)


class ReviewAnalysisResponse(BaseModel):
    review_id: int
    review: str
    rating: int
    customer_name: str
    model: str
    sentiment: str
    summary: str
    key_issues: list[str]
    suggestions: list[str]
    raw_response: str | None = None


class BulkReviewAnalysisResponse(BaseModel):
    total_reviews: int
    average_rating: float
    rating_breakdown: dict[str, int]
    model: str
    overall_sentiment: str
    summary: str
    common_themes: list[str]
    key_issues: list[str]
    suggestions: list[str]
    raw_response: str | None = None
