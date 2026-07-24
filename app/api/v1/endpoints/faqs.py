from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.faq import FAQCreate, FAQResponse, FAQUpdate
from app.services import faq_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/",
    response_model=list[FAQResponse],
)
def get_faqs(
    db: DbSession,
    published_only: Annotated[bool, Query()] = False,
) -> list[FAQResponse]:
    return faq_service.list_faqs(db, published_only=published_only)


@router.get(
    "/{faq_id}",
    response_model=FAQResponse,
)
def get_faq(faq_id: int, db: DbSession) -> FAQResponse:
    faq = faq_service.get_faq(db, faq_id)
    if faq is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    return faq


@router.post(
    "/",
    response_model=FAQResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_faq(faq_data: FAQCreate, db: DbSession) -> FAQResponse:
    return faq_service.create_faq(db, faq_data)


@router.patch(
    "/{faq_id}",
    response_model=FAQResponse,
)
def update_faq(
    faq_id: int,
    faq_data: FAQUpdate,
    db: DbSession,
) -> FAQResponse:
    faq = faq_service.get_faq(db, faq_id)
    if faq is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    return faq_service.update_faq(db, faq, faq_data)


@router.delete(
    "/{faq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_faq(faq_id: int, db: DbSession) -> None:
    faq = faq_service.get_faq(db, faq_id)
    if faq is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    faq_service.delete_faq(db, faq)
