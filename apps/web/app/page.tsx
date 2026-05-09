import { LinkButton } from "@/components/ui";
import { apiUrl } from "./lib/api";

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="border-b border-slate-200 pb-6">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Production RAG Workspace
          </p>
          <h1 className="mt-3 text-4xl font-semibold text-slate-950">
            Production RAG Assistant
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
            Upload documents, process them through asynchronous ingestion, search embedded chunks,
            and ask grounded questions with citations.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <LinkButton href="/chat">Open Chat</LinkButton>
            <LinkButton href="/upload">Upload Document</LinkButton>
            <LinkButton href="/documents" variant="secondary">
              View Documents
            </LinkButton>
            <LinkButton href="/retrieval" variant="secondary">
              Retrieval Debug
            </LinkButton>
          </div>
        </header>

        <div className="grid gap-4 md:grid-cols-4">
          {[
            ["API", apiUrl, "Health, upload, retrieval, chat"],
            ["Worker", "Celery + Redis", "Async extraction, chunking, embedding"],
            ["PostgreSQL", "postgres:5432", "Documents, chunks, chat history"],
            ["Qdrant", "qdrant:6333", "Vector search collection"],
            ["Redis", "redis:6379", "Queue broker and results"],
            ["Ollama", "ollama:11434", "Local embeddings and chat"],
            ["Embeddings", "nomic-embed-text", "768 dimensional vectors"],
            ["Chat", "qwen2.5:0.5b", "OpenAI-compatible provider"],
          ].map(([label, value, description]) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <p className="mt-2 break-words font-mono text-sm text-slate-900">{value}</p>
              <p className="mt-2 text-xs leading-5 text-slate-500">{description}</p>
            </div>
          ))}
        </div>

        <a className="w-fit text-sm font-medium text-slate-950 underline" href={`${apiUrl}/health`}>
          Open API Health
        </a>
      </section>
    </main>
  );
}
