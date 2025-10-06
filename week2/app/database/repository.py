from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, TypeVar, Generic

from .connection import get_pool
from ..exceptions import DatabaseError

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Base repository class for database operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection from the pool."""
        with get_pool().get_connection() as connection:
            yield connection
    
    def _execute_query(
        self, 
        query: str, 
        params: tuple = (), 
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """Execute a query with proper error handling."""
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return list(cursor.fetchall())
                else:
                    return cursor.lastrowid
        except Exception as e:
            raise DatabaseError(f"execute query on {self.table_name}", str(e))
    
    def _execute_transaction(self, operations: List[tuple[str, tuple]]) -> List[Any]:
        """Execute multiple operations in a single transaction."""
        try:
            with self._get_connection() as connection:
                cursor = connection.cursor()
                results = []
                
                for query, params in operations:
                    cursor.execute(query, params)
                    results.append(cursor.lastrowid)
                
                connection.commit()
                return results
        except Exception as e:
            raise DatabaseError(f"execute transaction on {self.table_name}", str(e))
    
    @abstractmethod
    def create(self, *args, **kwargs) -> Any:
        """Create a new record."""
        pass
    
    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[Any]:
        """Get a record by ID."""
        pass
    
    @abstractmethod
    def list_all(self, *args, **kwargs) -> List[Any]:
        """List all records with optional filters."""
        pass
    
    @abstractmethod
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """Update a record."""
        pass
    
    @abstractmethod
    def delete(self, record_id: int) -> bool:
        """Delete a record."""
        pass


class NoteRepository(BaseRepository):
    """Repository for note operations."""
    
    def __init__(self):
        super().__init__("notes")
    
    def create(self, content: str) -> int:
        """Create a new note and return its ID."""
        query = "INSERT INTO notes (content) VALUES (?)"
        return self._execute_query(query, (content,))
    
    def get_by_id(self, note_id: int) -> Optional[sqlite3.Row]:
        """Get a note by ID."""
        query = "SELECT id, content, created_at FROM notes WHERE id = ?"
        return self._execute_query(query, (note_id,), fetch_one=True)
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[sqlite3.Row]:
        """List all notes with pagination."""
        query = "SELECT id, content, created_at FROM notes ORDER BY id DESC"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        return self._execute_query(query, fetch_all=True)
    
    def update(self, note_id: int, data: Dict[str, Any]) -> bool:
        """Update a note's content."""
        content = data.get('content')
        if not content:
            raise ValueError("content is required for note update")
        query = "UPDATE notes SET content = ?, updated_at = datetime('now') WHERE id = ?"
        self._execute_query(query, (content, note_id))
        return True
    
    def delete(self, note_id: int) -> bool:
        """Delete a note and return success status."""
        query = "DELETE FROM notes WHERE id = ?"
        self._execute_query(query, (note_id,))
        return True
    
    def count(self) -> int:
        """Get total count of notes."""
        query = "SELECT COUNT(*) as count FROM notes"
        result = self._execute_query(query, fetch_one=True)
        return result["count"] if result else 0


class ActionItemRepository(BaseRepository):
    """Repository for action item operations."""
    
    def __init__(self):
        super().__init__("action_items")
    
    def create(self, text: str, note_id: Optional[int] = None) -> int:
        """Create a new action item and return its ID."""
        query = "INSERT INTO action_items (note_id, text) VALUES (?, ?)"
        return self._execute_query(query, (note_id, text))
    
    def create_batch(self, items: List[tuple[str, Optional[int]]]) -> List[int]:
        """Create multiple action items in a single transaction."""
        operations = [
            ("INSERT INTO action_items (text, note_id) VALUES (?, ?)", (text, note_id))
            for text, note_id in items
        ]
        return self._execute_transaction(operations)
    
    def get_by_id(self, action_item_id: int) -> Optional[sqlite3.Row]:
        """Get an action item by ID."""
        query = """
            SELECT id, note_id, text, done, created_at 
            FROM action_items 
            WHERE id = ?
        """
        return self._execute_query(query, (action_item_id,), fetch_one=True)
    
    def list_all(self, note_id: Optional[int] = None, limit: Optional[int] = None, offset: int = 0) -> List[sqlite3.Row]:
        """List action items with optional filtering and pagination."""
        if note_id:
            query = """
                SELECT id, note_id, text, done, created_at 
                FROM action_items 
                WHERE note_id = ? 
                ORDER BY id DESC
            """
            params = (note_id,)
        else:
            query = """
                SELECT id, note_id, text, done, created_at 
                FROM action_items 
                ORDER BY id DESC
            """
            params = ()
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        return self._execute_query(query, params, fetch_all=True)
    
    def update(self, action_item_id: int, data: Dict[str, Any]) -> bool:
        """Update an action item."""
        updates = []
        params = []
        
        if 'text' in data:
            updates.append("text = ?")
            params.append(data['text'])
        
        if 'done' in data:
            updates.append("done = ?")
            params.append(1 if data['done'] else 0)
        
        if not updates:
            raise ValueError("No valid fields to update")
        
        query = f"UPDATE action_items SET {', '.join(updates)} WHERE id = ?"
        params.append(action_item_id)
        self._execute_query(query, tuple(params))
        return True
    
    def update_status(self, action_item_id: int, done: bool) -> bool:
        """Update an action item's done status."""
        return self.update(action_item_id, {'done': done})
    
    def delete(self, action_item_id: int) -> bool:
        """Delete an action item."""
        query = "DELETE FROM action_items WHERE id = ?"
        self._execute_query(query, (action_item_id,))
        return True
    
    def delete_by_note_id(self, note_id: int) -> int:
        """Delete all action items for a specific note."""
        query = "DELETE FROM action_items WHERE note_id = ?"
        self._execute_query(query, (note_id,))
        return True
    
    def count(self, note_id: Optional[int] = None) -> int:
        """Get count of action items, optionally filtered by note."""
        if note_id:
            query = "SELECT COUNT(*) as count FROM action_items WHERE note_id = ?"
            params = (note_id,)
        else:
            query = "SELECT COUNT(*) as count FROM action_items"
            params = ()
        
        result = self._execute_query(query, params, fetch_one=True)
        return result["count"] if result else 0


# Repository instances
note_repository = NoteRepository()
action_item_repository = ActionItemRepository()
