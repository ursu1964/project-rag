import Link from "next/link";

const appDashboards = [
  { title: "Admin", href: "/admin", description: "System administration and platform configuration." },
  { title: "Ask", href: "/ask", description: "Ask infrastructure and RAG questions." },
  { title: "Documents", href: "/documents", description: "Upload, inspect, and reindex documents." },
  { title: "Audit", href: "/audit", description: "Review system events and operational history." },
  { title: "Topology", href: "/topology", description: "View infrastructure and knowledge topology." },
  { title: "Evaluation", href: "/evaluation", description: "Review quality and evaluation results." },
];

const externalTools = [
  { title: "API Docs", href: "http://localhost:18000/docs" },
  { title: "Grafana", href: "http://localhost:3001" },
  { title: "Prometheus", href: "http://localhost:9091" },
  { title: "GraphDB", href: "http://localhost:7200" },
  { title: "Qdrant", href: "http://localhost:6333/dashboard" },
  { title: "Alertmanager", href: "http://localhost:19094" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto max-w-7xl">
        <div className="mb-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-xl">
          <p className="mb-2 text-sm uppercase tracking-[0.3em] text-cyan-400">ProjectRAG Control Plane</p>
          <h1 className="mb-4 text-4xl font-semibold">AI Infrastructure Dashboard</h1>
          <p className="max-w-3xl text-slate-300">
            Central launcher for the ProjectRAG application, RAG workflows, infrastructure services,
            monitoring tools, and operational dashboards.
          </p>
        </div>

        <h2 className="mb-4 text-2xl font-semibold">Application Dashboards</h2>
        <div className="mb-10 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {appDashboards.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-cyan-400 hover:bg-slate-800"
            >
              <h3 className="mb-2 text-xl font-semibold text-cyan-300">{item.title}</h3>
              <p className="text-sm text-slate-300">{item.description}</p>
            </Link>
          ))}
        </div>

        <h2 className="mb-4 text-2xl font-semibold">Infrastructure Tools</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {externalTools.map((item) => (
            <a
              key={item.href}
              href={item.href}
              target="_blank"
              rel="noreferrer"
              className="rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-emerald-400 hover:bg-slate-800"
            >
              <h3 className="text-xl font-semibold text-emerald-300">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-400">{item.href}</p>
            </a>
          ))}
        </div>
      </section>
    </main>
  );
}
