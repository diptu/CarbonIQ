# ruff: noqa: D100
"""Users API (create/get/list + login) with consistent envelopes."""

from __future__ import annotations

from uuid import UUID

import bcrypt
from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from app.core.errors import AppError
from app.core.logging import get_logger
from app.domain import UserCreate, UserFilter, UserRole, UserService
from app.domain.services import PasswordHasher
from app.persistence import SqlUserRepo
from app.persistence.db import get_session
from app.persistence.repositories import UserSQL

log = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


def _ok(
    *,
    message: str = "OK",
    data: dict | list | None = None,
    meta: dict | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    body: dict = {"status": "success", "message": message}
    if data is not None:
        body["data"] = data
    if meta is not None:
        body["meta"] = meta
    return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


def _fail(
    *,
    message: str,
    code: str = "ERROR",
    details: dict | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    body: dict = {
        "status": "fail" if 400 <= status_code < 500 else "error",
        "code": code,
        "message": message,
    }
    if details:
        body["details"] = details
    return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


class BcryptHasher(PasswordHasher):
    """bcrypt hasher."""

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())


def get_service(session: Session = Depends(get_session)) -> UserService:
    """DI: UserService with SQL repo + bcrypt."""
    return UserService(users=SqlUserRepo(session), hasher=BcryptHasher())


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    svc: UserService = Depends(get_service),
) -> JSONResponse:
    try:
        user = svc.create_user(data)
        return _ok(
            message="User created",
            data=user.model_dump(),
            status_code=status.HTTP_201_CREATED,
        )
    except AppError as exc:
        log.warning("create_user failed: %s", exc, extra=exc.details)
        return _fail(
            message=exc.message,
            code=exc.code,
            details=exc.details,
            status_code=exc.status_code,
        )
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("create_user unexpected error")
        return _fail(
            message="Internal server error.",
            code="UNEXPECTED_ERROR",
            details={"reason": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/{user_id}")
def get_user(
    user_id: str,
    svc: UserService = Depends(get_service),
) -> JSONResponse:
    try:
        user = svc.get_user(UUID(user_id))
        return _ok(message="User fetched", data=user.model_dump())
    except AppError as exc:
        log.info("get_user app error: %s", exc, extra=exc.details)
        return _fail(
            message=exc.message,
            code=exc.code,
            details=exc.details,
            status_code=exc.status_code,
        )
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("get_user unexpected error")
        return _fail(
            message="Internal server error.",
            code="UNEXPECTED_ERROR",
            details={"reason": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("")
def list_users(
    svc: UserService = Depends(get_service),
    role: UserRole | None = Query(default=None),
    active_only: bool = Query(default=True),
) -> JSONResponse:
    try:
        flt = UserFilter(role=role, active_only=active_only)
        users = svc.list_users(flt)
        payload = {"items": [u.model_dump() for u in users], "total": len(users)}
        return _ok(message="Users listed", data=payload)
    except AppError as exc:
        log.info("list_users app error: %s", exc, extra=exc.details)
        return _fail(
            message=exc.message,
            code=exc.code,
            details=exc.details,
            status_code=exc.status_code,
        )
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("list_users unexpected error")
        return _fail(
            message="Internal server error.",
            code="UNEXPECTED_ERROR",
            details={"reason": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/login")
def login(
    email: str,
    password: str,
    session: Session = Depends(get_session),
) -> JSONResponse:
    try:
        users = SqlUserRepo(session)
        hasher = BcryptHasher()

        user = users.get_by_email(email)
        if not user:
            raise AppError(
                status_code=401, code="AUTH_INVALID", message="Invalid creds."
            )

        row = session.exec(select(UserSQL).where(UserSQL.id == user.id)).first()
        if not row or not hasher.verify(password, row.password_hash):
            raise AppError(
                status_code=401, code="AUTH_INVALID", message="Invalid creds."
            )

        svc = UserService(users=users, hasher=hasher)
        tokens = svc.issue_tokens(user.id)
        return _ok(message="Login successful", data=tokens.model_dump())
    except AppError as exc:
        log.info("login app error: %s", exc, extra=exc.details)
        return _fail(
            message=exc.message,
            code=exc.code,
            details=exc.details,
            status_code=exc.status_code,
        )
    except Exception as exc:  # pylint: disable=broad-except
        log.exception("login unexpected error")
        return _fail(
            message="Internal server error.",
            code="UNEXPECTED_ERROR",
            details={"reason": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
