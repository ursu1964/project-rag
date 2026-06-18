import { AppShell } from '@/components/AppShell';

export default function EvaluationPage() {
	return (
		<AppShell>
			<section className="page-head">
				<div>
					<h1>Evaluation Dashboard</h1>
					<p>Monitor regression readiness for graph, vector, hybrid, and safety-focused golden question sets.</p>
				</div>
				<span className="badge warn">Manual trigger</span>
			</section>
			<section className="grid">
				<article className="card">
					<h2>Golden Suites</h2>
					<div className="list">
						<div className="list-item"><h3>Graph</h3><p>Dependency accuracy and deterministic routing checks.</p></div>
						<div className="list-item"><h3>Vector</h3><p>Chunk relevance and semantic recall consistency.</p></div>
						<div className="list-item"><h3>Hybrid</h3><p>Evidence assembly quality across retrievers.</p></div>
						<div className="list-item"><h3>Safety</h3><p>Prompt policy and sensitive-data protection coverage.</p></div>
					</div>
				</article>
				<article className="card card-soft">
					<h2>Quality Gate Policy</h2>
					<table className="kv">
						<tbody>
							<tr><th>Regression Strategy</th><td>Fail-fast on citation and grounding drops</td></tr>
							<tr><th>Confidence Signal</th><td>Evidence-backed with validation stage</td></tr>
							<tr><th>Release Rule</th><td>No deployment without passing gates</td></tr>
						</tbody>
					</table>
				</article>
			</section>
		</AppShell>
	);
}
