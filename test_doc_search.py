#!/usr/bin/env python3
"""
Quick test script to upload deployment markdown files and verify search functionality
"""

import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_document_upload():
    """Upload DEPLOYMENT files to a test event"""
    
    print("🧪 Testing Document Upload & Search")
    print("=" * 60)
    
    # Step 1: Create a test event
    print("\n1️⃣ Creating test event...")
    event_data = {
        'title': 'Deployment Documentation',
        'description': 'Testing document upload with deployment markdown files',
        'date': '2025-10-23T17:00:00',
        'timeline': 'Testing',
        'actor': 'Tom',
        'tags': 'testing,documents,deployment'
    }
    
    # Find the deployment files
    deployment_md = Path('/home/tom/lnx_mac_int_drv/dev/chron/DEPLOYMENT.md')
    deployment_summary_md = Path('/home/tom/lnx_mac_int_drv/dev/chron/DEPLOYMENT-SUMMARY.md')
    
    # Check if files exist
    if not deployment_md.exists():
        print(f"❌ File not found: {deployment_md}")
        return
    if not deployment_summary_md.exists():
        print(f"❌ File not found: {deployment_summary_md}")
        return
    
    print(f"✅ Found: {deployment_md.name} ({deployment_md.stat().st_size} bytes)")
    print(f"✅ Found: {deployment_summary_md.name} ({deployment_summary_md.stat().st_size} bytes)")
    
    # Prepare files for upload
    files = [
        ('files', (deployment_md.name, open(deployment_md, 'rb'), 'text/markdown')),
        ('files', (deployment_summary_md.name, open(deployment_summary_md, 'rb'), 'text/markdown'))
    ]
    
    # Prepare form data
    form_data = {
        'title': event_data['title'],
        'description': event_data['description'],
        'date': event_data['date'],
        'timeline': event_data['timeline'],
        'actor': event_data['actor'],
        'tags': event_data['tags']
    }
    
    try:
        print("\n2️⃣ Uploading event with documents...")
        response = requests.post(
            f"{BASE_URL}/events/with-attachments",
            data=form_data,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            event = response.json()
            event_id = event['id']
            print(f"✅ Event created: {event['title']}")
            print(f"   Event ID: {event_id}")
            
            # Check attachments in database
            print("\n3️⃣ Verifying documents were stored...")
            import sqlite3
            conn = sqlite3.connect('/home/tom/lnx_mac_int_drv/dev/chron/data/chronicle.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT original_filename, file_size, LENGTH(parsed_content) as content_length 
                FROM attachment 
                WHERE event_id = ?
            """, (event_id,))
            
            attachments = cursor.fetchall()
            if attachments:
                for filename, size, content_len in attachments:
                    print(f"✅ {filename}: {size} bytes, parsed content: {content_len} chars")
            else:
                print("❌ No attachments found in database")
            
            conn.close()
            
            # Test search
            print("\n4️⃣ Testing search for 'deployment'...")
            search_response = requests.get(f"{BASE_URL}/search?q=deployment")
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Search returned {len(results)} results")
                for result in results[:3]:
                    print(f"   - {result['title']}")
            
            print("\n5️⃣ Testing search for 'nfsn'...")
            search_response = requests.get(f"{BASE_URL}/search?q=nfsn")
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Search returned {len(results)} results")
                for result in results[:3]:
                    print(f"   - {result['title']}")
            
            print("\n6️⃣ Testing search for 'ritualstack'...")
            search_response = requests.get(f"{BASE_URL}/search?q=ritualstack")
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Search returned {len(results)} results")
                for result in results[:3]:
                    print(f"   - {result['title']}")
            
            print("\n✅ Test completed successfully!")
            return event_id
            
        else:
            print(f"❌ Error creating event: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_document_upload()