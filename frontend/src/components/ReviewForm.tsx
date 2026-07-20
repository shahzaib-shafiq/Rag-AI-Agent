"use client";

import { FormEvent, useState } from "react";

type Props = {
  busy: boolean;
  onSubmit: (payload: {
    customer_name: string;
    rating: number;
    comment: string;
  }) => Promise<void>;
};

export function ReviewForm({ busy, onSubmit }: Props) {
  const [customerName, setCustomerName] = useState("");
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      customer_name: customerName.trim() || "Anonymous",
      rating,
      comment: comment.trim(),
    });
    setComment("");
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <div className="composer-grid">
        <label className="field">
          <span>Name</span>
          <input
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            placeholder="Customer name"
            maxLength={120}
          />
        </label>
        <label className="field">
          <span>Rating</span>
          <div className="rating-row" role="group" aria-label="Rating">
            {[1, 2, 3, 4, 5].map((value) => (
              <button
                key={value}
                type="button"
                className={value <= rating ? "rating-btn active" : "rating-btn"}
                onClick={() => setRating(value)}
                aria-pressed={value <= rating}
              >
                {value}
              </button>
            ))}
          </div>
        </label>
      </div>

      <label className="field">
        <span>Review</span>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Paste or write a customer review…"
          rows={4}
          required
        />
      </label>

      <button className="btn primary" type="submit" disabled={busy || !comment.trim()}>
        {busy ? "Analyzing…" : "Analyze & save"}
      </button>
    </form>
  );
}
