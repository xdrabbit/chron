"""
Smart Summary Service

Generates concise summaries from transcripts using:
1. First 1-2 sentences (contextual opening)
2. Key topic extraction (TF-IDF based)

Future enhancement: Personalized summaries based on user's communication style
learned from emails/messages (opt-in)
"""

import re
from collections import Counter
from typing import List, Dict
import math


class SummaryService:
    """
    Generate smart summaries from text transcripts.
    
    Future: Will incorporate user preference learning from opted-in communications.
    """
    
    # Common words to ignore in topic extraction
    STOP_WORDS = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
        'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 've', 'll',
        're', 'm', 'yeah', 'ok', 'okay', 'um', 'uh', 'like', 'know', 'think', 'mean',
        'going', 'get', 'got', 'let', 'see', 'well', 'right', 'want', 'need', 'make',
    }
    
    def __init__(self):
        """Initialize the summary service."""
        # Future: Load user preference model here
        self.user_style_model = None
    
    def generate_summary(self, text: str, max_snippet_chars: int = 150, 
                        num_topics: int = 5) -> Dict[str, any]:
        """
        Generate a smart summary with opening snippet and key topics.
        
        Args:
            text: The full transcript text
            max_snippet_chars: Maximum characters for the opening snippet
            num_topics: Number of key topics to extract
            
        Returns:
            Dict with 'snippet' and 'topics' keys
        """
        if not text or not text.strip():
            return {
                'snippet': '',
                'topics': []
            }
        
        # Get opening snippet (first 1-2 sentences)
        snippet = self._extract_opening_snippet(text, max_snippet_chars)
        
        # Extract key topics
        topics = self._extract_key_topics(text, num_topics)
        
        return {
            'snippet': snippet,
            'topics': topics
        }
    
    def _extract_opening_snippet(self, text: str, max_chars: int) -> str:
        """
        Extract the opening 1-2 sentences up to max_chars.
        
        Args:
            text: Full text
            max_chars: Maximum characters
            
        Returns:
            Opening snippet
        """
        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+\s+', text.strip())
        
        snippet = ""
        for sentence in sentences:
            # Add sentence if it fits
            if len(snippet) + len(sentence) <= max_chars:
                snippet += sentence + ". "
            else:
                # If snippet is still empty, truncate the first sentence
                if not snippet:
                    snippet = sentence[:max_chars-3] + "..."
                break
        
        return snippet.strip()
    
    def _extract_key_topics(self, text: str, num_topics: int) -> List[str]:
        """
        Extract key topics using simple TF-IDF-like scoring.
        
        Future: Will incorporate user's preferred topic categories and
        terminology learned from their communications.
        
        Args:
            text: Full text
            num_topics: Number of topics to extract
            
        Returns:
            List of key topic words
        """
        # Normalize text
        text_lower = text.lower()
        
        # Extract words (alphanumeric, 3+ chars)
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        
        # Filter stop words
        meaningful_words = [w for w in words if w not in self.STOP_WORDS]
        
        if not meaningful_words:
            return []
        
        # Count word frequencies
        word_freq = Counter(meaningful_words)
        
        # Simple TF-IDF scoring (TF only since we have one document)
        # Words that appear multiple times are likely important
        scored_words = []
        for word, count in word_freq.items():
            # Score based on frequency and length (longer words often more specific)
            score = count * (1 + (len(word) - 3) * 0.1)
            scored_words.append((word, score))
        
        # Sort by score and take top N unique topics
        scored_words.sort(key=lambda x: x[1], reverse=True)
        topics = [word for word, score in scored_words[:num_topics]]
        
        return topics
    
    def learn_from_user_communications(self, communications: List[Dict]):
        """
        Future method: Learn user's communication style and preferences.
        
        This will analyze opted-in emails/messages to understand:
        - Preferred vocabulary and terminology
        - Topic categories user cares about
        - Summary style (formal vs casual, detailed vs brief)
        - Key phrases and patterns
        
        Args:
            communications: List of user's communications (with opt-in consent)
        """
        # Placeholder for future ML-based personalization
        pass
    
    def generate_personalized_summary(self, text: str) -> Dict[str, any]:
        """
        Future method: Generate personalized summary based on learned preferences.
        
        Args:
            text: The full transcript text
            
        Returns:
            Dict with personalized summary
        """
        # For now, use default summary
        # Future: Apply user's learned preferences
        return self.generate_summary(text)


# Singleton instance
_summary_service = None

def get_summary_service() -> SummaryService:
    """Get or create the summary service singleton."""
    global _summary_service
    if _summary_service is None:
        _summary_service = SummaryService()
    return _summary_service
