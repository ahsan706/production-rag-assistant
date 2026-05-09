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

export function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
