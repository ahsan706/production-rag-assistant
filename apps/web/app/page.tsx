import { LinkButton } from "@/components/ui";
import { apiUrl } from "./lib/api";

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto flex max-w-5xl flex-col gap-8">
        <header className="border-b border-slate-200 pb-6">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Phase 2 Document Upload
          </p>
          <h1 className="mt-3 text-4xl font-semibold text-slate-950">
            Production RAG Assistant
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
            Dockerized infrastructure is running, and the document upload foundation is
            ready for ingestion in the next phase.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <LinkButton href="/upload">Upload Document</LinkButton>
            <LinkButton href="/documents" variant="secondary">
              View Documents
            </LinkButton>
          </div>
        </header>

        <div className="grid gap-4 md:grid-cols-3">
          {[
            ["API", apiUrl],
            ["PostgreSQL", "postgres:5432"],
            ["Qdrant", "qdrant:6333"],
            ["Redis", "redis:6379"],
            ["Worker", "Celery + Redis"],
            ["Ollama", "ollama:11434"],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <p className="mt-2 break-words font-mono text-sm text-slate-900">{value}</p>
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
