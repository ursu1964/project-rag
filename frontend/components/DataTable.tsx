type DataTableColumn = {
  key: string;
  label: string;
  type?: "text" | "date" | "number" | "boolean" | string;
  sortable?: boolean;
};

type DataTableProps<T extends Record<string, unknown>> = {
  title?: string;
  rows?: T[];
  columns?: DataTableColumn[];
  defaultSortKey?: string;
  defaultSortDirection?: "asc" | "desc" | string;
  emptyMessage?: string;
};

function formatValue(value: unknown, type?: string): string {
  if (value === null || value === undefined) return "";

  if (type === "date") {
    const date = new Date(String(value));
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
  }

  if (type === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export function DataTable<T extends Record<string, unknown>>({
  title,
  rows = [],
  columns,
  emptyMessage = "No data available.",
}: DataTableProps<T>) {
  const resolvedColumns: DataTableColumn[] =
    columns && columns.length > 0
      ? columns
      : rows.length > 0
        ? Object.keys(rows[0]).map(
            (key): DataTableColumn => ({
              key,
              label: key,
              type: "text",
              sortable: false,
            }),
          )
        : [];

  return (
    <section>
      {title ? <h2>{title}</h2> : null}

      {rows.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {resolvedColumns.map((column) => (
                <th key={column.key} style={{ border: "1px solid #ddd", padding: 8 }}>
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {resolvedColumns.map((column) => (
                  <td key={column.key} style={{ border: "1px solid #ddd", padding: 8 }}>
                    {formatValue(row[column.key], column.type)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
