from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.ticket import TicketPriority, TicketStatus


class TicketBase(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
        examples=["Unable to upload document"],
    )
    description: str = Field(
        min_length=5,
        examples=["PDF upload fails with a 500 error."],
    )
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    requester_name: str | None = Field(
        default=None,
        max_length=100,
        examples=["Jane Doe"],
    )
    requester_email: EmailStr | None = Field(
        default=None,
        examples=["jane@example.com"],
    )


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        min_length=5,
    )
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    requester_name: str | None = Field(
        default=None,
        max_length=100,
    )
    requester_email: EmailStr | None = None


class TicketResponse(TicketBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
