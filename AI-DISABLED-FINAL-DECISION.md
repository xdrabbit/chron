# AI Features: Final Decision - Disabled

**Date**: October 15-16, 2025  
**Decision**: AI features permanently disabled  
**Reason**: UX unacceptable despite multiple optimization attempts

## What We Tried

### Attempt 1: Connection Pooling & Context Reduction
- Added HTTP connection pooling with requests.Session
- Reduced context window: 2048 → 1024 tokens
- Reduced predictions: 256 → 200 tokens
- **Result**: Still 60-90 second timeout on first request

### Attempt 2: Smart Agent Pattern with FTS5
- Two-stage approach: Extract keywords → FTS5 search → Focused answer
- Minimal prompts (~400 chars instead of 3000+)
- FTS5 as tool pattern (like ChatGPT web search)
- **Result**: Still 60-90 seconds for first request (model loading)

### Attempt 3: Increased Timeouts
- Backend: 30s → 120s
- Frontend: 45s → 150s (2.5 minutes)
- **Result**: Works but UX is terrible - users wait 90 seconds staring at loading spinner

### Attempt 4: FTS5 Query Sanitization
- Strip special characters that break FTS5 (`?!@#$%` etc.)
- Auto-convert bare words to OR searches
- Case-sensitive operator detection
- **Result**: FTS5 works great, but Ollama still slow

## The Fundamental Problem

**Ollama Model Loading**: First API call takes 60-90 seconds to load llama3.2 (2.8GB) into RAM
- This is unavoidable
- Subsequent requests are fast (2-5 seconds) but model unloads after 5 minutes of inactivity
- Users almost always experience the slow first request

**User Experience**:
- User asks simple question: "were there any test transcriptions?"
- Waits 90 seconds staring at spinner
- Sees timeout error or thinks app is broken
- **This is not acceptable UX**

## Why FTS5 is Better

**FTS5 Full-Text Search**:
- **Instant**: <0.1 seconds for any query
- **Always works**: No model loading, no timeouts
- **Powerful**: Boolean operators, phrase search, ranking
- **Sufficient**: Timeline queries are simple fact-finding

**Example**:
```
User types: "test transcriptions"
FTS5 returns: 3 events in 0.05 seconds
User sees: Exact matches with highlighted snippets
```

This is what users actually want - fast, accurate search results.

## AI Value Proposition Failed

**What we thought AI would add**:
- Natural language understanding
- Conversational interface
- Contextual answers
- Pattern synthesis

**Reality**:
- Timeline queries are simple: "find events about X"
- Users just want search results, not conversation
- 90-second wait destroys any UX benefit
- FTS5 snippets provide enough context

## Files Modified to Disable AI

### Backend
1. `backend/main.py` - Commented out ask_router
2. Code remains in `backend/services/ollama_service.py` (for future reference)
3. Code remains in `backend/routes/ask.py` (for future reference)

### Frontend
1. `frontend/src/pages/Home.jsx`:
   - Commented out AskPanel and FloatingAskPanel imports
   - Removed Ask panel section
   - Removed AI button from floating controls
   - Removed state variables for AI panels

2. `frontend/src/pages/ProfessionalDashboard.jsx`:
   - Removed AI button from sidebar

3. `frontend/src/services/api.js`:
   - askTimeline() function remains but unused

## What Remains Active

**Core Features** (All Working Great):
- ✅ Timeline events with dates
- ✅ FTS5 full-text search (instant!)
- ✅ Voice transcription with Whisper GPU
- ✅ Audio attachments
- ✅ Visual timeline with vis-timeline
- ✅ CSV import/export
- ✅ Multiple timelines
- ✅ Floating panels (timeline, search, form)

## Lessons Learned

1. **Fast matters more than smart**: 0.05s "dumb" search beats 90s "smart" AI every time
2. **UX trumps technology**: Cool tech doesn't matter if users hate waiting
3. **Simple problems need simple solutions**: Timeline search doesn't need LLMs
4. **Test early with real latency**: Remote dev exposed the timeout issues
5. **Know when to quit**: We tried 4 different approaches - none solved the core problem

## Could AI Work in the Future?

**Maybe, if:**
1. **Smaller models**: 1B parameter models that load in <5 seconds
2. **Always-on**: Keep model loaded in background (memory intensive)
3. **Async**: Generate answers in background, notify when ready
4. **Different use case**: Summarization, pattern finding (not simple search)
5. **Cloud-hosted**: Ollama on dedicated server (defeats privacy-first goal)

**But for now**: FTS5 is the right tool for the job.

## Final Status

**AI Features**: ❌ Disabled  
**FTS5 Search**: ✅ Active and instant  
**Core Timeline**: ✅ Fully functional  
**Voice Transcription**: ✅ Working  

**Conclusion**: Chronicle is a better product without AI. Focus on what works.

---

*Decision made after 2 days of optimization attempts*  
*Sometimes the best feature is the one you remove*
