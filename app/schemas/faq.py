from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FAQBase(BaseModel):
    question: str = Field(
        min_length=5,
        max_length=500,
        examples=["How do I reset my password?"],
    )
    answer: str = Field(
        min_length=5,
        examples=["Go to Settings > Security and click Reset Password."],
    )
    category: str | None = Field(
        default=None,
        max_length=100,
        examples=["account"],
    )
    is_published: bool = Field(default=True)


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    question: str | None = Field(
        default=None,
        min_length=5,
        max_length=500,
    )
    answer: str | None = Field(
        default=None,
        min_length=5,
    )
    category: str | None = Field(
        default=None,
        max_length=100,
    )
    is_published: bool | None = None


class FAQResponse(FAQBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
