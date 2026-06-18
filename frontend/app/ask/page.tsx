'use client';
import { useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { apiPost } from '@/lib/api';

type QueryResult = {
  answer?: string;
  route?: string;
  validation?: Record<string, unknown>;
  citations?: unknown[];
  policy_decision?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
};

export default function AskPage() {
  const [question, setQuestion] = useState('What does VM1 depend on?');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError('');
    try {
      setResult(await apiPost<QueryResult>('/query', { question }));
    } catch {
      setError('The query failed. Confirm API availability and retry.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <h1>Ask Infrastructure</h1>
          <p>Run evidence-grounded questions and inspect routing, citations, validation, and policy outcomes.</p>
        </div>
        <span className="badge ok">Evidence Mode</span>
      </section>
      <div className="chat">
        <section className="card">
          <h2>Query</h2>
          <textarea rows={4} value={question} onChange={e => setQuestion(e.target.value)} />
          <p>
            <button onClick={submit} disabled={loading || !question.trim()}>{loading ? 'Running analysis...' : 'Ask ProjectRAG'}</button>
          </p>
          {error && <p className="badge danger">{error}</p>}
          <div className="json-box">
            <strong>Answer</strong>
            <pre>{result?.answer || 'Ask a grounded infrastructure question to generate an answer with citations.'}</pre>
          </div>
        </section>
        <aside className="card">
          <h2>Decision and Evidence</h2>
          <table className="kv">
            <tbody>
              <tr>
                <th>Route</th>
                <td>{result?.route || 'n/a'}</td>
              </tr>
              <tr>
                <th>Confidence</th>
                <td>{String((result?.validation as { confidence?: unknown } | undefined)?.confidence ?? 'n/a')}</td>
              </tr>
              <tr>
                <th>Citations</th>
                <td>{Array.isArray(result?.citations) ? result?.citations.length : 0}</td>
              </tr>
            </tbody>
          </table>
          <div className="json-box">
            <pre>
              {result
                ? JSON.stringify(
                    {
                      validation: result.validation,
                      citations: result.citations,
                      policy_decision: result.policy_decision,
                      metrics: result.metrics,
                    },
                    null,
                    2,
                  )
                : 'No evidence yet.'}
            </pre>
          </div>
        </aside>
      </div>
    </AppShell>
  );
}
