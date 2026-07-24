from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ticket import TicketPriority, TicketStatus
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services import ticket_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/",
    response_model=list[TicketResponse],
)
def get_tickets(
    db: DbSession,
    status_filter: Annotated[
        TicketStatus | None,
        Query(alias="status"),
    ] = None,
    priority: Annotated[TicketPriority | None, Query()] = None,
) -> list[TicketResponse]:
    return ticket_service.list_tickets(
        db,
        status=status_filter,
        priority=priority,
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(ticket_id: int, db: DbSession) -> TicketResponse:
    ticket = ticket_service.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    db: DbSession,
) -> TicketResponse:
    return ticket_service.create_ticket(db, ticket_data)


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: DbSession,
) -> TicketResponse:
    ticket = ticket_service.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket_service.update_ticket(db, ticket, ticket_data)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(ticket_id: int, db: DbSession) -> None:
    ticket = ticket_service.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    ticket_service.delete_ticket(db, ticket)
