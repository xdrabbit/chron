#!/usr/bin/env python3
"""
Database migration script to add legal workflow fields to existing Chronicle databases.

Adds:
- actor: Who was responsible (Tom, Lisa, Realtor, Court, etc.)
- evidence_links: URLs or file paths to supporting evidence
- privileged_notes: Attorney work product (not exported to PDF)
"""

import sqlite3
from pathlib import Path

def get_db_path():
    """Get the path to the Chronicle database"""
    return Path(__file__).parent / "data" / "chronicle.db"

def migrate_database():
    """Add new legal workflow fields to existing database"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("No migration needed - database will be created with new schema.")
        return
    
    print(f"Migrating database at {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(event)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add actor column if it doesn't exist
        if 'actor' not in columns:
            print("Adding 'actor' column...")
            cursor.execute("ALTER TABLE event ADD COLUMN actor TEXT")
        else:
            print("'actor' column already exists")
        
        # Add evidence_links column if it doesn't exist
        if 'evidence_links' not in columns:
            print("Adding 'evidence_links' column...")
            cursor.execute("ALTER TABLE event ADD COLUMN evidence_links TEXT")
        else:
            print("'evidence_links' column already exists")
        
        # Add privileged_notes column if it doesn't exist
        if 'privileged_notes' not in columns:
            print("Adding 'privileged_notes' column...")
            cursor.execute("ALTER TABLE event ADD COLUMN privileged_notes TEXT")
        else:
            print("'privileged_notes' column already exists")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Update FTS5 index if it exists
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_fts'")
            if cursor.fetchone():
                print("Rebuilding FTS5 index...")
                cursor.execute("DELETE FROM event_fts")
                cursor.execute("""
                    INSERT INTO event_fts (event_id, title, description, tags, timeline)
                    SELECT id, title, description, COALESCE(tags, ''), COALESCE(timeline, '')
                    FROM event
                """)
                conn.commit()
                print("✅ FTS5 index rebuilt")
        except Exception as e:
            print(f"Note: Could not update FTS5 index: {e}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()