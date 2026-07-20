export type Review = {
  id: number;
  customer_name: string;
  rating: number;
  comment: string;
  created_at: string;
  updated_at: string;
};

export type ReviewAnalysis = {
  review_id: number;
  review: string;
  rating: number;
  customer_name: string;
  model: string;
  sentiment: string;
  summary: string;
  key_issues: string[];
  suggestions: string[];
};

export type BulkAnalysis = {
  total_reviews: number;
  average_rating: number;
  rating_breakdown: Record<string, number>;
  model: string;
  overall_sentiment: string;
  summary: string;
  common_themes: string[];
  key_issues: string[];
  suggestions: string[];
};

export type CreateReviewInput = {
  customer_name: string;
  rating: number;
  comment: string;
};
