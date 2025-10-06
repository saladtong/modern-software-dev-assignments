from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

# Import optimized database components
from .database.connection import get_pool, close_pool
from .database.schema import create_tables
from .database.optimized_db import optimized_db

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Get a database connection (legacy method - use optimized_db for new code)."""
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Initialize the database with optimized schema and indexes."""
    ensure_data_directory_exists()
    create_tables()


# Legacy functions - maintained for backward compatibility
# New code should use optimized_db for better performance

def insert_note(content: str) -> int:
    """Legacy function - use optimized_db.create_note() for new code."""
    return optimized_db.create_note(content)


def list_notes() -> list[sqlite3.Row]:
    """Legacy function - use optimized_db.list_notes() for new code."""
    return optimized_db.list_notes()


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    """Legacy function - use optimized_db.get_note() for new code."""
    return optimized_db.get_note(note_id)


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    """Legacy function - use optimized_db.create_action_items_batch() for new code."""
    return optimized_db.create_action_items_batch(items, note_id)


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    """Legacy function - use optimized_db.list_action_items() for new code."""
    return optimized_db.list_action_items(note_id)


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Legacy function - use optimized_db.update_action_item_status() for new code."""
    optimized_db.update_action_item_status(action_item_id, done)


def delete_note(note_id: int) -> None:
    """Legacy function - use optimized_db.delete_note() for new code."""
    optimized_db.delete_note(note_id)


# New optimized functions
def get_database_stats() -> dict:
    """Get database and cache statistics."""
    return optimized_db.get_stats()


def optimize_database() -> None:
    """Run database optimization."""
    optimized_db.optimize_database()


def cleanup_database() -> None:
    """Clean up database connections."""
    close_pool()

