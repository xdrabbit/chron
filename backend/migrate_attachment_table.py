#!/usr/bin/env python3
"""
Migration script to add new columns to the attachment table for document parsing support.
"""

import sqlite3
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "data" / "chronicle.db"

def migrate_attachment_table():
    """Add new columns to attachment table for document parsing"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(attachment)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current attachment columns: {columns}")
    
    # Add missing columns if they don't exist
    new_columns = [
        ("original_filename", "VARCHAR"),
        ("parsed_content", "TEXT"),
        ("page_count", "INTEGER"),
        ("word_count", "INTEGER"),
        ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for column_name, column_type in new_columns:
        if column_name not in columns:
            try:
                sql = f"ALTER TABLE attachment ADD COLUMN {column_name} {column_type}"
                print(f"Executing: {sql}")
                cursor.execute(sql)
                print(f"✅ Added column: {column_name}")
            except sqlite3.Error as e:
                print(f"❌ Error adding column {column_name}: {e}")
        else:
            print(f"✅ Column {column_name} already exists")
    
    # Commit changes
    conn.commit()
    
    # Verify new schema
    cursor.execute("PRAGMA table_info(attachment)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Updated attachment columns: {columns}")
    
    conn.close()
    print("✅ Migration completed!")

if __name__ == "__main__":
    migrate_attachment_table()