from __future__ import annotations

import sqlite3

from .connection import get_pool
from ..exceptions import DatabaseError


def create_tables() -> None:
    """Create database tables with optimized schema and indexes."""
    try:
        with get_pool().get_connection() as connection:
            cursor = connection.cursor()
            
            # Create notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
            """)
            
            # Create action_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                );
            """)
            
            # Add updated_at column to notes table if it doesn't exist
            try:
                cursor.execute("ALTER TABLE notes ADD COLUMN updated_at TEXT DEFAULT (datetime('now'))")
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass
            
            # Create performance indexes
            create_indexes(cursor)
            
            connection.commit()
    except Exception as e:
        raise DatabaseError("create tables", str(e))


def create_indexes(cursor) -> None:
    """Create database indexes for optimal query performance."""
    indexes = [
        # Notes table indexes
        "CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC)",
        
        # Action items table indexes
        "CREATE INDEX IF NOT EXISTS idx_action_items_note_id ON action_items(note_id)",
        "CREATE INDEX IF NOT EXISTS idx_action_items_done ON action_items(done)",
        "CREATE INDEX IF NOT EXISTS idx_action_items_created_at ON action_items(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_action_items_note_done ON action_items(note_id, done)",
        
        # Composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_action_items_note_created ON action_items(note_id, created_at DESC)",
    ]
    
    # Only create updated_at index if the column exists
    try:
        cursor.execute("SELECT updated_at FROM notes LIMIT 1")
        indexes.append("CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC)")
    except sqlite3.OperationalError:
        # updated_at column doesn't exist, skip the index
        pass
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except sqlite3.OperationalError as e:
            # Skip indexes that fail (e.g., column doesn't exist)
            print(f"Warning: Could not create index: {e}")
            continue


def optimize_database() -> None:
    """Run database optimization commands."""
    try:
        with get_pool().get_connection() as connection:
            cursor = connection.cursor()
            
            # Analyze tables for query optimization
            cursor.execute("ANALYZE")
            
            # Optimize database file
            cursor.execute("VACUUM")
            
            connection.commit()
    except Exception as e:
        raise DatabaseError("optimize database", str(e))


def get_database_stats() -> dict:
    """Get database statistics for monitoring."""
    try:
        with get_pool().get_connection() as connection:
            cursor = connection.cursor()
            
            # Get table sizes
            cursor.execute("""
                SELECT 
                    name,
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=main.name) as row_count
                FROM sqlite_master 
                WHERE type='table' AND name IN ('notes', 'action_items')
            """)
            
            stats = {}
            for row in cursor.fetchall():
                table_name = row['name']
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count_result = cursor.fetchone()
                stats[table_name] = count_result['count'] if count_result else 0
            
            return stats
    except Exception as e:
        raise DatabaseError("get database stats", str(e))
