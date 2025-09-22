"""Refresh-token store with Redis backend and safe in-memory fallback."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

try:
    from redis.asyncio import Redis  # type: ignore
except Exception:  # pragma: no cover
    Redis = None  # type: ignore[assignment]

from .settings import Settings, get_settings

log = logging.getLogger("ima.token_store")


# ------------------------------- protocol ------------------------------------ #


class TokenStore(Protocol):
    async def mark_refresh_active(
        self, *, user_id: str, jti: str, ttl_s: int
    ) -> None: ...
    async def is_refresh_active(self, jti: str) -> bool: ...
    async def rotate_refresh(
        self, *, user_id: str, old_jti: str, new_jti: str, ttl_s: int
    ) -> None: ...
    async def revoke_refresh(self, jti: str, *, user_id: str | None = None) -> None: ...
    async def revoke_all_for_user(self, user_id: str) -> None: ...


def ttl_from_exp(exp_epoch: int) -> int:
    """Compute TTL seconds from an 'exp' epoch (clamped >= 0)."""
    now = int(datetime.now(timezone.utc).timestamp())
    return max(exp_epoch - now, 0)


# ------------------------------- memory -------------------------------------- #


@dataclass(slots=True)
class _MemEntry:
    user_id: str
    exp_epoch: int  # absolute exp; we compute ttl on read


class MemoryTokenStore:
    """Process-local store: OK for dev/tests; not for multi-instance prod."""

    def __init__(self) -> None:
        self._jti: dict[str, _MemEntry] = {}
        self._user_jtis: dict[str, set[str]] = {}

    async def mark_refresh_active(self, *, user_id: str, jti: str, ttl_s: int) -> None:
        exp = int(datetime.now(timezone.utc).timestamp()) + int(ttl_s)
        self._jti[jti] = _MemEntry(user_id=user_id, exp_epoch=exp)
        self._user_jtis.setdefault(user_id, set()).add(jti)

    async def is_refresh_active(self, jti: str) -> bool:
        e = self._jti.get(jti)
        if not e:
            return False
        if e.exp_epoch <= int(datetime.now(timezone.utc).timestamp()):
            # expired: clean up lazily
            await self.revoke_refresh(jti, user_id=e.user_id)
            return False
        return True

    async def rotate_refresh(
        self, *, user_id: str, old_jti: str, new_jti: str, ttl_s: int
    ) -> None:
        await self.revoke_refresh(old_jti, user_id=user_id)
        await self.mark_refresh_active(user_id=user_id, jti=new_jti, ttl_s=ttl_s)

    async def revoke_refresh(self, jti: str, *, user_id: str | None = None) -> None:
        e = self._jti.pop(jti, None)
        uid = user_id or (e.user_id if e else None)
        if uid and uid in self._user_jtis:
            self._user_jtis[uid].discard(jti)
            if not self._user_jtis[uid]:
                self._user_jtis.pop(uid, None)

    async def revoke_all_for_user(self, user_id: str) -> None:
        for j in list(self._user_jtis.get(user_id, ())):
            self._jti.pop(j, None)
        self._user_jtis.pop(user_id, None)


# ------------------------------- redis --------------------------------------- #


class RedisTokenStore:
    """Redis-backed store: supports multi-instance deployments."""

    def __init__(self, r: "Redis", *, prefix: str = "ima:rt") -> None:  # type: ignore[name-defined]
        self._r = r
        self._p = prefix

    def _k_jti(self, jti: str) -> str:
        return f"{self._p}:jti:{jti}"

    def _k_user(self, user_id: str) -> str:
        return f"{self._p}:user:{user_id}"

    async def mark_refresh_active(self, *, user_id: str, jti: str, ttl_s: int) -> None:
        # value=user_id for quick checks; also add to user's set of JTIs
        pipe = self._r.pipeline()
        pipe.set(self._k_jti(jti), user_id, ex=int(ttl_s), nx=True)  # set if not exists
        pipe.sadd(self._k_user(user_id), jti)
        pipe.expire(self._k_user(user_id), int(max(ttl_s, 60)))
        await pipe.execute()

    async def is_refresh_active(self, jti: str) -> bool:
        return bool(await self._r.exists(self._k_jti(jti)))

    async def rotate_refresh(
        self, *, user_id: str, old_jti: str, new_jti: str, ttl_s: int
    ) -> None:
        pipe = self._r.pipeline()
        pipe.delete(self._k_jti(old_jti))
        pipe.set(self._k_jti(new_jti), user_id, ex=int(ttl_s))
        pipe.sadd(self._k_user(user_id), new_jti)
        pipe.srem(self._k_user(user_id), old_jti)
        pipe.expire(self._k_user(user_id), int(max(ttl_s, 60)))
        await pipe.execute()

    async def revoke_refresh(self, jti: str, *, user_id: str | None = None) -> None:
        # if user_id unknown, try to fetch from value
        uid = user_id
        if uid is None:
            uid = await self._r.get(self._k_jti(jti))
        pipe = self._r.pipeline()
        pipe.delete(self._k_jti(jti))
        if uid:
            pipe.srem(self._k_user(str(uid)), jti)
        await pipe.execute()

    async def revoke_all_for_user(self, user_id: str) -> None:
        # delete all jtis in set, then the set
        key_u = self._k_user(user_id)
        jt_is = await self._r.smembers(key_u)
        if jt_is:
            pipe = self._r.pipeline()
            for j in jt_is:
                pipe.delete(self._k_jti(j))
            pipe.delete(key_u)
            await pipe.execute()
        else:
            await self._r.delete(key_u)


# ------------------------------- factory ------------------------------------- #

_STORE: TokenStore | None = None


def _make_store(st: Settings) -> TokenStore:
    """Create a store: Redis if DSN is configured and reachable, else Memory."""
    dsn = None
    try:
        dsn = (st.redis_dsn or st.redis_url).get_secret_value()  # type: ignore[union-attr]
    except Exception:
        dsn = None

    if dsn and Redis is not None:
        try:
            r = Redis.from_url(dsn, decode_responses=True)  # type: ignore[arg-type]
            # quick probe
            asyncio.get_event_loop()

            # ping with short timeout
            async def _probe() -> bool:
                try:
                    return (await r.ping()) is True
                except Exception:
                    return False

            ok = asyncio.get_event_loop().run_until_complete(_probe())
            if ok:
                log.info("TokenStore: using Redis backend")
                return RedisTokenStore(r)
            log.warning(
                "TokenStore: Redis DSN set but ping failed, falling back to memory"
            )
        except Exception as exc:  # pragma: no cover
            log.warning(
                "TokenStore: Redis init failed (%s), falling back to memory", exc
            )

    log.info("TokenStore: using in-memory backend")
    return MemoryTokenStore()


def get_token_store(st: Settings | None = None) -> TokenStore:
    """Singleton accessor used by FastAPI DI."""
    global _STORE  # noqa: PLW0603
    if _STORE is None:
        _STORE = _make_store(st or get_settings())
    return _STORE


__all__ = [
    "TokenStore",
    "get_token_store",
    "ttl_from_exp",
    "MemoryTokenStore",
    "RedisTokenStore",
]
