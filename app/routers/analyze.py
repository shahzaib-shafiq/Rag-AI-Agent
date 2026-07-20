from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.schemas import (
    BulkReviewAnalysisResponse,
    ReviewAnalysisRequest,
    ReviewAnalysisResponse,
)
from app.services.ollama import analyze_all_reviews, analyze_review

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.get("/all", response_model=BulkReviewAnalysisResponse)
async def analyze_all_customer_reviews(db: Session = Depends(get_db)):
    """Fetch all reviews from the DB, analyze them with Ollama, and return suggestions."""
    return await analyze_all_reviews(db)


@router.post("/", response_model=ReviewAnalysisResponse)
async def analyze_customer_review(
    payload: ReviewAnalysisRequest,
    db: Session = Depends(get_db),
):
    """Analyze a review with Ollama, save it to the DB, and return suggestions."""
    analysis = await analyze_review(payload)

    saved = crud.create_review(
        db,
        schemas.ReviewCreate(
            customer_name=payload.customer_name,
            rating=payload.rating,
            comment=payload.comment,
        ),
    )

    return analysis.model_copy(
        update={
            "review_id": saved.id,
            "customer_name": saved.customer_name,
            "rating": saved.rating,
        }
    )
