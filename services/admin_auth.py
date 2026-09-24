# Admin auth sidecar — new file, v1 auth code untouched.
# Token scheme is intentionally distinct from user tokens:
#   user  -> token_{username}_{id}
#   admin -> admin_token_{username}_{id}
# Demo-grade auth (no JWT). Do not use for production without JWT + rate limiting.

import os


def _get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def is_admin_token(authorization: str | None) -> bool:
    if not authorization:
        return False
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return False
    return token.startswith("admin_token_")


def admin_username_from_token(authorization: str | None) -> str | None:
    if not is_admin_token(authorization):
        return None
    _, _, token = authorization.partition(" ")
    parts = token.split("_")
    # admin_token_{username}_{id}
    if len(parts) >= 4:
        return "_".join(parts[2:-1])
    return None


def require_admin(authorization=None) -> str:
    """FastAPI dependency — use ONLY on /api/admin/* routes.

    `authorization` is injected by FastAPI via the `Depends` wrapper
    registered in server.py (Header). Kept untyped here so the seed path
    works even when fastapi isn't installed.
    """
    try:
        from fastapi import HTTPException as _HTTPException
    except ImportError:
        class _HTTPException(Exception):  # type: ignore
            def __init__(self, status_code=403, detail=""):
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail
    username = admin_username_from_token(authorization)
    if not username:
        raise _HTTPException(status_code=403, detail="Admin access required")
    # Belt-and-braces: verify the admin still exists and is_admin.
    try:
        from services.auth_db import AuthSessionLocal, UserAuthModel

        db = AuthSessionLocal()
        try:
            user = db.query(UserAuthModel).filter(
                UserAuthModel.username == username
            ).first()
            if not user or not user.is_admin:
                raise _HTTPException(status_code=403, detail="Admin access required")
        finally:
            db.close()
    except _HTTPException:
        raise
    except Exception:
        # If auth.db is unreachable, fail closed.
        raise _HTTPException(status_code=403, detail="Admin access required")
    return username


def ensure_admin_seed() -> None:
    """Ensure the env-configured admin exists. No plaintext password in code.

    Env:
      ADMIN_USERNAME (default: admin)
      ADMIN_PASSWORD (plaintext, only from env — e.g. admin@123 for demo)
      ADMIN_PASSWORD_HASH (preferred: pre-hashed with services.auth_db.hash_password)
      ADMIN_EMAIL / ADMIN_FULL_NAME / ADMIN_DEPARTMENT (optional)
    """
    from services.auth_db import AuthSessionLocal, UserAuthModel, hash_password

    username = _get_env("ADMIN_USERNAME", "admin").strip() or "admin"
    password_hash = _get_env("ADMIN_PASSWORD_HASH", "").strip()
    if not password_hash:
        password = _get_env("ADMIN_PASSWORD", "")
        if not password:
            return  # fail closed: do not create/reset admin without env creds
        password_hash = hash_password(password)

    email = _get_env("ADMIN_EMAIL", "admin@nexora.com").strip() or "admin@nexora.com"
    full_name = _get_env("ADMIN_FULL_NAME", "Platform Administrator").strip()
    department = _get_env("ADMIN_DEPARTMENT", "IT & SecOps").strip()

    db = AuthSessionLocal()
    try:
        user = db.query(UserAuthModel).filter(
            UserAuthModel.username == username
        ).first()
        if not user:
            user = UserAuthModel(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name or username,
                role="IT Administrator",
                department=department or "IT & SecOps",
                is_admin=True,
            )
            db.add(user)
        else:
            # Keep admin reachable via env; never downgrade.
            user.password_hash = password_hash
            user.is_admin = True
            if full_name:
                user.full_name = full_name
            if department:
                user.department = department
        db.commit()
    finally:
        db.close()
