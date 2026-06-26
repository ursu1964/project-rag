function apiBase(): string {
  if (typeof window === 'undefined') {
    return (
      process.env.PROJECTRAG_INTERNAL_API_BASE_URL ||
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      'http://localhost:8001'
    );
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
}

export type AuthRole = 'admin' | 'operator' | 'analyst' | 'viewer' | 'agent';

export type AuthContext = {
  token: string;
  user: string;
  role: AuthRole;
  tenantId: string;
};

export class ApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function authStatusMessage(error: unknown): string {
  if (!isApiError(error)) return 'The request failed. Confirm API availability and retry.';
  if (error.status === 401) return 'Authentication required. Add a valid API token or trusted identity.';
  if (error.status === 403) return 'Forbidden. Your role does not have permission for this resource.';
  return error.message;
}

function browserStorage(): Storage | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage;
}

function normalizeRole(role: string | null | undefined): AuthRole {
  const value = String(role || '').toLowerCase();
  if (['admin', 'operator', 'analyst', 'viewer', 'agent'].includes(value)) return value as AuthRole;
  return 'viewer';
}

export function getAuthContext(): AuthContext {
  const storage = browserStorage();
  return {
    token: process.env.NEXT_PUBLIC_API_TOKEN || storage?.getItem('projectrag_api_token') || '',
    user: storage?.getItem('projectrag_user') || '',
    role: normalizeRole(storage?.getItem('projectrag_role') || 'viewer'),
    tenantId: storage?.getItem('projectrag_tenant_id') || 'local',
  };
}

export function setAuthContext(next: Partial<AuthContext>): void {
  const storage = browserStorage();
  if (!storage) return;
  if (next.token !== undefined) storage.setItem('projectrag_api_token', next.token);
  if (next.user !== undefined) storage.setItem('projectrag_user', next.user);
  if (next.role !== undefined) storage.setItem('projectrag_role', next.role);
  if (next.tenantId !== undefined) storage.setItem('projectrag_tenant_id', next.tenantId);
  window.dispatchEvent(new Event('projectrag-auth-changed'));
}

export function clearApiToken(): void {
  const storage = browserStorage();
  if (!storage) return;
  storage.removeItem('projectrag_api_token');
  window.dispatchEvent(new Event('projectrag-auth-changed'));
}

export function clearAuthContext(): void {
  const storage = browserStorage();
  if (!storage) return;
  storage.removeItem('projectrag_api_token');
  storage.removeItem('projectrag_user');
  storage.removeItem('projectrag_role');
  storage.removeItem('projectrag_tenant_id');
  window.dispatchEvent(new Event('projectrag-auth-changed'));
}

/** Backward-compatible token setter used by existing callers. */
export function setApiToken(token: string): void {
  setAuthContext({ token });
}

function authHeaders(): Record<string, string> {
  const auth = getAuthContext();
  const headers: Record<string, string> = {
  };
  if (auth.user) {
    headers['x-projectrag-user'] = auth.user;
    headers['x-projectrag-role'] = auth.role;
    headers['x-projectrag-tenant-id'] = auth.tenantId;
  }
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`;
  return headers;
}

function emitAuthError(error: ApiError): void {
  if (typeof window === 'undefined') return;
  if (error.status === 401 || error.status === 403) {
    window.dispatchEvent(new CustomEvent('projectrag-auth-error', { detail: error }));
  }
}

async function parseError(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  }
  try {
    return await response.text();
  } catch {
    return undefined;
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase()}${path}`, {
    cache: 'no-store',
    ...init,
    headers: {
      ...(init.headers || {}),
      ...authHeaders(),
    },
  });
  if (!response.ok) {
    const detail = await parseError(response);
    const error = new ApiError(`${init.method || 'GET'} ${path} failed: ${response.status}`, response.status, detail);
    emitAuthError(error);
    throw error;
  }
  return response.json();
}

export async function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'GET' });
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
}
