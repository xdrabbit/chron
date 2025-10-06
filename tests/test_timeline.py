"""Tests for Timeline class."""

import pytest
import os
import tempfile
from chron.timeline import Timeline


class TestTimeline:
    """Test cases for Timeline class."""
    
    def test_timeline_creation(self):
        """Test basic timeline creation."""
        timeline = Timeline()
        assert timeline.events == []
        assert timeline.theme == "default"
    
    def test_timeline_with_events(self):
        """Test timeline creation with events."""
        events = [
            {"date": "2024-01-01", "event": "Test Event", "description": "Test"}
        ]
        timeline = Timeline(events)
        assert len(timeline.events) == 1
        assert timeline.events[0]["event"] == "Test Event"
    
    def test_set_range(self):
        """Test setting date range."""
        timeline = Timeline()
        timeline.set_range("2024-01-01", "2024-12-31")
        assert timeline.start_date == "2024-01-01"
        assert timeline.end_date == "2024-12-31"
    
    def test_set_theme(self):
        """Test setting theme."""
        timeline = Timeline()
        timeline.set_theme("modern")
        assert timeline.theme == "modern"
    
    def test_render_html(self):
        """Test HTML rendering."""
        events = [
            {"date": "2024-01-01", "event": "Test Event", "description": "Test Description"}
        ]
        timeline = Timeline(events)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
            output_path = f.name
        
        try:
            timeline.render(output_path)
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert "Test Event" in content
                assert "2024-01-01" in content
                assert "Test Description" in content
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
