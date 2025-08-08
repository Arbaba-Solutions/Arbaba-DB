from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Entry:
    """Represents a database entry."""
    id: Optional[uuid.UUID] = None
    title: str = ""
    content: str = ""
    entry_type: str = "note"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str = "user"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Tag:
    """Represents a tag."""
    id: Optional[uuid.UUID] = None
    name: str = ""
    usage_count: int = 0


class EntryRepository:
    """Handles all database operations for entries."""
    
    def __init__(self, get_connection_func):
        self.get_connection = get_connection_func
    
    def create_entry(self, entry: Entry) -> uuid.UUID:
        """Create a new entry in the database."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Insert the entry
            cur.execute("""
                INSERT INTO entries (title, content, type, created_by)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (entry.title, entry.content, entry.entry_type, entry.created_by))
            
            entry_id = cur.fetchone()[0]
            
            # Handle tags if provided
            if entry.tags:
                self._add_tags_to_entry(cur, entry_id, entry.tags)
            
            conn.commit()
            return entry_id
            
        finally:
            cur.close()
            conn.close()
    
    def get_entries(self, tag: Optional[str] = None, entry_type: Optional[str] = None, 
                   limit: int = 20) -> List[Entry]:
        """Get entries with optional filtering."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Build query based on filters
            base_query = """
                SELECT DISTINCT e.id, e.title, e.content, e.type, e.created_at, e.updated_at, e.created_by
                FROM entries e
            """
            
            conditions = []
            params = []
            
            if tag:
                base_query += """
                    LEFT JOIN entry_tags et ON e.id = et.entry_id
                    LEFT JOIN tags t ON et.tag_id = t.id
                """
                conditions.append("t.name = %s")
                params.append(tag)
            
            if entry_type:
                conditions.append("e.type = %s")
                params.append(entry_type)
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY e.created_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(base_query, params)
            rows = cur.fetchall()
            
            entries = []
            for row in rows:
                entry_id, title, content, etype, created, updated, created_by = row
                # Get tags for this entry
                tags = self._get_entry_tags(cur, entry_id)
                
                entry = Entry(
                    id=entry_id,
                    title=title,
                    content=content,
                    entry_type=etype,
                    created_at=created,
                    updated_at=updated,
                    created_by=created_by,
                    tags=tags
                )
                entries.append(entry)
            
            return entries
            
        finally:
            cur.close()
            conn.close()
    
    def search_entries(self, query: str, in_title: bool = True, 
                      in_content: bool = True) -> List[Entry]:
        """Search entries by title or content."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            conditions = []
            search_term = f"%{query}%"
            
            if in_title:
                conditions.append("title ILIKE %s")
            if in_content:
                conditions.append("content ILIKE %s")
            
            if not conditions:
                return []
            
            where_clause = " OR ".join(conditions)
            params = [search_term] * len(conditions)
            
            cur.execute(f"""
                SELECT id, title, content, type, created_at, updated_at, created_by
                FROM entries 
                WHERE {where_clause}
                ORDER BY created_at DESC
            """, params)
            
            rows = cur.fetchall()
            
            entries = []
            for row in rows:
                entry_id, title, content, etype, created, updated, created_by = row
                tags = self._get_entry_tags(cur, entry_id)
                
                entry = Entry(
                    id=entry_id,
                    title=title,
                    content=content,
                    entry_type=etype,
                    created_at=created,
                    updated_at=updated,
                    created_by=created_by,
                    tags=tags
                )
                entries.append(entry)
            
            return entries
            
        finally:
            cur.close()
            conn.close()
    
    def get_entry_by_title(self, title: str) -> Optional[Entry]:
        """Get a specific entry by title."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT id, title, content, type, created_at, updated_at, created_by
                FROM entries 
                WHERE title ILIKE %s
            """, (f"%{title}%",))
            
            row = cur.fetchone()
            if not row:
                return None
            
            entry_id, title, content, etype, created, updated, created_by = row
            tags = self._get_entry_tags(cur, entry_id)
            
            return Entry(
                id=entry_id,
                title=title,
                content=content,
                entry_type=etype,
                created_at=created,
                updated_at=updated,
                created_by=created_by,
                tags=tags
            )
            
        finally:
            cur.close()
            conn.close()
    
    def get_all_tags(self) -> List[Tag]:
        """Get all tags with their usage counts."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT t.id, t.name, COUNT(et.entry_id) as usage_count
                FROM tags t
                LEFT JOIN entry_tags et ON t.id = et.tag_id
                GROUP BY t.id, t.name
                ORDER BY usage_count DESC, t.name
            """)
            
            rows = cur.fetchall()
            
            tags = []
            for tag_id, name, count in rows:
                tag = Tag(id=tag_id, name=name, usage_count=count)
                tags.append(tag)
            
            return tags
            
        finally:
            cur.close()
            conn.close()
    
    def _add_tags_to_entry(self, cur, entry_id: uuid.UUID, tag_names: List[str]):
        """Helper method to add tags to an entry."""
        for tag_name in tag_names:
            # Insert or get tag
            cur.execute("""
                INSERT INTO tags (name) VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (tag_name,))
            
            result = cur.fetchone()
            if result:
                tag_id = result[0]
            else:
                # Tag already exists, get its ID
                cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
                tag_id = cur.fetchone()[0]
            
            # Link entry to tag
            cur.execute("""
                INSERT INTO entry_tags (entry_id, tag_id) VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (entry_id, tag_id))
    
    def _get_entry_tags(self, cur, entry_id: uuid.UUID) -> List[str]:
        """Helper method to get tags for an entry."""
        cur.execute("""
            SELECT t.name
            FROM tags t
            JOIN entry_tags et ON t.id = et.tag_id
            WHERE et.entry_id = %s
        """, (entry_id,))
        
        return [row[0] for row in cur.fetchall()]