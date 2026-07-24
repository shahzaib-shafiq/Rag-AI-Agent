from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate


def list_tickets(
    db: Session,
    *,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
) -> list[Ticket]:
    stmt = select(Ticket).order_by(Ticket.id)
    if status is not None:
        stmt = stmt.where(Ticket.status == status.value)
    if priority is not None:
        stmt = stmt.where(Ticket.priority == priority.value)
    return list(db.scalars(stmt).all())


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    payload = data.model_dump()
    payload["status"] = payload["status"].value
    payload["priority"] = payload["priority"].value
    ticket = Ticket(**payload)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(db: Session, ticket: Ticket, data: TicketUpdate) -> Ticket:
    updates = data.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] is not None:
        updates["status"] = updates["status"].value
    if "priority" in updates and updates["priority"] is not None:
        updates["priority"] = updates["priority"].value
    for field, value in updates.items():
        setattr(ticket, field, value)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket: Ticket) -> None:
    db.delete(ticket)
    db.commit()
