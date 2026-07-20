from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", response_model=list[schemas.ReviewRead])
def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    rating: int | None = Query(None, ge=1, le=5),
    db: Session = Depends(get_db),
):
    return crud.get_reviews(db, skip=skip, limit=limit, rating=rating)


@router.get("/{review_id}", response_model=schemas.ReviewRead)
def read_review(review_id: int, db: Session = Depends(get_db)):
    review = crud.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


@router.post("/", response_model=schemas.ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    return crud.create_review(db, review)


@router.put("/{review_id}", response_model=schemas.ReviewRead)
def update_review(
    review_id: int, review: schemas.ReviewUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_review(db, review_id, review)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return updated


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
