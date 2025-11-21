import math
from typing import Dict, Optional


def paginate(skip: int, limit: int, total: int) -> Dict[str, Optional[int]]:
    """
    Returns page-based pagination metadata for API responses.

    Args:
        skip (int): Number of items skipped (offset).
        limit (int): Number of items per page.
        total (int): Total number of items in the database.

    Returns:
        dict: Pagination info with keys: current_page, total_pages, next, previous, limit, total.
    """
    if limit <= 0:
        limit = 1  # avoid division by zero

    total_pages = math.ceil(total / limit)
    current_page = (skip // limit) + 1

    next_page = current_page + 1 if current_page < total_pages else None
    previous_page = current_page - 1 if current_page > 1 else None

    return {
        "currentPage": current_page,
        "totalPages": total_pages,
        "next": next_page,
        "previous": previous_page,
        "limit": limit,
        "total": total,
    }
