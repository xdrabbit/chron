"""
Full-text search setup using SQLite FTS5.
This module handles creating and managing the FTS5 virtual table for searching event transcriptions.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_db_path() -> Path:
    """Get the path to the SQLite database"""
    return Path(__file__).parent.parent.parent / "data" / "chronicle.db"

def create_fts_table():
    """
    Create the FTS5 virtual table for full-text search on events.
    This should be called on startup to ensure the FTS table exists.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Create FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS event_fts USING fts5(
                event_id UNINDEXED,
                title,
                description,
                tags,
                timeline,
                tokenize='porter unicode61'
            )
        """)
        
        conn.commit()
        logger.info("FTS5 table created successfully")
        
    except Exception as e:
        logger.error(f"Error creating FTS5 table: {e}")
        raise
    finally:
        conn.close()

def index_event(event_id: str, title: str, description: str, tags: str = None, timeline: str = None):
    """
    Add or update an event in the FTS index.
    
    Args:
        event_id: UUID of the event
        title: Event title
        description: Event description/transcription
        tags: Comma-separated tags
        timeline: Timeline name
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Delete existing entry if it exists
        cursor.execute("DELETE FROM event_fts WHERE event_id = ?", (event_id,))
        
        # Insert new entry
        cursor.execute("""
            INSERT INTO event_fts (event_id, title, description, tags, timeline)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, title, description, tags or "", timeline or ""))
        
        conn.commit()
        logger.debug(f"Indexed event {event_id}")
        
    except Exception as e:
        logger.error(f"Error indexing event {event_id}: {e}")
        raise
    finally:
        conn.close()

def remove_from_index(event_id: str):
    """Remove an event from the FTS index"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM event_fts WHERE event_id = ?", (event_id,))
        conn.commit()
        logger.debug(f"Removed event {event_id} from index")
    except Exception as e:
        logger.error(f"Error removing event {event_id} from index: {e}")
        raise
    finally:
        conn.close()

def search_events(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search events using FTS5.
    
    Args:
        query: Search query (supports AND, OR, NOT, phrase searches with quotes, etc.)
        limit: Maximum number of results
    
    Returns:
        List of dicts with event_id, title, description snippet with highlights
    
    Example queries:
        - "town council" - phrase search
        - "ordinance AND 2020" - both terms must appear
        - "meeting OR hearing" - either term
        - "daniel NOT subdivision" - exclude subdivision
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Sanitize FTS5 query - only add OR operators if none exist
        # Check for uppercase operators to distinguish from regular words
        has_operators = any(op in query for op in [' AND ', ' OR ', ' NOT '])
        
        if query and not has_operators:
            # No operators found - convert to OR search
            # This prevents FTS5 from treating words as column names
            words = query.split()
            if len(words) > 1:
                query = ' OR '.join(words)
                logger.debug(f"Converted query to OR search: {query}")
        
        # FTS5 query with snippet highlighting
        cursor.execute("""
            SELECT 
                event_id,
                title,
                snippet(event_fts, 1, '<mark>', '</mark>', '...', 50) as title_snippet,
                snippet(event_fts, 2, '<mark>', '</mark>', '...', 100) as description_snippet,
                rank
            FROM event_fts
            WHERE event_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "event_id": row[0],
                "title": row[1],
                "title_snippet": row[2],
                "description_snippet": row[3],
                "rank": row[4]
            })
        
        logger.info(f"Found {len(results)} results for query: {query}")
        return results
        
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        raise
    finally:
        conn.close()

def rebuild_index():
    """
    Rebuild the entire FTS index from scratch.
    This should be called if the index gets out of sync.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Clear existing FTS data
        cursor.execute("DELETE FROM event_fts")
        
        # Reindex all events
        cursor.execute("""
            INSERT INTO event_fts (event_id, title, description, tags, timeline)
            SELECT id, title, description, COALESCE(tags, ''), COALESCE(timeline, '')
            FROM event
        """)
        
        conn.commit()
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM event_fts")
        count = cursor.fetchone()[0]
        
        logger.info(f"Rebuilt FTS index with {count} events")
        return count
        
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise
    finally:
        conn.close()
