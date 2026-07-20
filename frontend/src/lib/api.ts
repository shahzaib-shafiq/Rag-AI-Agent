import type {
  BulkAnalysis,
  CreateReviewInput,
  Review,
  ReviewAnalysis,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function getReviews(): Promise<Review[]> {
  return request<Review[]>("/reviews/");
}

export function analyzeAndSaveReview(
  payload: CreateReviewInput
): Promise<ReviewAnalysis> {
  return request<ReviewAnalysis>("/analyze/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function analyzeAllReviews(): Promise<BulkAnalysis> {
  return request<BulkAnalysis>("/analyze/all");
}
