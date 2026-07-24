from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate


def list_faqs(db: Session, *, published_only: bool = False) -> list[FAQ]:
    stmt = select(FAQ).order_by(FAQ.id)
    if published_only:
        stmt = stmt.where(FAQ.is_published.is_(True))
    return list(db.scalars(stmt).all())


def get_faq(db: Session, faq_id: int) -> FAQ | None:
    return db.get(FAQ, faq_id)


def create_faq(db: Session, data: FAQCreate) -> FAQ:
    faq = FAQ(**data.model_dump())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def update_faq(db: Session, faq: FAQ, data: FAQUpdate) -> FAQ:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(faq, field, value)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def delete_faq(db: Session, faq: FAQ) -> None:
    db.delete(faq)
    db.commit()
