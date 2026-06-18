"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ConnectorItem = {
  type?: string;
  status?: string;
};

type AuditEvent = {
  action?: string;
  timestamp?: string;
};

function dayBucket(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "unknown";
  return date.toISOString().slice(0, 10);
}

export function DashboardCharts({ connectors, events }: { connectors: ConnectorItem[]; events: AuditEvent[] }) {
  const statusCounts = connectors.reduce<Record<string, number>>((acc, connector) => {
    const key = String(connector.status || "unknown");
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  const connectorData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }));

  const trend = events.reduce<Record<string, { date: string; audit: number; ingestion: number; query: number }>>(
    (acc, event) => {
      const date = dayBucket(String(event.timestamp || ""));
      if (!acc[date]) {
        acc[date] = { date, audit: 0, ingestion: 0, query: 0 };
      }
      const action = String(event.action || "").toLowerCase();
      acc[date].audit += 1;
      if (action.includes("ingest") || action.includes("upload") || action.includes("index")) {
        acc[date].ingestion += 1;
      }
      if (action.includes("query") || action.includes("ask") || action.includes("search")) {
        acc[date].query += 1;
      }
      return acc;
    },
    {},
  );

  const trendData = Object.values(trend)
    .filter((item) => item.date !== "unknown")
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-10);

  const totalAudit = trendData.reduce((sum, row) => sum + row.audit, 0);
  const totalIngestion = trendData.reduce((sum, row) => sum + row.ingestion, 0);
  const totalQuery = trendData.reduce((sum, row) => sum + row.query, 0);

  return (
    <>
      <section className="grid" style={{ marginTop: 14 }}>
        <article className="card card-soft">
          <h3>Audit Events (10d)</h3>
          <div className="metric-value">{totalAudit}</div>
        </article>
        <article className="card card-soft">
          <h3>Ingestion Events (10d)</h3>
          <div className="metric-value">{totalIngestion}</div>
        </article>
        <article className="card card-soft">
          <h3>Query Events (10d)</h3>
          <div className="metric-value">{totalQuery}</div>
        </article>
      </section>

      <section className="split" style={{ marginTop: 14 }}>
        <article className="card">
          <h3>Connector Status Distribution</h3>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={connectorData.length ? connectorData : [{ name: "none", value: 1 }]}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={92}
                  innerRadius={44}
                  fill="#2fd4b4"
                />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </article>
        <article className="card">
          <h3>Operational Trends</h3>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trendData.length ? trendData : [{ date: "n/a", audit: 0, ingestion: 0, query: 0 }]}> 
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(154, 194, 211, 0.24)" />
                <XAxis dataKey="date" stroke="#96b0bf" tickLine={false} axisLine={false} />
                <YAxis stroke="#96b0bf" tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line dataKey="audit" stroke="#2fd4b4" strokeWidth={2} dot={false} />
                <Line dataKey="ingestion" stroke="#f9b44c" strokeWidth={2} dot={false} />
                <Line dataKey="query" stroke="#8aa4ff" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="card" style={{ marginTop: 14 }}>
        <h3>Audit Event Activity</h3>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={trendData.length ? trendData : [{ date: "n/a", audit: 0, ingestion: 0, query: 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(154, 194, 211, 0.24)" />
              <XAxis dataKey="date" stroke="#96b0bf" tickLine={false} axisLine={false} />
              <YAxis stroke="#96b0bf" tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="audit" fill="#f9b44c" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </>
  );
}

