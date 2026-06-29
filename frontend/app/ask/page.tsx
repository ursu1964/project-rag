'use client';
import { useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { apiPost, authStatusMessage } from '@/lib/api';

type QueryResult = {
  answer?: string;
  route?: string;
  validation?: Record<string, unknown>;
  citations?: unknown[];
  provenance?: { source_documents?: string[]; workflow_id?: string };
  policy_decision?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
};

export default function AskPage() {
  const [question, setQuestion] = useState('What does VM1 depend on?');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const sources = result?.provenance?.source_documents || [];

  async function submit() {
    setLoading(true);
    setError('');
    try {
      setResult(await apiPost<QueryResult>('/api/v1/query', { question }));
    } catch (err) {
      setError(authStatusMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'agent']}>
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
          {error && <AuthErrorBanner error={new Error(error)} />}
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
              <tr>
                <th>Sources</th>
                <td>{sources.length}</td>
              </tr>
            </tbody>
          </table>
          {result && sources.length === 0 ? (
            <p className="badge warn">No source documents returned. Upload and ingest documents before relying on this answer.</p>
          ) : null}
          {sources.length > 0 ? (
            <div className="json-box">
              <strong>Source documents</strong>
              <pre>{sources.join('\n')}</pre>
            </div>
          ) : null}
          <div className="json-box">
            <pre>
              {result
                ? JSON.stringify(
                    {
                      validation: result.validation,
                      citations: result.citations,
                      provenance: result.provenance,
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
      </ProtectedPage>
    </AppShell>
  );
}
