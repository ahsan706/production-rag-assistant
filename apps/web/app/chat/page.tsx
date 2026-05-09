"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Button, LinkButton, PageHeader, StatusBadge } from "@/components/ui";
import {
  apiUrl,
  formatScore,
  type ChatMessage,
  type ChatSession,
  type ChatTurnResponse,
} from "../lib/api";

export default function ChatPage() {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [content, setContent] = useState("");
  const [topK, setTopK] = useState(5);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function createSession() {
      try {
        const response = await fetch(`${apiUrl}/chat/sessions`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ title: "RAG chat" }),
        });
        if (!response.ok) throw new Error("Unable to create chat session.");
        const nextSession = (await response.json()) as ChatSession;
        setSession(nextSession);
        setMessages(nextSession.messages);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to create chat session.");
      }
    }

    void createSession();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || !content.trim()) return;

    setIsSending(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/chat/sessions/${session.id}/messages`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ content: content.trim(), top_k: topK }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Chat request failed.");
      const turn = payload as ChatTurnResponse;
      setMessages((current) => [...current, turn.user_message, turn.assistant_message]);
      setContent("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6">
      <section className="mx-auto max-w-6xl">
        <PageHeader eyebrow="Grounded Chat" title="Ask Your Documents">
          <LinkButton href="/documents" variant="secondary">
            Documents
          </LinkButton>
          <LinkButton href="/retrieval" variant="secondary">
            Retrieval Debug
          </LinkButton>
          <LinkButton href="/" variant="ghost">
            Dashboard
          </LinkButton>
        </PageHeader>

        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
          <section className="flex min-h-[620px] flex-col overflow-hidden rounded-lg border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div>
                <p className="text-sm font-medium text-slate-950">Session</p>
                <p className="mt-1 font-mono text-xs text-slate-500">{session?.id ?? "Creating..."}</p>
              </div>
              <StatusBadge status={session?.status ?? "starting"} />
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto p-4">
              {messages.length === 0 ? (
                <div className="rounded-md border border-dashed border-slate-300 p-5 text-sm leading-6 text-slate-600">
                  Ask a question after at least one document is embedded. Unsupported questions will be refused
                  instead of answered from model memory.
                </div>
              ) : null}

              {messages.map((message) => (
                <article
                  className={`rounded-lg border p-4 ${
                    message.role === "assistant"
                      ? "border-slate-200 bg-slate-50"
                      : "ml-auto max-w-[86%] border-slate-900 bg-slate-950 text-white"
                  }`}
                  key={message.id}
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-xs font-medium uppercase">{message.role}</p>
                    {message.role === "assistant" ? <StatusBadge status={message.status} /> : null}
                  </div>
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-6">{message.content}</p>

                  {message.role === "assistant" && message.citations.length > 0 ? (
                    <div className="mt-4 border-t border-slate-200 pt-3">
                      <p className="text-xs font-medium uppercase text-slate-500">Citations</p>
                      <div className="mt-2 grid gap-2">
                        {message.citations.map((citation) => (
                          <div className="rounded-md border border-slate-200 bg-white p-3" key={citation.label}>
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="font-mono text-xs font-semibold text-slate-950">
                                [{citation.label}]
                              </span>
                              <span className="text-sm font-medium text-slate-900">{citation.filename}</span>
                              <span className="text-xs text-slate-500">
                                chunk {citation.chunk_index}
                                {citation.page_number ? ` · page ${citation.page_number}` : ""}
                              </span>
                              <span className="ml-auto font-mono text-xs text-slate-500">
                                {formatScore(citation.score)}
                              </span>
                            </div>
                            <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">
                              {citation.excerpt}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  {message.role === "assistant" && message.retrieved_context.length > 0 ? (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-xs font-medium text-slate-500">
                        Retrieved chunks
                      </summary>
                      <div className="mt-2 space-y-2">
                        {message.retrieved_context.map((chunk) => (
                          <div className="rounded-md border border-slate-200 bg-white p-3" key={chunk.chunk_id}>
                            <div className="flex justify-between gap-3 text-xs text-slate-500">
                              <span>{chunk.filename}</span>
                              <span className="font-mono">{formatScore(chunk.score)}</span>
                            </div>
                            <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">{chunk.text}</p>
                          </div>
                        ))}
                      </div>
                    </details>
                  ) : null}
                </article>
              ))}
              <div ref={bottomRef} />
            </div>

            <form className="border-t border-slate-200 p-4" onSubmit={onSubmit}>
              {error ? <p className="mb-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
              <textarea
                className="min-h-24 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950 outline-none focus:border-slate-500"
                onChange={(event) => setContent(event.target.value)}
                placeholder="Ask a grounded question..."
                value={content}
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
                <Button disabled={!session || !content.trim() || isSending} type="submit">
                  {isSending ? "Generating..." : "Send"}
                </Button>
              </div>
            </form>
          </section>

          <aside className="rounded-lg border border-slate-200 bg-white p-4">
            <p className="text-sm font-semibold text-slate-950">Grounding Contract</p>
            <div className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
              <p>Answers are generated only after vector retrieval.</p>
              <p>Assistant responses include backend citation metadata when context supports the answer.</p>
              <p>Weak retrieval is refused and preserved with retrieved debug context.</p>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
