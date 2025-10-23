export interface KnowledgeBaseEntry {
  id: string;
  question: string;
  answer: string;
  tags: string[];
  category?: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  last_modified_by: string;
}

export interface QuestionResult {
  question: string;
  answer: string;
  confidence: number;
  source_id?: string;
  source_question?: string;
}

export interface ProcessingResult {
  questions_processed: number;
  answers_found: number;
  results: QuestionResult[];
  processing_time?: number;
}

export interface SearchResult {
  id: string;
  question: string;
  answer: string;
  confidence: number;
  tags: string[];
  category?: string;
}

export interface SearchResponse {
  query: string;
  matches: SearchResult[];
  total_matches: number;
}

export interface KnowledgeBaseStats {
  total_entries: number;
  categories: Record<string, number>;
  top_tags: Record<string, number>;
}

export interface QuestionSubmission {
  id: string;
  input_type: 'text' | 'pdf';
  raw_input: string;
  questions_count: number;
  answers_found: number;
  created_at: string;
  status: string;
}
