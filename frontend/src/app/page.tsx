"use client";

import { useCallback, useEffect, useState } from "react";
import { AnalysisPanel } from "@/components/AnalysisPanel";
import { ReviewForm } from "@/components/ReviewForm";
import { ReviewList } from "@/components/ReviewList";
import {
  analyzeAllReviews,
  analyzeAndSaveReview,
  getReviews,
} from "@/lib/api";
import type { BulkAnalysis, Review, ReviewAnalysis } from "@/lib/types";

export default function HomePage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [singleAnalysis, setSingleAnalysis] = useState<ReviewAnalysis | null>(
    null
  );
  const [bulkAnalysis, setBulkAnalysis] = useState<BulkAnalysis | null>(null);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [loadingBulk, setLoadingBulk] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReviews = useCallback(async (preferId?: number) => {
    setLoadingReviews(true);
    setError(null);
    try {
      const data = await getReviews();
      setReviews(data);
      if (preferId != null) {
        setSelectedId(preferId);
      } else {
        setSelectedId((current) => current ?? data[0]?.id ?? null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load reviews");
    } finally {
      setLoadingReviews(false);
    }
  }, []);

  useEffect(() => {
    void loadReviews();
  }, [loadReviews]);

  async function handleSubmit(payload: {
    customer_name: string;
    rating: number;
    comment: string;
  }) {
    setSubmitting(true);
    setError(null);
    try {
      const analysis = await analyzeAndSaveReview(payload);
      setSingleAnalysis(analysis);
      await loadReviews(analysis.review_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analyze failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAnalyzeAll() {
    setLoadingBulk(true);
    setError(null);
    try {
      const analysis = await analyzeAllReviews();
      setBulkAnalysis(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bulk analyze failed");
    } finally {
      setLoadingBulk(false);
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <h1 className="brand">PlateWise</h1>
        <p className="tagline">
          Turn food-app reviews into clear product moves — save feedback, read
          sentiment, and get concrete improvement suggestions.
        </p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="workspace">
        <section className="panel stack">
          <div className="panel-head">
            <h2>Reviews</h2>
            <span className="muted">
              {loadingReviews ? "Loading…" : `${reviews.length} stored`}
            </span>
          </div>

          <ReviewForm busy={submitting} onSubmit={handleSubmit} />
          <ReviewList
            reviews={reviews}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </section>

        <AnalysisPanel
          single={singleAnalysis}
          bulk={bulkAnalysis}
          loadingBulk={loadingBulk}
          onAnalyzeAll={handleAnalyzeAll}
        />
      </div>
    </main>
  );
}
