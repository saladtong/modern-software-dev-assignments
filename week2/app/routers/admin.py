from __future__ import annotations

from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from .. import db
from ..exceptions import handle_database_error

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=Dict[str, Any])
def get_database_stats() -> Dict[str, Any]:
    """
    Get database and cache statistics.
    
    Returns comprehensive statistics about database performance and cache usage.
    """
    try:
        return db.get_database_stats()
    except Exception as e:
        handle_database_error("get database stats", e)


@router.post("/optimize")
def optimize_database() -> Dict[str, str]:
    """
    Run database optimization.
    
    Performs VACUUM and ANALYZE operations to optimize database performance.
    """
    try:
        db.optimize_database()
        return {"message": "Database optimization completed successfully"}
    except Exception as e:
        handle_database_error("optimize database", e)


@router.post("/cleanup")
def cleanup_database() -> Dict[str, str]:
    """
    Clean up database connections and cache.
    
    Closes connection pool and clears cache for memory management.
    """
    try:
        db.cleanup_database()
        return {"message": "Database cleanup completed successfully"}
    except Exception as e:
        handle_database_error("cleanup database", e)
