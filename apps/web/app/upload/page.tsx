"use client";

import { FormEvent, useState } from "react";
import { Button, LinkButton } from "@/components/ui";
import { apiUrl, type UploadResponse } from "../lib/api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setMessage(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiUrl}/documents/upload`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "Upload failed.");
      }

      const result = payload as UploadResponse;
      setMessage(
        result.duplicate
          ? "This document already exists. Showing the existing record."
          : "Document uploaded successfully.",
      );
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto max-w-3xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Documents</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">Upload</h1>
          </div>
          <LinkButton href="/documents" variant="secondary">
            Document List
          </LinkButton>
        </div>

        <form className="rounded-lg border border-slate-200 bg-white p-5" onSubmit={onSubmit}>
          <label className="block text-sm font-medium text-slate-700" htmlFor="file">
            Document file
          </label>
          <input
            id="file"
            className="mt-2 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 file:mr-4 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-800"
            type="file"
            accept=".pdf,.txt,.md,.markdown,application/pdf,text/plain,text/markdown"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <p className="mt-2 text-sm text-slate-500">PDF, TXT, and Markdown up to 10 MB.</p>

          <div className="mt-5 flex items-center gap-3">
            <Button disabled={!file || isUploading} type="submit">
              {isUploading ? "Uploading..." : "Upload"}
            </Button>
            <LinkButton href="/" variant="secondary">
              Dashboard
            </LinkButton>
          </div>
        </form>

        {message ? (
          <div className="mt-4 rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            {message}
          </div>
        ) : null}
        {error ? (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        ) : null}
      </section>
    </main>
  );
}
