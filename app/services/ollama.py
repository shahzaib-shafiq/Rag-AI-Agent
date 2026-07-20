import json
import re
from collections import Counter

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.models import Review
from app.schemas import (
    BulkReviewAnalysisResponse,
    ReviewAnalysisRequest,
    ReviewAnalysisResponse,
)

SYSTEM_PROMPT = """You are a product analyst for a food delivery app.
Given a customer review, analyze it and suggest concrete improvements for the app, restaurant partners, or operations.

Respond with ONLY valid JSON in this exact shape:
{
  "sentiment": "positive" | "neutral" | "negative" | "mixed",
  "summary": "one short sentence summarizing the review",
  "key_issues": ["issue 1", "issue 2"],
  "suggestions": ["actionable improvement 1", "actionable improvement 2", "actionable improvement 3"]
}

Rules:
- suggestions must be specific and actionable
- if the review is positive, still suggest ways to reinforce what worked
- key_issues can be an empty list for fully positive reviews
- do not include markdown or extra text outside the JSON object
"""

BULK_SYSTEM_PROMPT = """You are a product analyst for a food delivery app.
You will receive a list of customer reviews. Analyze them as a whole and recommend product/ops improvements.

Respond with ONLY valid JSON in this exact shape:
{
  "overall_sentiment": "positive" | "neutral" | "negative" | "mixed",
  "summary": "2-3 sentence overview of what customers are saying",
  "common_themes": ["theme 1", "theme 2", "theme 3"],
  "key_issues": ["top recurring issue 1", "top recurring issue 2"],
  "suggestions": ["prioritized actionable improvement 1", "improvement 2", "improvement 3", "improvement 4", "improvement 5"]
}

Rules:
- prioritize frequent and high-impact problems
- suggestions must be specific and actionable for a food delivery app
- include strengths to keep if reviews are mixed/positive
- do not include markdown or extra text outside the JSON object
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("Model did not return valid JSON")


async def _chat_json(system_prompt: str, user_prompt: str) -> tuple[dict, str]:
    body = {
        "model": settings.ollama_model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0.2},
    }

    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json=body,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach Ollama at {settings.ollama_base_url}: {exc}",
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama error ({response.status_code}): {response.text}",
        )

    data = response.json()
    content = data.get("message", {}).get("content", "")
    if not content:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama returned an empty response",
        )

    try:
        return _extract_json(content), content
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to parse Ollama response: {exc}",
        ) from exc


def _format_reviews_for_prompt(reviews: list[Review]) -> str:
    lines: list[str] = []
    for review in reviews:
        lines.append(
            f"- [id={review.id}] {review.customer_name} | {review.rating}/5 | {review.comment}"
        )
    return "\n".join(lines)


def _rating_breakdown(reviews: list[Review]) -> dict[str, int]:
    counts = Counter(review.rating for review in reviews)
    return {str(stars): counts.get(stars, 0) for stars in range(1, 6)}


async def analyze_review(payload: ReviewAnalysisRequest) -> ReviewAnalysisResponse:
    user_prompt = (
        f"Customer name: {payload.customer_name}\n"
        f"Rating: {payload.rating}/5\n"
        f"Review: {payload.comment}"
    )
    parsed, content = await _chat_json(SYSTEM_PROMPT, user_prompt)
    return ReviewAnalysisResponse(
        review_id=0,
        review=payload.comment,
        rating=payload.rating,
        customer_name=payload.customer_name,
        model=settings.ollama_model,
        sentiment=parsed.get("sentiment", "neutral"),
        summary=parsed.get("summary", ""),
        key_issues=parsed.get("key_issues", []) or [],
        suggestions=parsed.get("suggestions", []) or [],
        raw_response=content,
    )


async def analyze_all_reviews(db: Session) -> BulkReviewAnalysisResponse:
    reviews = crud.get_reviews(db, skip=0, limit=1000)
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found in the database",
        )

    average_rating = round(sum(r.rating for r in reviews) / len(reviews), 2)
    user_prompt = (
        f"Total reviews: {len(reviews)}\n"
        f"Average rating: {average_rating}/5\n"
        f"Rating breakdown: {_rating_breakdown(reviews)}\n\n"
        f"Reviews:\n{_format_reviews_for_prompt(reviews)}"
    )

    parsed, content = await _chat_json(BULK_SYSTEM_PROMPT, user_prompt)
    return BulkReviewAnalysisResponse(
        total_reviews=len(reviews),
        average_rating=average_rating,
        rating_breakdown=_rating_breakdown(reviews),
        model=settings.ollama_model,
        overall_sentiment=parsed.get("overall_sentiment", "mixed"),
        summary=parsed.get("summary", ""),
        common_themes=parsed.get("common_themes", []) or [],
        key_issues=parsed.get("key_issues", []) or [],
        suggestions=parsed.get("suggestions", []) or [],
        raw_response=content,
    )
