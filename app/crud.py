from sqlalchemy.orm import Session

from app import models, schemas


def get_reviews(
    db: Session, skip: int = 0, limit: int = 100, rating: int | None = None
) -> list[models.Review]:
    query = db.query(models.Review)
    if rating is not None:
        query = query.filter(models.Review.rating == rating)
    return query.order_by(models.Review.id.desc()).offset(skip).limit(limit).all()


def get_review(db: Session, review_id: int) -> models.Review | None:
    return db.query(models.Review).filter(models.Review.id == review_id).first()


def create_review(db: Session, review: schemas.ReviewCreate) -> models.Review:
    db_review = models.Review(**review.model_dump())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(
    db: Session, review_id: int, review: schemas.ReviewUpdate
) -> models.Review | None:
    db_review = get_review(db, review_id)
    if not db_review:
        return None

    updates = review.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_review, field, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int) -> bool:
    db_review = get_review(db, review_id)
    if not db_review:
        return False
    db.delete(db_review)
    db.commit()
    return True
