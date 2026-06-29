"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';
import { AuthRole } from '@/lib/api';

const nav: Array<[string, string, AuthRole[]?]> = [
  ['Dashboards', '/dashboards'],
  ['Ask AI', '/ask', ['admin', 'operator', 'analyst', 'agent']],
  ['Topology', '/topology', ['admin', 'operator', 'analyst', 'viewer', 'agent']],
  ['Documents', '/documents', ['admin', 'operator', 'analyst', 'viewer', 'agent']],
  ['Models', '/models', ['admin', 'operator', 'analyst', 'viewer', 'agent']],
  ['Memory', '/memory', ['admin', 'operator', 'analyst', 'viewer', 'agent']],
  ['Workflows', '/workflows', ['admin', 'operator', 'analyst', 'viewer', 'agent']],
  ['Audit', '/audit', ['admin']],
  ['Evaluation', '/evaluation', ['admin', 'operator', 'analyst']],
  ['Admin', '/admin', ['admin']],
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const auth = useAuth();
  const tenantEditable = auth.role === 'admin';
  const useLocalAdmin = () => auth.updateAuth({ apiKey: 'local-dev-key', user: 'local-dev', role: 'admin', tenantId: 'local' });

  return (
    <div className="shell">
      <aside className="nav">
        <div className="brand">
          <h1>ProjectRAG</h1>
          <p>Evidence-first infrastructure intelligence</p>
        </div>
        <div className="status-strip">
          <span className="badge ok">Control Plane</span>
          <span className="badge warn">Cloud Dormant</span>
        </div>
        <section className="auth-panel" aria-label="Authentication context">
          <label>
            API key
            <input
              type="password"
              value={auth.apiKey ?? ''}
              placeholder="local-dev-key"
              onChange={(event) => auth.updateAuth({ apiKey: event.target.value })}
            />
          </label>
          <p className="auth-help">Local dev auth uses API key + user/role/tenant headers. This is not a production login.</p>
          <button className="button-muted" type="button" onClick={useLocalAdmin}>Use local admin</button>
          <label>
            User
            <input value={auth.user ?? ''} onChange={(event) => auth.updateAuth({ user: event.target.value })} />
          </label>
          <label>
            Role
            <select value={auth.role ?? 'viewer'} onChange={(event) => auth.updateAuth({ role: event.target.value as AuthRole })}>
              <option value="viewer">viewer</option>
              <option value="analyst">analyst</option>
              <option value="operator">operator</option>
              <option value="agent">agent</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <label>
            Tenant
            <input
              value={auth.tenantId ?? ''}
              disabled={!tenantEditable}
              title={tenantEditable ? 'Admin tenant context' : 'Only admins may edit tenant context'}
              onChange={(event) => auth.updateAuth({ tenantId: event.target.value })}
            />
          </label>
          {!tenantEditable && <p className="auth-help">Tenant context is read-only unless role is admin.</p>}
          {auth.lastAuthError && <p className="badge danger">{auth.lastAuthError.status === 401 ? 'Unauthorized' : 'Forbidden'}</p>}
          <button className="button-muted" onClick={auth.logout}>Clear auth</button>
        </section>
        <nav className="nav-links" aria-label="Primary">
          {nav.map(([label, href, roles]) => {
            const active = href === '/' ? pathname === '/' : pathname.startsWith(href);
            const allowed = auth.canAccess(roles);
            return (
              <Link key={href} href={href} className={`nav-link${active ? ' active' : ''}${allowed ? '' : ' disabled'}`}>
                {label}{allowed ? '' : ' 🔒'}
              </Link>
            );
          })}
        </nav>
        <div className="nav-footnote">
          Local-first operations with policy controls and audited workflows.
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
