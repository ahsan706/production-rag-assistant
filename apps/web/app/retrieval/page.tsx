"use client";

import { FormEvent, useState } from "react";
import { Button, LinkButton, PageHeader } from "@/components/ui";
import { apiUrl, formatScore, type RetrievalDebugResponse } from "../lib/api";

export default function RetrievalDebugPage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<RetrievalDebugResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/retrieval/debug`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ query: query.trim(), top_k: topK }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Retrieval request failed.");
      setResult(payload as RetrievalDebugResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Retrieval request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6">
      <section className="mx-auto max-w-6xl">
        <PageHeader eyebrow="Retrieval Debug" title="Inspect Semantic Search">
          <LinkButton href="/chat" variant="secondary">
            Chat
          </LinkButton>
          <LinkButton href="/documents" variant="secondary">
            Documents
          </LinkButton>
          <LinkButton href="/" variant="ghost">
            Dashboard
          </LinkButton>
        </PageHeader>

        <form className="rounded-lg border border-slate-200 bg-white p-4" onSubmit={onSubmit}>
          <label className="block text-sm font-medium text-slate-700" htmlFor="query">
            Query
          </label>
          <textarea
            className="mt-2 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950 outline-none focus:border-slate-500"
            id="query"
            onChange={(event) => setQuery(event.target.value)}
            value={query}
          />
          <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <label className="flex items-center gap-2 text-sm text-slate-600">
              Top K
              <input
                className="h-9 w-20 rounded-md border border-slate-300 px-2 text-sm text-slate-950"
                max={20}
                min={1}
                onChange={(event) => setTopK(Number(event.target.value))}
                type="number"
                value={topK}
              />
            </label>
            <Button disabled={!query.trim() || isLoading} type="submit">
              {isLoading ? "Searching..." : "Search"}
            </Button>
          </div>
        </form>

        {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

        {result ? (
          <div className="mt-5 overflow-hidden rounded-lg border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-4 py-3">
              <p className="text-sm font-medium text-slate-950">Results for "{result.query}"</p>
              <p className="mt-1 text-xs text-slate-500">Requested top {result.top_k}</p>
            </div>
            {result.results.length === 0 ? (
              <p className="p-4 text-sm text-slate-600">No vector results returned.</p>
            ) : (
              <div className="divide-y divide-slate-200">
                {result.results.map((chunk, index) => (
                  <article className="grid gap-3 p-4 lg:grid-cols-[88px_minmax(0,1fr)]" key={chunk.chunk_id}>
                    <div>
                      <p className="font-mono text-sm font-semibold text-slate-950">#{index + 1}</p>
                      <p className="mt-1 font-mono text-sm text-slate-600">{formatScore(chunk.score)}</p>
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-medium text-slate-950">{chunk.filename}</p>
                        <span className="text-xs text-slate-500">chunk {chunk.chunk_index}</span>
                        {chunk.page_number ? <span className="text-xs text-slate-500">page {chunk.page_number}</span> : null}
                      </div>
                      <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{chunk.text}</p>
                      <p className="mt-3 break-all font-mono text-xs text-slate-400">{chunk.chunk_id}</p>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        ) : null}
      </section>
    </main>
  );
}
