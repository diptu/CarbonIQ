"""User domain services (hasher, repo adapter, service, authenticate_user)."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional
from passlib.context import CryptContext

# --------------------------- password hashing --------------------------------
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    def hash(self, password: str) -> str:
        return _pwd.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return _pwd.verify(password, password_hash)
        except Exception:
            return False  # pragma: no cover


# --------------------------- optional SQL repo wiring -------------------------
def _load_repo() -> dict[str, Optional[Callable[..., Any]]]:
    try:
        from ..persistence.repositories import (  # type: ignore
            create_user,
            delete_user,
            get_user_by_email,
            get_user_by_id,
            list_users,
            update_user,
        )

        return {
            "create_user": create_user,
            "delete_user": delete_user,
            "get_user_by_email": get_user_by_email,
            "get_user_by_id": get_user_by_id,
            "list_users": list_users,
            "update_user": update_user,
        }
    except Exception:  # pragma: no cover
        return {
            "create_user": None,
            "delete_user": None,
            "get_user_by_email": None,
            "get_user_by_id": None,
            "list_users": None,
            "update_user": None,
        }


_REPO_FUNCS = _load_repo()


# --------------------------- in-memory fallback -------------------------------
@dataclass
class _MemUser:
    id: str
    email: str | None
    role: str
    password_hash: str


class _MemStore:
    def __init__(self) -> None:
        self._by_id: dict[str, _MemUser] = {}
        self._by_email: dict[str, _MemUser] = {}

    def upsert(self, u: _MemUser) -> _MemUser:
        self._by_id[u.id] = u
        if u.email:
            self._by_email[u.email.lower()] = u
        return u

    def get_by_email(self, email: str) -> _MemUser | None:
        return self._by_email.get(email.lower())

    def get_by_id(self, uid: str) -> _MemUser | None:
        return self._by_id.get(uid)

    def list(self) -> Iterable[_MemUser]:
        return list(self._by_id.values())

    def delete(self, uid: str) -> bool:
        u = self._by_id.pop(uid, None)
        if not u:
            return False
        if u.email:
            self._by_email.pop(u.email.lower(), None)
        return True


_hasher = PasswordHasher()
_mem = _MemStore()
# Seed demo owner for bootstrap: admin@example.com / secret
_mem.upsert(
    _MemUser(
        id="u-demo-owner",
        email="admin@example.com",
        role="owner",
        password_hash=_hasher.hash("secret"),
    )
)


# --------------------------- repository adapter -------------------------------
class UserRepo:
    async def get_by_email(self, email: str) -> Any | None:
        fn = _REPO_FUNCS["get_user_by_email"]
        if fn:
            try:
                res = fn(email)
                res = await res if hasattr(res, "__await__") else res
                if res:
                    return res
            except Exception:
                pass
        return _mem.get_by_email(email)

    async def get_by_id(self, user_id: str) -> Any | None:
        fn = _REPO_FUNCS["get_user_by_id"]
        if fn:
            try:
                res = fn(user_id)
                res = await res if hasattr(res, "__await__") else res
                if res:
                    return res
            except Exception:
                pass
        return _mem.get_by_id(user_id)

    async def list(self) -> Iterable[Any]:
        fn = _REPO_FUNCS["list_users"]
        if fn:
            try:
                res = fn()
                res = await res if hasattr(res, "__await__") else res
                if res is not None:
                    return res
            except Exception:
                pass
        return _mem.list()

    async def create(self, *, email: str, role: str, password: str) -> Any:
        fn = _REPO_FUNCS["create_user"]
        if not fn:
            uid = f"u-{len(list(_mem.list())) + 1:04d}"
            return _mem.upsert(
                _MemUser(
                    id=uid, email=email, role=role, password_hash=_hasher.hash(password)
                )
            )
        try:
            res = fn(email=email, role=role, password_hash=_hasher.hash(password))
            return await res if hasattr(res, "__await__") else res
        except Exception:
            uid = f"u-{len(list(_mem.list())) + 1:04d}"
            return _mem.upsert(
                _MemUser(
                    id=uid, email=email, role=role, password_hash=_hasher.hash(password)
                )
            )

    async def delete(self, user_id: str) -> bool:
        fn = _REPO_FUNCS["delete_user"]
        if fn:
            try:
                res = fn(user_id)
                out = await res if hasattr(res, "__await__") else res
                if out:
                    return True
            except Exception:
                pass
        return _mem.delete(user_id)

    async def update(self, user_id: str, **fields: Any) -> Any | None:
        fn = _REPO_FUNCS["update_user"]
        if fn:
            try:
                res = fn(user_id, **fields)
                res = await res if hasattr(res, "__await__") else res
                if res is not None:
                    return res
            except Exception:
                pass
        u = _mem.get_by_id(user_id)
        if not u:
            return None
        if "role" in fields:
            u.role = str(fields["role"])
        if "password" in fields:
            u.password_hash = _hasher.hash(str(fields["password"]))
        if "email" in fields:
            u.email = str(fields["email"])
        return u


# --------------------------- service ------------------------------------------
def _extract(obj: Any, *cands: str) -> Any | None:
    if isinstance(obj, Mapping):
        for k in cands:
            if k in obj:
                return obj[k]
        return None
    for k in cands:
        if hasattr(obj, k):
            return getattr(obj, k)
    return None


class UserService:
    def __init__(self, repo: UserRepo, hasher: PasswordHasher) -> None:
        self._repo = repo
        self._hasher = hasher

    async def authenticate_user(self, email: str, password: str) -> Any | None:
        u = await self._repo.get_by_email(email)
        if not u:
            return None
        stored = _extract(u, "password_hash", "hashed_password", "password")
        return (
            u
            if (isinstance(stored, str) and self._hasher.verify(password, stored))
            else None
        )

    async def create_user(self, *, email: str, role: str, password: str) -> Any:
        role = role.lower()
        if role not in {"owner", "editor", "viewer"}:
            role = "viewer"
        return await self._repo.create(email=email, role=role, password=password)

    async def get_user(self, user_id: str) -> Any | None:
        return await self._repo.get_by_id(user_id)

    async def list_users(self) -> Iterable[Any]:
        return await self._repo.list()

    async def delete_user(self, user_id: str) -> bool:
        return await self._repo.delete(user_id)


# module-level default service + façade for auth.py
_REPO = UserRepo()
_SERVICE = UserService(_REPO, _hasher)


async def authenticate_user(email: str, password: str) -> Any | None:
    return await _SERVICE.authenticate_user(email, password)


__all__ = ["PasswordHasher", "UserRepo", "UserService", "authenticate_user"]
