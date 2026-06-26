'use client';

import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import {
  ApiError,
  AuthContext,
  AuthRole,
  authStatusMessage,
  clearAuthContext,
  getAuthContext,
  setAuthContext,
} from '@/lib/api';

type AuthState = AuthContext & {
  authenticated: boolean;
  lastAuthError: ApiError | null;
  updateAuth: (next: Partial<AuthContext>) => void;
  logout: () => void;
  canAccess: (roles?: AuthRole[]) => boolean;
};

const AuthContextState = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuth] = useState<AuthContext>(() => getAuthContext());
  const [lastAuthError, setLastAuthError] = useState<ApiError | null>(null);

  useEffect(() => {
    const refresh = () => setAuth(getAuthContext());
    const authError = (event: Event) => {
      const detail = (event as CustomEvent<ApiError>).detail;
      if (detail) setLastAuthError(detail);
    };
    window.addEventListener('projectrag-auth-changed', refresh);
    window.addEventListener('storage', refresh);
    window.addEventListener('projectrag-auth-error', authError);
    refresh();
    return () => {
      window.removeEventListener('projectrag-auth-changed', refresh);
      window.removeEventListener('storage', refresh);
      window.removeEventListener('projectrag-auth-error', authError);
    };
  }, []);

  const value = useMemo<AuthState>(() => ({
    ...auth,
    authenticated: Boolean(auth.token || auth.user),
    lastAuthError,
    updateAuth: (next) => {
      setAuthContext(next);
      setAuth(getAuthContext());
      setLastAuthError(null);
    },
    logout: () => {
      clearAuthContext();
      setAuth(getAuthContext());
    },
    canAccess: (roles) => !roles || roles.includes(auth.role),
  }), [auth, lastAuthError]);

  return <AuthContextState.Provider value={value}>{children}</AuthContextState.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContextState);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}

export function AuthErrorBanner({ error }: { error: unknown }) {
  return (
    <section className="card auth-state" role="alert">
      <span className="badge danger">Access issue</span>
      <h2>{authStatusMessage(error)}</h2>
      <p>Check your token, role, and tenant context in the left navigation.</p>
    </section>
  );
}

export function ProtectedPage({
  children,
  roles,
}: {
  children: React.ReactNode;
  roles?: AuthRole[];
}) {
  const auth = useAuth();
  if (!auth.authenticated) {
    return <AuthErrorBanner error={new ApiError(401, 'Authentication required')} />;
  }
  if (!auth.canAccess(roles)) {
    return <AuthErrorBanner error={new ApiError(403, 'Forbidden')} />;
  }
  return <>{children}</>;
}
