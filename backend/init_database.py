#!/usr/bin/env python3
"""
Initialize a fresh Chronicle database with proper schema
"""

import sys
sys.path.append('/home/tom/lnx_mac_int_drv/dev/chron/backend')

from sqlmodel import SQLModel, create_engine
from pathlib import Path

# Import all models to register them
from models import Event, Participant, Attachment, EventParticipantLink
from db.base import DB_PATH, engine
from db.fts import create_fts_table

def initialize_database():
    """Create fresh database with all tables"""
    print("🗄️  Initializing Chronicle database...")
    print(f"Database location: {DB_PATH}")
    
    # Create all tables
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created")
    
    # Create FTS5 search index
    print("Creating FTS5 search index...")
    create_fts_table()
    print("✅ FTS5 index created")
    
    print("\n✅ Database initialization complete!")
    print(f"Database file: {DB_PATH}")
    print("The database is ready to use.")

if __name__ == "__main__":
    initialize_database()