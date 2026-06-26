"""Static smoke checks for frontend auth wiring."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PROTECTED = ["ask", "documents", "audit", "evaluation", "topology", "admin"]


def main() -> int:
    api = (FRONTEND / "lib/api.ts").read_text()
    required_api = ["Authorization", "x-projectrag-user", "x-projectrag-role", "x-projectrag-tenant-id", "ApiError", "projectrag-auth-error"]
    missing = [item for item in required_api if item not in api]
    if missing:
        raise SystemExit(f"frontend API auth wrapper missing: {missing}")

    shell = (FRONTEND / "components/AppShell.tsx").read_text()
    for required in ["Tenant", "disabled={!tenantEditable}", "role === 'admin'"]:
        if required not in shell:
            raise SystemExit(f"AppShell tenant/admin control missing: {required}")

    for page in PROTECTED:
        text = (FRONTEND / f"app/{page}/page.tsx").read_text()
        if "ProtectedPage" not in text:
            raise SystemExit(f"/{page} is not protected")
    if "roles={['admin']}" not in (FRONTEND / "app/admin/page.tsx").read_text():
        raise SystemExit("/admin is not admin-only")
    if "roles={['admin']}" not in (FRONTEND / "app/audit/page.tsx").read_text():
        raise SystemExit("/audit is not admin-only")

    print("frontend auth validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
