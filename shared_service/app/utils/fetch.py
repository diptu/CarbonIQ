from typing import Awaitable, Callable, TypeVar

from fastapi import HTTPException

T = TypeVar("T")  # Generic type for model


async def fetch_or_404(crud_get: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    """
    Generic async fetch helper.

    Args:
        crud_get: The async CRUD `get` method to call.
        *args, **kwargs: Arguments to pass to the CRUD `get` method.

    Returns:
        Instance of T (model)

    Raises:
        HTTPException(404) if not found.
    """
    obj = await crud_get(*args, **kwargs)
    if not obj:
        raise HTTPException(status_code=404, detail="Item Not found")
    return obj
