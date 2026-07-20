"use client";

import type { Review } from "@/lib/types";

type Props = {
  reviews: Review[];
  selectedId: number | null;
  onSelect: (id: number) => void;
};

export function ReviewList({ reviews, selectedId, onSelect }: Props) {
  if (!reviews.length) {
    return <p className="empty">No reviews yet. Add one to get started.</p>;
  }

  return (
    <ul className="review-list">
      {reviews.map((review, index) => (
        <li
          key={review.id}
          className={selectedId === review.id ? "review-item selected" : "review-item"}
          style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}
        >
          <button type="button" onClick={() => onSelect(review.id)}>
            <div className="review-meta">
              <strong>{review.customer_name}</strong>
              <span className="stars">{review.rating}/5</span>
            </div>
            <p>{review.comment}</p>
          </button>
        </li>
      ))}
    </ul>
  );
}
