"""Tests for EventParser class."""

import pytest
import os
import tempfile
import json
from chron.parser import EventParser


class TestEventParser:
    """Test cases for EventParser class."""
    
    def test_parse_csv(self):
        """Test CSV parsing."""
        parser = EventParser()
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("date,event,description\n")
            f.write("2024-01-01,Event 1,Description 1\n")
            f.write("2024-02-01,Event 2,Description 2\n")
            csv_path = f.name
        
        try:
            events = parser.parse_csv(csv_path)
            assert len(events) == 2
            assert events[0]['event'] == 'Event 1'
            assert events[1]['date'] == '2024-02-01'
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)
    
    def test_parse_json(self):
        """Test JSON parsing."""
        parser = EventParser()
        
        # Create temporary JSON file
        data = {
            "events": [
                {"date": "2024-01-01", "event": "Event 1", "description": "Description 1"},
                {"date": "2024-02-01", "event": "Event 2", "description": "Description 2"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            json_path = f.name
        
        try:
            events = parser.parse_json(json_path)
            assert len(events) == 2
            assert events[0]['event'] == 'Event 1'
            assert events[1]['description'] == 'Description 2'
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)
