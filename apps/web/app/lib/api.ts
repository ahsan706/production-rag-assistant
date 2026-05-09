export const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type DocumentRecord = {
  id: string;
  original_filename: string;
  stored_filename: string;
  content_type: string;
  file_extension: string;
  size_bytes: number;
  checksum_sha256: string;
  status: string;
  error_message: string | null;
  extracted_text_path: string | null;
  document_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type UploadResponse = {
  document: DocumentRecord;
  duplicate: boolean;
};

export type RetrievedChunk = {
  chunk_id: string;
  document_id: string;
  filename: string;
  chunk_index: number;
  page_number: number | null;
  score: number;
  text: string;
};

export type Citation = {
  label: number;
  chunk_id: string;
  document_id: string;
  filename: string;
  chunk_index: number;
  page_number: number | null;
  score: number;
  excerpt: string;
};

export type ChatMessage = {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  error_message: string | null;
  citations: Citation[];
  retrieved_context: RetrievedChunk[];
  message_metadata: Record<string, unknown>;
  created_at: string;
};

export type ChatSession = {
  id: string;
  title: string | null;
  status: string;
  error_message: string | null;
  session_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
};

export type ChatTurnResponse = {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
};

export type RetrievalDebugResponse = {
  query: string;
  top_k: number;
  results: RetrievedChunk[];
};

export function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function formatScore(score: number) {
  return score.toFixed(3);
}
