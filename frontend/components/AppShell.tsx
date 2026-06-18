"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const nav = [
  ['Dashboard', '/'],
  ['Ask AI', '/ask'],
  ['Topology', '/topology'],
  ['Documents', '/documents'],
  ['Audit', '/audit'],
  ['Evaluation', '/evaluation'],
  ['Admin', '/admin'],
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

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
        <nav className="nav-links" aria-label="Primary">
          {nav.map(([label, href]) => {
            const active = href === '/' ? pathname === '/' : pathname.startsWith(href);
            return (
              <Link key={href} href={href} className={`nav-link${active ? ' active' : ''}`}>
                {label}
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
