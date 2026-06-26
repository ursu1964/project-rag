import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>ProjectRAG Control Plane</h1>
      <p>Select a workspace area:</p>
      <ul>
        <li><Link href="/ask">Ask</Link></li>
        <li><Link href="/documents">Documents</Link></li>
        <li><Link href="/admin">Admin</Link></li>
        <li><Link href="/audit">Audit</Link></li>
        <li><Link href="/topology">Topology</Link></li>
        <li><Link href="/evaluation">Evaluation</Link></li>
      </ul>
    </main>
  );
}
