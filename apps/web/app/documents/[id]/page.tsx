"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { LinkButton, StatusBadge } from "@/components/ui";
import { apiUrl, formatBytes, type DocumentRecord } from "../../lib/api";

export default function DocumentDetailsPage() {
  const params = useParams<{ id: string }>();
  const [document, setDocument] = useState<DocumentRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDocument() {
      try {
        const response = await fetch(`${apiUrl}/documents/${params.id}`);
        if (!response.ok) throw new Error("Unable to load document.");
        setDocument((await response.json()) as DocumentRecord);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load document.");
      }
    }

    void loadDocument();
  }, [params.id]);

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Document</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">
              {document?.original_filename ?? "Details"}
            </h1>
          </div>
          <LinkButton href="/documents" variant="secondary">
            Back
          </LinkButton>
        </div>

        {error ? <p className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</p> : null}
        {!document && !error ? <p className="text-sm text-slate-500">Loading document...</p> : null}
        {document ? (
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="flex flex-wrap items-center gap-3">
              <StatusBadge status={document.status} />
              <span className="text-sm text-slate-500">{formatBytes(document.size_bytes)}</span>
              <span className="text-sm text-slate-500">{document.content_type}</span>
            </div>
            <dl className="mt-6 grid gap-4 md:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-slate-500">Stored filename</dt>
                <dd className="mt-1 font-mono text-sm text-slate-900">{document.stored_filename}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">SHA-256</dt>
                <dd className="mt-1 break-all font-mono text-sm text-slate-900">
                  {document.checksum_sha256}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Extracted text</dt>
                <dd className="mt-1 break-all font-mono text-sm text-slate-900">
                  {document.extracted_text_path ?? "Not available"}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Chunking</dt>
                <dd className="mt-1 break-all font-mono text-sm text-slate-900">
                  {JSON.stringify(document.document_metadata.chunking ?? "Not available")}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Created</dt>
                <dd className="mt-1 text-sm text-slate-900">
                  {new Date(document.created_at).toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Updated</dt>
                <dd className="mt-1 text-sm text-slate-900">
                  {new Date(document.updated_at).toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>
        ) : null}
      </section>
    </main>
  );
}
