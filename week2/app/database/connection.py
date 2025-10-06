from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from ..exceptions import DatabaseError


class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool for better performance."""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections: list[sqlite3.Connection] = []
        self._lock = threading.Lock()
        self._ensure_db_directory()
    
    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimizations."""
        connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow sharing across threads
            timeout=30.0,  # 30 second timeout
        )
        connection.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrency
        connection.execute("PRAGMA journal_mode=WAL")
        
        # Enable foreign key constraints
        connection.execute("PRAGMA foreign_keys=ON")
        
        # Optimize for performance
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA cache_size=10000")
        connection.execute("PRAGMA temp_store=MEMORY")
        
        return connection
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool with automatic cleanup."""
        connection = None
        try:
            with self._lock:
                if self._connections:
                    connection = self._connections.pop()
                elif len(self._connections) < self.max_connections:
                    connection = self._create_connection()
                else:
                    # Wait for a connection to become available
                    connection = self._create_connection()
            
            yield connection
        except Exception as e:
            if connection:
                try:
                    connection.rollback()
                except Exception:
                    pass
            raise DatabaseError("get connection", str(e))
        finally:
            if connection:
                try:
                    connection.commit()
                    with self._lock:
                        if len(self._connections) < self.max_connections:
                            self._connections.append(connection)
                        else:
                            connection.close()
                except Exception:
                    if connection:
                        connection.close()
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for connection in self._connections:
                try:
                    connection.close()
                except Exception:
                    pass
            self._connections.clear()


# Global connection pool instance
_pool: Optional[DatabaseConnectionPool] = None


def get_pool() -> DatabaseConnectionPool:
    """Get the global connection pool instance."""
    global _pool
    if _pool is None:
        from .. import db
        _pool = DatabaseConnectionPool(db.DB_PATH)
    return _pool


def close_pool() -> None:
    """Close the global connection pool."""
    global _pool
    if _pool:
        _pool.close_all()
        _pool = None
