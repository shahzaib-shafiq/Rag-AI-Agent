"""Seed the reviews table from feedback.txt."""

from __future__ import annotations

import re
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Review
from app.schemas import ReviewCreate

LINE_PATTERN = re.compile(
    r"^\[(?P<rating>\d)/5\]\s+(?P<name>[^-]+)\s+-\s+(?P<comment>.+)$"
)


def parse_feedback_file(path: Path) -> list[ReviewCreate]:
    reviews: list[ReviewCreate] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        match = LINE_PATTERN.match(line)
        if not match:
            continue
        reviews.append(
            ReviewCreate(
                customer_name=match.group("name").strip(),
                rating=int(match.group("rating")),
                comment=match.group("comment").strip(),
            )
        )
    return reviews


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    feedback_path = Path(__file__).resolve().parent.parent / "feedback.txt"
    parsed = parse_feedback_file(feedback_path)

    db = SessionLocal()
    try:
        existing = db.query(Review).count()
        if existing:
            print(f"Skipping seed — {existing} reviews already exist.")
            return

        for item in parsed:
            db.add(Review(**item.model_dump()))
        db.commit()
        print(f"Seeded {len(parsed)} reviews from feedback.txt")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
