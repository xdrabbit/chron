#!/usr/bin/env python3
"""
Test datetime parsing issue
"""

from datetime import datetime

# Test the actual datetime strings from database
test_strings = [
    '2025-10-02T09:00:00',
    '2025-10-06T09:30:00', 
    '2025-10-10T17:17:00'
]

print("Testing datetime parsing:")
for date_str in test_strings:
    try:
        dt = datetime.fromisoformat(date_str)
        print(f"✅ {date_str} -> {dt}")
    except Exception as e:
        print(f"❌ {date_str} -> Error: {e}")
        
        # Try alternative parsing
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            print(f"✅ {date_str} -> {dt} (with strptime)")
        except Exception as e2:
            print(f"❌ {date_str} -> strptime error: {e2}")