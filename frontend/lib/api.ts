export type AuthRole =
  | "admin"
  | "editor"
  | "viewer"
  | "query"
  | "read"
  | "ingest"
  | "operator"
  | "analyst"
  | "agent";

export type AuthContext = {
  user?: string;
  tenantId?: string;
  token?: string;
  apiKey?: string;
  role?: AuthRole;
  roles?: AuthRole[];
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:18000";
const AUTH_STORAGE_KEY = "projectrag.auth";

let memoryAuthContext: AuthContext = {};

export function getAuthContext(): AuthContext {
  if (typeof window === "undefined") {
    return memoryAuthContext;
  }

  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return memoryAuthContext;
    return JSON.parse(raw) as AuthContext;
  } catch {
    return memoryAuthContext;
  }
}

export function setAuthContext(context: AuthContext): void {
  memoryAuthContext = context;

  if (typeof window !== "undefined") {
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(context));
  }
}

export function clearAuthContext(): void {
  memoryAuthContext = {};

  if (typeof window !== "undefined") {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
  }
}

function authHeaders(): Record<string, string> {
  const auth = getAuthContext();
  const headers: Record<string, string> = {};

  if (auth.token) {
    headers.Authorization = `Bearer ${auth.token}`;
  }

  if (auth.apiKey) {
    headers["X-API-Key"] = auth.apiKey;
  }

  if (auth.role) {
    headers["X-ProjectRAG-Role"] = auth.role;
  }

  return headers;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `API error ${response.status}: ${response.statusText}`;

    try {
      const body = await response.json();
      if (body?.detail) {
        message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // Keep default message.
    }

    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

export function authStatusMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  return "Authentication or API error";
}
