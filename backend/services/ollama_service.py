"""
Ollama LLM Service for Conversational Timeline Queries

Provides natural language interface to query and understand timeline events.
Uses local Ollama instance for privacy-first AI assistance.
"""

import os
import requests
import json
import logging
from typing import List, Dict, Optional

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
        
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def ask(self, question: str, context_events: List[Dict], conversation_history: List[Dict] = None) -> Dict:
        """
        Ask a natural language question about timeline events.
        
        Args:
            question: User's natural language question
            context_events: List of relevant events from FTS5 search
            conversation_history: Previous conversation for context
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Build context from events
            context = self._build_context(context_events)
            
            # Build prompt
            prompt = self._build_prompt(question, context, conversation_history)
            
            # Debug logging
            logger.info(f"Prompt length: {len(prompt)} chars, {len(prompt.split())} words")
            logger.info(f"Context events: {len(context_events)}")
            
            # Call Ollama with optimized settings for speed
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_ctx": 2048,  # Smaller context window for speed
                        "num_predict": 256,  # Limit response length
                    }
                },
                timeout=60  # Should be much faster now
            )
            
            if response.status_code == 200:
                result = response.json()
                answer_text = result.get("response", "").strip()
                
                # Extract event references from answer
                referenced_events = self._extract_event_references(answer_text, context_events)
                
                return {
                    "answer": answer_text,
                    "sources": referenced_events,
                    "model": self.model,
                    "context_used": len(context_events)
                }
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {
                    "answer": "I'm having trouble connecting to the AI service. Please try again.",
                    "sources": [],
                    "error": True
                }
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "sources": [],
                "error": True
            }
    
    def _build_context(self, events: List[Dict]) -> str:
        """
        Build context string from events for the LLM.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Formatted context string
        """
        if not events:
            return "No relevant events found in the timeline."
        
        context_parts = ["Relevant events:\n"]
        
        # Limit to top 5 for speed, with concise formatting
        for i, event in enumerate(events[:5], 1):
            event_text = f"{i}. {event.get('title', 'Untitled')} ({event.get('date', 'Unknown')})"
            
            # Add description/transcript - much shorter for speed
            description = event.get('description', '')
            if description:
                # Aggressive truncation for speed
                if len(description) > 150:
                    description = description[:150] + "..."
                event_text += f" - {description}"
            
            context_parts.append(event_text)
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str, history: List[Dict] = None) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            question: User's question
            context: Event context
            history: Conversation history
            
        Returns:
            Complete prompt string
        """
        system_prompt = """You help users query their Chronicle timeline events. 

CRITICAL RULES:
- ONLY use information from the events provided below
- NEVER make up or invent event names, dates, or details
- If the events don't contain the answer, say "I don't see any events about that in this timeline"
- Always cite the actual event title when referencing information
- Be concise and factual"""

        prompt_parts = [system_prompt, "\n\n"]
        
        # Add conversation history if present
        if history:
            prompt_parts.append("Previous conversation:\n")
            for turn in history[-3:]:  # Last 3 turns for context
                prompt_parts.append(f"User: {turn.get('question', '')}\n")
                prompt_parts.append(f"Assistant: {turn.get('answer', '')}\n")
            prompt_parts.append("\n")
        
        # Add current context and question
        prompt_parts.append("EVENTS IN THIS TIMELINE:\n")
        prompt_parts.append(context)
        prompt_parts.append(f"\n\nUser's question: {question}")
        prompt_parts.append("\n\nAnswer (only use information from the events above):")
        
        return "".join(prompt_parts)
    
    def _extract_event_references(self, answer: str, events: List[Dict]) -> List[Dict]:
        """
        Extract which events were referenced in the answer.
        
        Args:
            answer: The generated answer text
            events: Available events
            
        Returns:
            List of event dicts that were referenced
        """
        referenced = []
        
        for event in events:
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
