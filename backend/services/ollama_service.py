"""
Ollama LLM Service for Conversational Timeline Queries

SMART AGENT PATTERN:
1. Extract search keywords from user question (tiny prompt, ~2 seconds)
2. Use FTS5 to search events (instant, <0.1 seconds)
3. Generate answer from focused snippets (small prompt, ~3-5 seconds)

Total: 5-8 seconds instead of 60+ seconds!

Uses local Ollama instance for privacy-first AI assistance.
FTS5 acts as the "memory" - Ollama just connects the dots.
"""

import os
import requests
import json
import logging
import time
from typing import List, Dict, Optional, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service for interacting with Ollama LLM for conversational timeline queries.
    """
    
    def __init__(self, base_url: str = None, model: str = "llama3.2"):
        """
        Initialize Ollama service.
        
        Args:
            base_url: Ollama API URL (default: checks OLLAMA_URL env var, or uses localhost)
            model: Model to use (default: llama3.2)
        """
        # Prefer environment variable, fallback to localhost (can switch to oasis later)
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", model)
        
        # Create persistent session with connection pooling and keepalive
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with connection pooling and keepalive.
        This significantly reduces latency for remote connections.
        """
        session = requests.Session()
        
        # Configure retry strategy for transient failures
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=0.5
        )
        
        # Mount adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set TCP keepalive in headers
        session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=60, max=100'
        })
        
        return session
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def extract_search_keywords(self, question: str) -> str:
        """
        STAGE 1: Extract search keywords from user question.
        This is a tiny, fast prompt that just identifies what to search for.
        
        Args:
            question: User's natural language question
            
        Returns:
            FTS5-compatible search query string
        """
        try:
            start_time = time.time()
            
            # Minimal prompt for keyword extraction
            prompt = f"""Extract search keywords for a timeline database query.

User question: "{question}"

Return ONLY the search keywords (no explanation). Use AND/OR operators if needed.
Examples:
- "What did Judge Smith say about rezoning?" → "Judge Smith AND rezoning"
- "Were there any test transcriptions?" → "test AND transcription"
- "Show me meetings from last week" → "meeting"

Keywords:"""

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Low temp for focused extraction
                        "num_ctx": 512,      # Small context
                        "num_predict": 30,   # Very short response
                        "num_thread": 8,
                    }
                },
                timeout=120  # First request loads model (60-90s), subsequent are fast
            )
            
            extract_time = time.time() - start_time
            logger.info(f"Keyword extraction time: {extract_time:.3f}s")
            
            if response.status_code == 200:
                result = response.json()
                keywords = result.get("response", "").strip()
                # Clean up the response - remove FTS5-incompatible characters
                import re
                keywords = keywords.replace('"', '').replace('\n', ' ')
                # Remove special chars that break FTS5: ? ! @ # $ % ^ & * ( ) [ ] { } < > / \ | ~ ` ; :
                keywords = re.sub(r'[?!@#$%^&*()\[\]{}<>/\\|~`;:,.]', ' ', keywords)
                keywords = keywords.strip()
                # Replace multiple spaces with single space
                keywords = re.sub(r'\s+', ' ', keywords)
                logger.info(f"Extracted and cleaned keywords: '{keywords}'")
                return keywords
            else:
                logger.warning(f"Keyword extraction failed, using original question")
                # Clean the original question too
                import re
                cleaned = re.sub(r'[?!@#$%^&*()\[\]{}<>/\\|~`;:,.]', ' ', question)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                return cleaned
                
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            # Return cleaned version of question as fallback
            import re
            cleaned = re.sub(r'[?!@#$%^&*()\[\]{}<>/\\|~`;:,.]', ' ', question)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned

    def ask(self, question: str, fts_search_func, conversation_history: List[Dict] = None) -> Dict:
        """
        SMART AGENT PATTERN: Ask a question about timeline events.
        
        Flow:
        1. Extract search keywords (2-3 seconds)
        2. Search FTS5 with keywords (instant)
        3. Generate answer from snippets (3-5 seconds)
        
        Args:
            question: User's natural language question
            fts_search_func: Function to call FTS5 search (passed from route)
            conversation_history: Previous conversation for context
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Start timing
            start_time = time.time()
            
            # STAGE 1: Extract search keywords
            logger.info(f"Question: {question}")
            keywords = self.extract_search_keywords(question)
            extract_time = time.time() - start_time
            
            # STAGE 2: Search FTS5 (instant)
            search_start = time.time()
            search_results = fts_search_func(keywords)
            search_time = time.time() - search_start
            logger.info(f"FTS5 search time: {search_time:.3f}s, found {len(search_results)} results")
            
            # STAGE 3: Generate answer from focused snippets
            answer_start = time.time()
            
            if not search_results:
                return {
                    "answer": f"I searched for '{keywords}' but didn't find any matching events in your timeline.",
                    "sources": [],
                    "keywords_used": keywords,
                    "timing": {
                        "total": round(time.time() - start_time, 3),
                        "keyword_extraction": round(extract_time, 3),
                        "fts5_search": round(search_time, 3),
                        "answer_generation": 0
                    }
                }
            
            # Build minimal context from snippets (NOT full text!)
            context = self._build_focused_context(search_results[:5])  # Max 5 results
            
            # Focused prompt for answer generation
            prompt = self._build_focused_prompt(question, context, conversation_history)
            
            logger.info(f"Focused prompt length: {len(prompt)} chars")
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_ctx": 512,      # Small context window
                        "num_predict": 150,  # Concise answers
                        "num_thread": 8,
                    }
                },
                timeout=120  # Model may still be loaded from first stage
            )
            
            answer_time = time.time() - answer_start
            logger.info(f"Answer generation time: {answer_time:.3f}s")
            
            if response.status_code == 200:
                result = response.json()
                answer_text = result.get("response", "").strip()
                
                # Extract event references
                referenced_events = self._extract_event_references_from_results(answer_text, search_results)
                
                total_time = time.time() - start_time
                logger.info(f"Total request time: {total_time:.3f}s")
                
                return {
                    "answer": answer_text,
                    "sources": referenced_events,
                    "keywords_used": keywords,
                    "model": self.model,
                    "context_used": len(search_results),
                    "timing": {
                        "total": round(total_time, 3),
                        "keyword_extraction": round(extract_time, 3),
                        "fts5_search": round(search_time, 3),
                        "answer_generation": round(answer_time, 3)
                    }
                }
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {
                    "answer": "I'm having trouble connecting to the AI service. Please try again.",
                    "sources": [],
                    "error": True
                }
                
        except Exception as e:
            logger.error(f"Error in smart ask: {str(e)}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "sources": [],
                "error": True
            }
    
    def _build_focused_context(self, search_results: List[Dict]) -> str:
        """
        Build MINIMAL context from FTS5 search results.
        Only uses snippets, not full text!
        
        Args:
            search_results: List of FTS5 search results with snippets
            
        Returns:
            Focused context string (under 500 chars)
        """
        if not search_results:
            return "No relevant events found."
        
        context_parts = []
        
        for i, result in enumerate(search_results[:5], 1):
            # Get the event from the result
            event = result.get('event', {})
            
            # Use snippet or truncated description
            snippet = result.get('description_snippet', '')
            if not snippet:
                desc = event.get('description', '')
                snippet = desc[:80] + "..." if len(desc) > 80 else desc
            
            # Format: "1. Title (Date) - snippet"
            event_text = f"{i}. {event.get('title', 'Untitled')} ({event.get('date', 'Unknown')})"
            if snippet:
                # Clean HTML marks from snippet
                snippet = snippet.replace('<mark>', '').replace('</mark>', '')
                event_text += f" - {snippet}"
            
            context_parts.append(event_text)
        
        return "\n".join(context_parts)
    
    def _build_focused_prompt(self, question: str, context: str, history: List[Dict] = None) -> str:
        """
        Build MINIMAL prompt for focused answer generation.
        Much shorter than old version = faster inference!
        
        Args:
            question: User's question
            context: Focused context from snippets
            history: Conversation history (optional)
            
        Returns:
            Focused prompt string (~400 chars)
        """
        # Minimal system instruction
        system = "Answer based ONLY on these timeline events. Be concise. Cite event titles."
        
        prompt_parts = [system, "\n\n"]
        
        # Add conversation history (only last 2 turns to stay minimal)
        if history and len(history) > 0:
            last_turn = history[-1]
            prompt_parts.append(f"Previous: Q: {last_turn.get('question', '')} A: {last_turn.get('answer', '')[:100]}\n\n")
        
        # Add context and question
        prompt_parts.append("Events:\n")
        prompt_parts.append(context)
        prompt_parts.append(f"\n\nQ: {question}\nA:")
        
        return "".join(prompt_parts)
    
    def _extract_event_references_from_results(self, answer: str, search_results: List[Dict]) -> List[Dict]:
        """
        Extract which events were referenced in the answer.
        
        Args:
            answer: The generated answer text
            search_results: FTS5 search results
            
        Returns:
            List of event dicts that were referenced
        """
        referenced = []
        
        for result in search_results:
            event = result.get('event', {})
            title = event.get('title', '').lower()
            # Simple matching - check if event title appears in answer
            if title and title in answer.lower():
                referenced.append({
                    'id': event.get('id'),
                    'title': event.get('title'),
                    'date': event.get('date'),
                    'has_audio': bool(event.get('audio_file'))
                })
        
        return referenced


# Singleton instance
_ollama_service = None


def get_ollama_service() -> OllamaService:
    """Get or create the Ollama service singleton."""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service
