export interface Document {
  document_id: string;
  title: string;
  file_path: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  text_chunks: number;
  image_chunks: number;
  table_chunks: number;
  total_chunks: number;
  created_at: string;
  updated_at: string;
}

export interface Chunk {
  chunk_id: string;
  document_id: string;
  content: string;
  chunk_type: string;
  token_count: number;
  page_num?: number;
}

export interface Citation {
  index: number;
  source: string;
  page?: number | null;
  content_preview: string;
  confidence?: number;
  document_id?: string;
}

export interface QueryResponse {
  response: string;
  citations: Citation[];
  num_sources: number;
  metadata?: {
    retrieved_chunks: number;
    reranked_chunks: number;
    query_length: number;
  };
}

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

export interface ProcessingUpdate {
  type: string;
  document_id: string;
  progress: number;
  status: string;
  current_step: string;
  details?: Record<string, unknown>;
}

export interface WebSocketMessage {
  type: string;
  [key: string]: unknown;
}
