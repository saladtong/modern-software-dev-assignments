from __future__ import annotations

import sqlite3
from typing import List, Optional

from .connection import get_pool
from .repository import note_repository, action_item_repository
from .cache import cached_query, invalidate_cache
from ..exceptions import DatabaseError


class OptimizedDatabase:
    """Optimized database layer with connection pooling, caching, and batch operations."""
    
    def __init__(self):
        self.note_repo = note_repository
        self.action_item_repo = action_item_repository
    
    # Note operations with caching
    @cached_query(ttl=60)  # Cache for 1 minute
    def get_note(self, note_id: int) -> Optional[sqlite3.Row]:
        """Get a note by ID with caching."""
        return self.note_repo.get_by_id(note_id)
    
    @cached_query(ttl=30)  # Cache for 30 seconds
    def list_notes(self, limit: Optional[int] = None, offset: int = 0) -> List[sqlite3.Row]:
        """List notes with pagination and caching."""
        return self.note_repo.list_all(limit=limit, offset=offset)
    
    def create_note(self, content: str) -> int:
        """Create a new note and invalidate relevant caches."""
        note_id = self.note_repo.create(content)
        # Invalidate notes list cache
        invalidate_cache("list_notes")
        return note_id
    
    def update_note(self, note_id: int, content: str) -> bool:
        """Update a note and invalidate caches."""
        success = self.note_repo.update(note_id, content)
        if success:
            invalidate_cache("get_note")
            invalidate_cache("list_notes")
        return success
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note and all its action items."""
        try:
            # Delete action items first (cascade should handle this, but being explicit)
            self.action_item_repo.delete_by_note_id(note_id)
            # Delete the note
            success = self.note_repo.delete(note_id)
            if success:
                invalidate_cache("get_note")
                invalidate_cache("list_notes")
                invalidate_cache("list_action_items")
            return success
        except Exception as e:
            raise DatabaseError("delete note", str(e))
    
    # Action item operations with caching
    @cached_query(ttl=30)  # Cache for 30 seconds
    def get_action_item(self, action_item_id: int) -> Optional[sqlite3.Row]:
        """Get an action item by ID with caching."""
        return self.action_item_repo.get_by_id(action_item_id)
    
    @cached_query(ttl=30)  # Cache for 30 seconds
    def list_action_items(self, note_id: Optional[int] = None, limit: Optional[int] = None, offset: int = 0) -> List[sqlite3.Row]:
        """List action items with optional filtering and caching."""
        return self.action_item_repo.list_all(note_id=note_id, limit=limit, offset=offset)
    
    def create_action_item(self, text: str, note_id: Optional[int] = None) -> int:
        """Create a new action item and invalidate caches."""
        action_item_id = self.action_item_repo.create(text, note_id)
        invalidate_cache("list_action_items")
        return action_item_id
    
    def create_action_items_batch(self, items: List[str], note_id: Optional[int] = None) -> List[int]:
        """Create multiple action items in a single transaction."""
        items_with_note = [(text, note_id) for text in items]
        ids = self.action_item_repo.create_batch(items_with_note)
        invalidate_cache("list_action_items")
        return ids
    
    def update_action_item_status(self, action_item_id: int, done: bool) -> bool:
        """Update an action item's done status and invalidate caches."""
        success = self.action_item_repo.update_status(action_item_id, done)
        if success:
            invalidate_cache("list_action_items")
        return success
    
    def delete_action_item(self, action_item_id: int) -> bool:
        """Delete an action item and invalidate caches."""
        success = self.action_item_repo.delete(action_item_id)
        if success:
            invalidate_cache("list_action_items")
        return success
    
    # Batch operations for better performance
    def create_note_with_action_items(self, content: str, action_items: List[str]) -> tuple[int, List[int]]:
        """Create a note and its action items in a single transaction."""
        try:
            with get_pool().get_connection() as connection:
                cursor = connection.cursor()
                
                # Create note
                cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
                note_id = cursor.lastrowid
                
                # Create action items
                action_item_ids = []
                for item in action_items:
                    cursor.execute(
                        "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                        (note_id, item)
                    )
                    action_item_ids.append(cursor.lastrowid)
                
                connection.commit()
                
                # Invalidate caches
                invalidate_cache("list_notes")
                invalidate_cache("list_action_items")
                
                return note_id, action_item_ids
        except Exception as e:
            raise DatabaseError("create note with action items", str(e))
    
    # Statistics and monitoring
    def get_stats(self) -> dict:
        """Get database statistics."""
        try:
            from .schema import get_database_stats
            from .cache import get_cache_stats
            
            return {
                'database': get_database_stats(),
                'cache': get_cache_stats()
            }
        except Exception as e:
            raise DatabaseError("get stats", str(e))
    
    def optimize_database(self) -> None:
        """Run database optimization."""
        try:
            from .schema import optimize_database
            optimize_database()
        except Exception as e:
            raise DatabaseError("optimize database", str(e))


# Global optimized database instance
optimized_db = OptimizedDatabase()
