#!/usr/bin/env python3
"""
Simple test to verify core Chronicle functionality works
"""

import sys
import os
sys.path.append('/home/tom/lnx_mac_int_drv/dev/chron/backend')

from sqlmodel import Session, select
from db.base import engine
from models import Event

def test_basic_database():
    """Test basic database operations"""
    print("🧪 Testing basic Chronicle database functionality")
    print("=" * 50)
    
    try:
        # Test database connection
        with Session(engine) as session:
            # Count events
            statement = select(Event)
            events = session.exec(statement).all()
            print(f"✅ Database connection: OK")
            print(f"✅ Current events in database: {len(events)}")
            
            # Show first few events
            for i, event in enumerate(events[:3]):
                print(f"  {i+1}. {event.title} ({event.timeline})")
            
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_database()
    if success:
        print("\n✅ Core database functionality is working!")
    else:
        print("\n❌ Core database functionality has issues.")
        sys.exit(1)