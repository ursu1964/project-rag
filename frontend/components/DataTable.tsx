"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

function usePersistedState<T>(storageKey: string, initial: T): [T, (value: T) => void] {
  const [state, setState] = useState<T>(() => {
    if (typeof window === "undefined") return initial;
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored !== null ? (JSON.parse(stored) as T) : initial;
    } catch {
      return initial;
    }
  });
  const set = useCallback(
    (value: T) => {
      setState(value);
      try {
        window.localStorage.setItem(storageKey, JSON.stringify(value));
      } catch { /* quota exceeded — silently ignore */ }
    },
    [storageKey],
  );
  return [state, set];
}

function exportToCsv(title: string, columns: DataColumn[], rows: Record<string, unknown>[]): void {
  const escape = (value: string) => `"${value.replace(/"/g, '""')}"`;
  const header = columns.map((col) => escape(col.label)).join(",");
  const body = rows.map((row) =>
    columns.map((col) => {
      const value = row[col.key];
      if (value === null || value === undefined) return "";
      if (typeof value === "object") return escape(JSON.stringify(value));
      return escape(String(value));
    }).join(",")
  );
  const csv = [header, ...body].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${title.toLowerCase().replace(/\s+/g, "_")}_${new Date().toISOString().slice(0, 10)}.csv`;
  anchor.click();
  URL.revokeObjectURL(url);
}

type ColumnType = "text" | "number" | "date" | "json";

type DataColumn = {
  key: string;
  label: string;
  type?: ColumnType;
  sortable?: boolean;
};

type DataTableProps = {
  title: string;
  rows: Record<string, unknown>[];
  columns: DataColumn[];
  defaultSortKey?: string;
  defaultSortDirection?: "asc" | "desc";
  emptyMessage?: string;
};

function normalize(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function compareValues(a: unknown, b: unknown, type: ColumnType): number {
  if (type === "number") {
    const av = Number(a || 0);
    const bv = Number(b || 0);
    return av - bv;
  }
  if (type === "date") {
    const av = Date.parse(String(a || ""));
    const bv = Date.parse(String(b || ""));
    return av - bv;
  }
  return normalize(a).localeCompare(normalize(b));
}

function renderCell(value: unknown, type: ColumnType): string {
  if (value === null || value === undefined || value === "") return "-";
  if (type === "date") {
    const date = new Date(String(value));
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
  }
  if (type === "json") {
    return typeof value === "string" ? value : JSON.stringify(value);
  }
  return String(value);
}

export function DataTable({
  title,
  rows,
  columns,
  defaultSortKey,
  defaultSortDirection = "desc",
  emptyMessage = "No rows available.",
}: DataTableProps) {
  const storagePrefix = `datatable:${title.toLowerCase().replace(/\s+/g, "_")}`;
  const [query, setQuery] = usePersistedState(`${storagePrefix}:filter`, "");
  const [sortKey, setSortKey] = usePersistedState(`${storagePrefix}:sort_key`, defaultSortKey || columns[0]?.key || "");
  const [sortDirection, setSortDirection] = usePersistedState<"asc" | "desc">(`${storagePrefix}:sort_dir`, defaultSortDirection);
  // Sync defaultSortKey on first mount only (external prop may differ from stored value)
  useEffect(() => {
    if (!window.localStorage.getItem(`${storagePrefix}:sort_key`) && defaultSortKey) {
      setSortKey(defaultSortKey);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sorted = useMemo(() => {
    const filtered = rows.filter((row) => normalize(row).toLowerCase().includes(query.toLowerCase()));
    const column = columns.find((item) => item.key === sortKey);
    if (!column || column.sortable === false) return filtered;
    const type = column.type || "text";
    return [...filtered].sort((left, right) => {
      const cmp = compareValues(left[sortKey], right[sortKey], type);
      return sortDirection === "asc" ? cmp : -cmp;
    });
  }, [rows, query, columns, sortKey, sortDirection]);

  return (
    <section className="card" style={{ marginTop: 14 }}>
      <div className="table-toolbar">
        <h2>{title}</h2>
        <div className="table-controls">
          <input
            aria-label={`${title} filter`}
            placeholder="Filter rows"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <select
            aria-label={`${title} sort field`}
            value={sortKey}
            onChange={(event) => setSortKey(event.target.value)}
          >
            {columns.map((column) => (
              <option key={column.key} value={column.key}>
                Sort: {column.label}
              </option>
            ))}
          </select>
          <select
            aria-label={`${title} sort direction`}
            value={sortDirection}
            onChange={(event) => setSortDirection(event.target.value as "asc" | "desc")}
          >
            <option value="desc">Desc</option>
            <option value="asc">Asc</option>
          </select>
          <button
            className="button-muted"
            title="Export visible rows as CSV"
            onClick={() => exportToCsv(title, columns, sorted)}
          >
            Export CSV
          </button>
        </div>
      </div>

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, index) => (
              <tr key={`${title}-row-${index}`}>
                {columns.map((column) => (
                  <td key={`${column.key}-${index}`}>{renderCell(row[column.key], column.type || "text")}</td>
                ))}
              </tr>
            ))}
            {sorted.length === 0 && (
              <tr>
                <td colSpan={columns.length}>{emptyMessage}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
