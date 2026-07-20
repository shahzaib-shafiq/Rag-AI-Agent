"use client";

import type { BulkAnalysis, ReviewAnalysis } from "@/lib/types";

type Props = {
  single: ReviewAnalysis | null;
  bulk: BulkAnalysis | null;
  loadingBulk: boolean;
  onAnalyzeAll: () => void;
};

function SentimentBadge({ value }: { value: string }) {
  return <span className={`sentiment sentiment-${value.toLowerCase()}`}>{value}</span>;
}

export function AnalysisPanel({
  single,
  bulk,
  loadingBulk,
  onAnalyzeAll,
}: Props) {
  return (
    <aside className="insight-panel">
      <div className="panel-head">
        <h2>Insights</h2>
        <button
          className="btn secondary"
          type="button"
          onClick={onAnalyzeAll}
          disabled={loadingBulk}
        >
          {loadingBulk ? "Reading all reviews…" : "Analyze all reviews"}
        </button>
      </div>

      {bulk ? (
        <section className="insight-block appear">
          <div className="insight-top">
            <h3>All feedback</h3>
            <SentimentBadge value={bulk.overall_sentiment} />
          </div>
          <p className="muted">
            {bulk.total_reviews} reviews · avg {bulk.average_rating.toFixed(2)}/5
          </p>
          <p>{bulk.summary}</p>

          <div className="bars">
            {Object.entries(bulk.rating_breakdown).map(([stars, count]) => (
              <div key={stars} className="bar-row">
                <span>{stars}★</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${
                        bulk.total_reviews
                          ? (count / bulk.total_reviews) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
                <span>{count}</span>
              </div>
            ))}
          </div>

          {!!bulk.common_themes.length && (
            <>
              <h4>Themes</h4>
              <ul className="bullet-list">
                {bulk.common_themes.map((theme) => (
                  <li key={theme}>{theme}</li>
                ))}
              </ul>
            </>
          )}

          {!!bulk.key_issues.length && (
            <>
              <h4>Issues</h4>
              <ul className="bullet-list">
                {bulk.key_issues.map((issue) => (
                  <li key={issue}>{issue}</li>
                ))}
              </ul>
            </>
          )}

          <h4>Suggestions</h4>
          <ul className="bullet-list emphasis">
            {bulk.suggestions.map((suggestion) => (
              <li key={suggestion}>{suggestion}</li>
            ))}
          </ul>
        </section>
      ) : (
        <p className="empty soft">
          Run a full pass to surface themes and prioritized improvements across
          every stored review.
        </p>
      )}

      {single && (
        <section className="insight-block appear">
          <div className="insight-top">
            <h3>Latest review</h3>
            <SentimentBadge value={single.sentiment} />
          </div>
          <p className="muted">
            Saved as #{single.review_id} · {single.customer_name} · {single.rating}/5
          </p>
          <p>{single.summary}</p>

          {!!single.key_issues.length && (
            <>
              <h4>Issues</h4>
              <ul className="bullet-list">
                {single.key_issues.map((issue) => (
                  <li key={issue}>{issue}</li>
                ))}
              </ul>
            </>
          )}

          <h4>Suggestions</h4>
          <ul className="bullet-list emphasis">
            {single.suggestions.map((suggestion) => (
              <li key={suggestion}>{suggestion}</li>
            ))}
          </ul>
        </section>
      )}
    </aside>
  );
}
