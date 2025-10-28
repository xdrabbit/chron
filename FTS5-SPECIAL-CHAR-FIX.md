# FTS5 Special Character Fix

**Issue**: FTS5 syntax error when questions contain special characters like `?`

## The Problem

When users ask questions like:
- "were there any test transcriptions**?**"
- "what meetings did I have**?**"

FTS5 would throw: `fts5: syntax error near "?"`

Additionally, when Ollama extracted keywords without operators (e.g., just "test transcription"), FTS5 would interpret "test" as a column name, causing: `no such column: test`

## The Fix

### 1. Clean Special Characters in Keyword Extraction

**File**: `backend/services/ollama_service.py`

**Changed**: Added regex cleaning to remove FTS5-incompatible characters:

```python
import re
# Remove special chars that break FTS5: ? ! @ # $ % ^ & * ( ) [ ] { } < > / \ | ~ ` ; :
keywords = re.sub(r'[?!@#$%^&*()\[\]{}<>/\\|~`;:,.]', ' ', keywords)
keywords = re.sub(r'\s+', ' ', keywords).strip()  # Collapse spaces
```

**Applied to**:
- Successful keyword extraction results
- Fallback to original question
- Exception handling fallback

### 2. Sanitize FTS5 Queries

**File**: `backend/db/fts.py`

**Changed**: Convert bare words to OR searches to prevent column name interpretation:

```python
def search_events(query: str, limit: int = 50):
    # Check for UPPERCASE operators (case-sensitive!)
    has_operators = any(op in query for op in [' AND ', ' OR ', ' NOT '])
    
    # If no operators found, convert to OR search
    if query and not has_operators:
        words = query.split()
        if len(words) > 1:
            query = ' OR '.join(words)  # "test transcription" → "test OR transcription"
```

**Why this works**:
- FTS5 interprets `test` alone as a column reference
- `test OR transcription` is correctly parsed as a search query
- **Case-sensitive check**: Only looks for UPPERCASE operators
- Preserves text like "or" in phrases without treating it as an operator

## Examples

### Before
```
User: "were there any test transcriptions?"
Keywords extracted: "test transcription"
FTS5: ERROR - no such column: test
```

### After
```
User: "were there any test transcriptions?"
Keywords extracted: "test transcription"  (? removed)
FTS5 query: "test OR transcription"  (auto-converted)
Result: ✅ Success - found 3 events
```

## Testing

```bash
# Test with question mark
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "were there any test transcriptions?", "timeline": "Default"}'

# Should now work without FTS5 syntax errors
```

## Special Characters Removed

The following characters are now stripped from FTS5 queries:
- `?` `!` - Question/exclamation marks
- `@` `#` `$` `%` - Symbols
- `^` `&` `*` - Operators
- `(` `)` `[` `]` `{` `}` - Brackets
- `<` `>` `/` `\` `|` - Angle brackets, slashes
- `~` `` ` `` `;` `:` `,` `.` - Other punctuation

## Operators Preserved

These FTS5 operators are intentionally preserved when extracted by Ollama:
- `AND` - Both terms must appear
- `OR` - Either term appears
- `NOT` - Exclude term

## Files Modified

1. `backend/services/ollama_service.py` - Clean extracted keywords
2. `backend/db/fts.py` - Sanitize FTS5 queries with OR conversion

---

*Fixed: October 15, 2025*  
*Issue: FTS5 syntax errors from special characters*  
*Solution: Regex cleaning + OR query conversion*
