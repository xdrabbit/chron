# Document Management Feature - Development Roadmap

**Created:** October 22, 2025  
**Feature:** Complete document attachment and viewing system for Chronicle  
**Goal:** Enable attorneys to attach any document to timeline events and access them instantly

---

## 🎯 Vision

**"Everything in a timeline, click to view or search"**

Attorneys should be able to:
1. Attach court pleadings, emails (PDF), transcripts, evidence to timeline events
2. Click any document to open in native app (PDF reader, Word, etc.)
3. Search across ALL content (events + documents + audio transcripts)
4. See at a glance which events have attachments

---

## 🏗️ Architecture (Current State)

### **Backend (Already Complete ✅)**

```
SQLite Database (chronicle.db)
├─ event table (33 events)
│   ├─ id, title, date, description, timeline, actor, tags
│   └─ audio_file, transcription_words
└─ attachment table (5 attachments)
    ├─ id, event_id, file_path, file_type
    ├─ original_filename, parsed_content
    └─ page_count, word_count

File System (backend/uploads/)
├─ documents/
│   ├─ {uuid}.pdf (actual PDF files)
│   ├─ {uuid}.docx (actual Word docs)
│   └─ {uuid}.txt (text files)
└─ {uuid}.mp3 (audio files)

FTS5 Search Index (event_fts)
├─ Events (title, description, tags)
├─ Audio transcripts (word-level)
└─ Documents (parsed content with page numbers)
```

### **Backend API Endpoints (Already Working ✅)**

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/events/{id}/documents` | POST | Upload document | ✅ Works |
| `/events/{id}/documents` | GET | List documents | ✅ Works |
| `/documents/{id}` | GET | Download document | ✅ Works |
| `/documents/{id}` | DELETE | Delete document | ✅ Works |
| `/search?q=...` | GET | Search events + docs | ✅ Works |

**Supported formats:** PDF, DOCX, Markdown, TXT  
**Document parsing:** Automatic text extraction for search  
**File storage:** Filesystem (not in DB - scales infinitely)

---

## 🚧 What Needs to Be Built (Frontend Only)

### **Phase 1: Display Existing Documents** 
*Show what's already there*

#### **1.1 EventCard - Document List**
- [ ] Show attached documents in EventCard
- [ ] Display file icon based on type (📄 PDF, 📝 Word, 📋 Text)
- [ ] Show filename and metadata (pages, size)
- [ ] Download/View button for each document
- [ ] Expandable section (collapsed by default)

**Location:** `frontend/src/components/EventCard.jsx`

**Design:**
```jsx
<EventCard>
  <h3>Event Title</h3>
  <p>Description...</p>
  
  {/* NEW: Document Section */}
  {event.attachments?.length > 0 && (
    <div className="documents-section">
      <button onClick={() => setShowDocs(!showDocs)}>
        📎 {event.attachments.length} Document(s)
      </button>
      
      {showDocs && (
        <div className="document-list">
          {event.attachments.map(doc => (
            <div className="document-item">
              📄 {doc.original_filename}
              <span className="doc-meta">{doc.page_count} pages</span>
              <button onClick={() => downloadDocument(doc.id)}>
                View/Download
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )}
</EventCard>
```

#### **1.2 EventCard - Document Badge**
- [ ] Show badge if event has documents (like audio badge)
- [ ] Click badge to expand document list

**Example:**
```jsx
{event.attachments?.length > 0 && (
  <span className="badge document-badge">
    📎 {event.attachments.length}
  </span>
)}
```

---

### **Phase 2: Upload Documents**
*Let users attach files*

#### **2.1 EventForm - File Upload Field**
- [ ] Add file input field to EventForm
- [ ] Multiple file selection support
- [ ] Show selected files before upload
- [ ] Remove file from selection
- [ ] Upload files when event is created/updated

**Location:** `frontend/src/components/EventForm.jsx`

**Design:**
```jsx
<EventForm>
  {/* Existing fields: title, date, description, etc. */}
  
  {/* NEW: Document Upload */}
  <div className="form-group">
    <label>Attach Documents</label>
    <input 
      type="file" 
      multiple 
      accept=".pdf,.docx,.md,.txt"
      onChange={handleFileSelect}
    />
    
    {/* Show selected files */}
    {selectedFiles.length > 0 && (
      <div className="selected-files">
        {selectedFiles.map(file => (
          <div className="file-item">
            📄 {file.name} ({formatFileSize(file.size)})
            <button onClick={() => removeFile(file)}>✕</button>
          </div>
        ))}
      </div>
    )}
  </div>
</EventForm>
```

#### **2.2 Drag & Drop Support**
- [ ] Add drag-over visual feedback
- [ ] Handle file drop events
- [ ] Validate file types
- [ ] Show upload progress

**Enhancement:**
```jsx
<div 
  className={`drop-zone ${isDragging ? 'dragging' : ''}`}
  onDragOver={handleDragOver}
  onDrop={handleDrop}
>
  <p>Drag files here or click to browse</p>
  <input type="file" multiple hidden ref={fileInputRef} />
</div>
```

---

### **Phase 3: Enhanced Search Results**
*Show documents in search*

#### **3.1 SearchPanel - Document Results**
- [ ] Show document type icon in search results
- [ ] Display which document contains the match
- [ ] Show page number where match was found
- [ ] Click to download document

**Location:** `frontend/src/components/SearchPanel.jsx`

**Current behavior:** Search already finds documents (backend indexes them)  
**What's missing:** UI doesn't show document-specific info

**Enhancement:**
```jsx
<SearchResult>
  {result.event.attachments?.map(doc => (
    <div className="document-match">
      📄 Found in: {doc.original_filename}
      <span className="page-info">Page {doc.page_count}</span>
      <button onClick={() => downloadDocument(doc.id)}>
        View Document
      </button>
    </div>
  ))}
</SearchResult>
```

---

### **Phase 4: Document Viewer (Optional Enhancement)**

#### **4.1 Inline Document Preview**
- [ ] PDF preview in modal (using PDF.js or similar)
- [ ] Text file preview in modal
- [ ] Download button in preview modal

**This is optional - may be better to just download and open in native app**

---

## 📋 Implementation Checklist

### **Step 1: Display Documents (60 min)**
- [ ] Update EventCard to fetch attachments from event object
- [ ] Create document list component
- [ ] Add download handler (GET /documents/{id})
- [ ] Add document badge to event metadata
- [ ] Style document list with file type icons
- [ ] Test with existing documents in database

### **Step 2: Upload Documents (90 min)**
- [ ] Add file input to EventForm
- [ ] Create multipart form data handler
- [ ] Update event creation to POST /events/{id}/documents
- [ ] Add file validation (type, size)
- [ ] Show upload progress
- [ ] Handle upload errors
- [ ] Test upload flow end-to-end

### **Step 3: Drag & Drop (30 min)**
- [ ] Add drag event handlers
- [ ] Visual feedback for drag-over
- [ ] File drop handler
- [ ] Test drag-drop with various file types

### **Step 4: Search Enhancement (45 min)**
- [ ] Update SearchPanel to show document matches
- [ ] Add document metadata to search results
- [ ] Style document-specific results
- [ ] Add download links in search results
- [ ] Test search with documents

### **Step 5: Testing & Polish (30 min)**
- [ ] Test upload with all supported file types
- [ ] Test download in different browsers
- [ ] Test search finds document content
- [ ] Add loading states
- [ ] Add error messages
- [ ] Update smoke tests

---

## 🎨 UI Design Principles

### **File Type Icons**
```
📄 .pdf  → PDF document
📝 .docx → Word document  
📋 .txt  → Text file
📑 .md   → Markdown
```

### **Color Coding**
```css
.document-badge { 
  bg: emerald-900/30, 
  text: emerald-300 
}
.audio-badge { 
  bg: purple-900/30, 
  text: purple-300 
}
```

### **Interaction Pattern**
1. **Collapsed by default** - Show badge with count
2. **Click badge** - Expand to show document list
3. **Click document** - Download and open in native app
4. **Hover** - Show filename and metadata

---

## 🔍 Search Behavior

### **How It Works Now (Backend):**
1. User uploads PDF to event
2. Backend parses PDF text content
3. Content indexed in FTS5 as `doc_{attachment.id}`
4. Search query searches both events and documents
5. Results include both event matches and document matches

### **What We're Adding (Frontend):**
- Show "Found in document: filename.pdf" in results
- Download link for matching documents
- Visual distinction between event matches and document matches

---

## 🧪 Testing Strategy

### **Manual Testing:**
1. Upload PDF to existing event → Verify shows in EventCard
2. Click download → Verify opens in PDF reader
3. Upload DOCX → Verify shows correctly
4. Search for text in document → Verify finds it
5. Create new event with document → Verify upload works
6. Delete document → Verify removes from event

### **Automated Testing (Add to test_smoke.py):**
- [x] Upload document to event (already tested)
- [x] Get event documents (already tested)
- [x] Search finds document content (already tested)
- [ ] Download document returns correct MIME type
- [ ] Delete document removes from filesystem

---

## 🚀 Launch Criteria

### **Minimum Viable:**
- ✅ View documents attached to events
- ✅ Download documents (opens in native app)
- ✅ Upload documents when creating events
- ✅ Search finds text in documents

### **Nice to Have:**
- Drag & drop upload
- Upload progress indicator
- Document preview modal
- Bulk document operations

---

## 📊 Technical Considerations

### **File Size Limits:**
- **Current:** No explicit limit (FastAPI default: 16MB)
- **Recommendation:** Set max 50MB per file
- **Large files:** Court transcripts can be 20-30MB
- **Solution:** If needed, increase limit in FastAPI config

### **Storage:**
- **Current:** Filesystem (backend/uploads/documents/)
- **Scalability:** Unlimited (filesystem scales to TB)
- **Backup:** Files are separate from DB (easy to backup)

### **Performance:**
- **FTS5:** Handles millions of documents
- **Current:** 5 attachments, instant search
- **Expected:** Thousands of documents, still fast
- **Optimization:** Already using FTS5 prefix matching

### **Security:**
- **Path validation:** Backend validates file paths
- **UUID filenames:** Prevents path traversal
- **MIME type validation:** Backend checks file types
- **TODO:** Add user-level access control (multi-user support)

---

## 🎯 Success Metrics

### **User Workflow:**
```
Timeline: "Smith vs. Jones Case"
├─ Event: "Initial Filing" (Jan 15)
│   └─ 📄 complaint.pdf (15 pages) ← Click → Opens in Acrobat
├─ Event: "Discovery Request" (Feb 3)
│   └─ 📄 discovery_motion.docx ← Click → Opens in Word
├─ Event: "Deposition" (Mar 10)
│   ├─ 🎤 Audio transcript (click to play)
│   └─ 📄 deposition_transcript.pdf (120 pages)
└─ Event: "Settlement Meeting" (Apr 5)
    └─ 📋 meeting_notes.txt

Search: "objection"
Results:
  ✅ Deposition (audio) → Jump to 15:30
  ✅ Deposition transcript (PDF) → Page 45
  ✅ Discovery motion (Word) → Found 3 times
```

### **Value Proposition:**
- **Before:** Files scattered across email, folders, cloud drives
- **After:** All documents tied to timeline events, instantly searchable
- **Impact:** Hours saved per case in document retrieval

---

## 🔄 Future Enhancements (Post-Launch)

1. **AI Document Summaries** (using Ollama)
   - Summarize long documents
   - Extract key dates and entities
   - Link related documents

2. **OCR Support**
   - Scan physical documents
   - Extract text from images
   - Searchable scanned PDFs

3. **Version Control**
   - Track document revisions
   - Show change history
   - Compare versions

4. **Collaboration**
   - Share documents with team
   - Comments and annotations
   - Access control per document

5. **Email Integration**
   - Import emails as events
   - Extract attachments automatically
   - Link email threads

---

## 📝 Notes & Decisions

### **Why Not Store Files in SQLite?**
- Files can be large (50MB+)
- Filesystem is faster for large files
- Easier to backup separately
- Standard practice for document management

### **Why Not Use Cloud Storage?**
- Want local-first architecture
- No internet dependency
- Attorney-client privilege (local only)
- Can add cloud sync later as option

### **Why Separate Documents from Audio?**
- Audio has word-level timestamps (seekable)
- Documents are static (download and read)
- Different UI patterns
- Both searchable via FTS5

---

## 🎬 Implementation Order

1. **Display Phase** (Get documents showing in UI)
2. **Upload Phase** (Let users add documents)
3. **Search Phase** (Show document matches clearly)
4. **Polish Phase** (Drag-drop, progress, error handling)

**Estimated Total Time:** 3-4 hours of focused development

---

**Ready to build!** 🚀

This document is our north star - if we get lost, we come back here.
