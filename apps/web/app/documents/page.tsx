"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { LinkButton, StatusBadge } from "@/components/ui";
import { apiUrl, formatBytes, type DocumentRecord } from "../lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDocuments() {
      try {
        const response = await fetch(`${apiUrl}/documents`);
        if (!response.ok) throw new Error("Unable to load documents.");
        setDocuments((await response.json()) as DocumentRecord[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load documents.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadDocuments();
  }, []);

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Documents</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">Library</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <LinkButton href="/chat" variant="secondary">
              Chat
            </LinkButton>
            <LinkButton href="/retrieval" variant="secondary">
              Retrieval
            </LinkButton>
            <LinkButton href="/upload">Upload</LinkButton>
          </div>
        </div>

        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          {isLoading ? <p className="p-5 text-sm text-slate-500">Loading documents...</p> : null}
          {error ? <p className="p-5 text-sm text-red-700">{error}</p> : null}
          {!isLoading && !error && documents.length === 0 ? (
            <div className="p-5">
              <p className="text-sm text-slate-600">No documents uploaded yet.</p>
              <LinkButton className="mt-4" href="/upload">
                Upload First Document
              </LinkButton>
            </div>
          ) : null}
          {documents.length > 0 ? (
            <div className="divide-y divide-slate-200">
              {documents.map((document) => (
                <Link
                  className="grid gap-3 p-4 transition hover:bg-slate-50 md:grid-cols-[1fr_120px_130px]"
                  href={`/documents/${document.id}`}
                  key={document.id}
                >
                  <div>
                    <p className="font-medium text-slate-950">{document.original_filename}</p>
                    <p className="mt-1 font-mono text-xs text-slate-500">
                      {document.checksum_sha256.slice(0, 16)}
                    </p>
                  </div>
                  <p className="text-sm text-slate-600">{formatBytes(document.size_bytes)}</p>
                  <StatusBadge status={document.status} />
                </Link>
              ))}
            </div>
          ) : null}
        </div>
      </section>
    </main>
  );
}
