#!/usr/bin/env python3
"""
Test script to verify document upload functionality
"""

import requests
import json
from pathlib import Path

# Test server URL
BASE_URL = "http://localhost:8000"

def test_create_event_with_documents():
    """Test creating an event with document attachments"""
    
    # Test data
    event_data = {
        'title': 'Test Event with Documents',
        'description': 'Testing document upload functionality',
        'date': '2025-10-21T12:00:00',
        'timeline': 'Testing',
        'actor': 'Brody',
        'tags': 'testing, documents'
    }
    
    # Test documents
    test_md_content = """# Test Legal Document
## Case Information
This is a test document to verify the document parsing functionality.
Key points: evidence, timeline, legal workflow.
"""
    
    test_txt_content = """Test document content
Legal case notes
Document parsing test
Search functionality validation"""
    
    # Prepare files for upload
    files = [
        ('files', ('test_document.md', test_md_content, 'text/markdown')),
        ('files', ('test_notes.txt', test_txt_content, 'text/plain'))
    ]
    
    # Prepare form data
    form_data = {}
    for key, value in event_data.items():
        form_data[key] = (None, value)
    
    try:
        print("Testing document upload endpoint...")
        response = requests.post(
            f"{BASE_URL}/events/with-attachments",
            data=form_data,
            files=files
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            event = response.json()
            print(f"✅ Event created successfully: {event['title']}")
            print(f"Event ID: {event['id']}")
            return event['id']
        else:
            print(f"❌ Error creating event: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_search_documents():
    """Test searching across document content"""
    
    try:
        print("\nTesting document search...")
        response = requests.get(f"{BASE_URL}/search?q=legal")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful, found {len(results)} results")
            for result in results:
                print(f"  - {result['title']}")
        else:
            print(f"❌ Search error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Search exception: {e}")

if __name__ == "__main__":
    print("🧪 Testing Chronicle Document Upload Functionality")
    print("=" * 50)
    
    # Test document upload
    event_id = test_create_event_with_documents()
    
    # Test search
    if event_id:
        test_search_documents()
    
    print("\n✅ Test completed!")