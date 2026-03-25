"""
Rule-based chatbot engine using keyword matching and fuzzy matching.
NO ML. NO AI. NO external dependencies.
Uses Python's built-in difflib for fuzzy matching.
FIXED FAQ QUESTIONS HAVE PRIORITY OVER ALL OTHER MATCHING.
"""

import json
import re
import string
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import fixed FAQ with priority
from .fixed_faq import check_fixed_faq, FIXED_FAQ_QUESTIONS


class ChatbotEngine:
    """
    Lightweight rule-based chatbot using keyword, substring, and fuzzy matching.
    Loads FAQ data once at startup for instant responses.
    Uses difflib for fuzzy matching - NO ML libraries.
    """
    
    def __init__(self, faq_path: str = None):
        """
        Initialize the chatbot engine with FAQ data.
        
        Args:
            faq_path: Path to the faq.json file
        """
        self.faq_data: List[Dict] = []
        self.fallback_response: str = "I'm sorry, I don't have information about that topic."
        self.metadata: Dict = {}
        
        # Load FAQ data at startup
        if faq_path:
            self.load_faq(faq_path)
        
        print("✅ Loaded FAQ")
    
    def load_faq(self, faq_path: str) -> None:
        """
        Load FAQ data from JSON file.
        Supports both simple array format and object format with faq_entries.
        
        Args:
            faq_path: Path to the faq.json file
        """
        try:
            path = Path(faq_path)
            if not path.exists():
                raise FileNotFoundError(f"FAQ file not found: {faq_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both formats: array or object with faq_entries
            if isinstance(data, list):
                self.faq_data = data
            else:
                self.faq_data = data.get('faq_entries', [])
                self.fallback_response = data.get(
                    'fallback_response', 
                    "I'm sorry, I don't have information about that topic."
                )
                self.metadata = data.get('metadata', {})
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in FAQ file: {e}")
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for matching: lowercase, trim, remove punctuation.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def tokenize(text: str) -> set:
        """
        Tokenize normalized text into a set of words.
        
        Args:
            text: Normalized text
            
        Returns:
            Set of word tokens
        """
        return set(text.split()) if text else set()
    
    def calculate_keyword_score(
        self, 
        user_tokens: set, 
        faq_entry: Dict
    ) -> float:
        """
        Calculate match score based on keyword overlap.
        
        Args:
            user_tokens: Tokenized user input
            faq_entry: FAQ entry to score against
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not user_tokens:
            return 0.0
        
        # Get FAQ keywords - use keywords field if present, otherwise extract from question
        if 'keywords' in faq_entry and faq_entry['keywords']:
            faq_keywords = set(faq_entry.get('keywords', []))
            faq_keywords = {self.normalize_text(kw) for kw in faq_keywords}
        else:
            # Extract keywords from the question itself
            faq_question = faq_entry.get('question', '')
            faq_keywords = self.tokenize(self.normalize_text(faq_question))
        
        if not faq_keywords:
            return 0.0
        
        # Calculate keyword overlap
        keyword_overlap = len(user_tokens & faq_keywords)
        keyword_score = keyword_overlap / len(faq_keywords)
        
        return min(keyword_score, 1.0)
    
    def calculate_substring_score(
        self, 
        normalized_user: str, 
        faq_entry: Dict
    ) -> float:
        """
        Calculate match score based on substring matching.
        
        Args:
            normalized_user: Normalized user input
            faq_entry: FAQ entry to score against
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not normalized_user:
            return 0.0
        
        # Normalize FAQ question
        faq_question = self.normalize_text(faq_entry.get('question', ''))
        
        if not faq_question:
            return 0.0
        
        # Check substring matches (both directions)
        if normalized_user in faq_question:
            # User input is substring of FAQ question
            return len(normalized_user) / len(faq_question)
        elif faq_question in normalized_user:
            # FAQ question is substring of user input
            return len(faq_question) / len(normalized_user)
        
        # Check for partial word matches
        user_words = self.tokenize(normalized_user)
        faq_words = self.tokenize(faq_question)
        
        if not user_words or not faq_words:
            return 0.0
        
        word_overlap = len(user_words & faq_words)
        return word_overlap / max(len(user_words), len(faq_words))
    
    def calculate_fuzzy_score(
        self, 
        user_input: str, 
        faq_entry: Dict
    ) -> float:
        """
        Calculate match score using difflib fuzzy matching.
        
        Args:
            user_input: Raw user input
            faq_entry: FAQ entry to score against
            
        Returns:
            Score between 0.0 and 1.0
        """
        normalized_user = self.normalize_text(user_input)
        faq_question = self.normalize_text(faq_entry.get('question', ''))
        
        if not normalized_user or not faq_question:
            return 0.0
        
        # Use difflib SequenceMatcher for fuzzy string matching
        matcher = difflib.SequenceMatcher(None, normalized_user, faq_question)
        fuzzy_ratio = matcher.ratio()
        
        # Also check fuzzy match against keywords
        keywords = faq_entry.get('keywords', [])
        if keywords:
            keyword_matches = []
            for keyword in keywords:
                kw_normalized = self.normalize_text(keyword)
                if kw_normalized:
                    kw_matcher = difflib.SequenceMatcher(None, normalized_user, kw_normalized)
                    keyword_matches.append(kw_matcher.ratio())
            
            if keyword_matches:
                max_keyword_match = max(keyword_matches)
                # Take the better of question match or keyword match
                fuzzy_ratio = max(fuzzy_ratio, max_keyword_match)
        
        return fuzzy_ratio
    
    def calculate_total_score(
        self, 
        user_input: str, 
        faq_entry: Dict
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate total match score combining multiple methods.
        
        Args:
            user_input: Raw user input
            faq_entry: FAQ entry to score against
            
        Returns:
            Tuple of (total_score, score_breakdown)
        """
        normalized_user = self.normalize_text(user_input)
        user_tokens = self.tokenize(normalized_user)
        
        # Calculate individual scores
        keyword_score = self.calculate_keyword_score(user_tokens, faq_entry)
        substring_score = self.calculate_substring_score(normalized_user, faq_entry)
        fuzzy_score = self.calculate_fuzzy_score(user_input, faq_entry)
        
        # Weight the scores: keyword (40%), substring (20%), fuzzy (40%)
        total_score = (keyword_score * 0.4) + (substring_score * 0.2) + (fuzzy_score * 0.4)
        
        score_breakdown = {
            "keyword_score": round(keyword_score, 3),
            "substring_score": round(substring_score, 3),
            "fuzzy_score": round(fuzzy_score, 3)
        }
        
        return total_score, score_breakdown
    
    def get_confidence_label(self, score: float) -> str:
        """
        Convert numeric score to confidence label.
        
        Args:
            score: Numeric score (0.0-1.0)
            
        Returns:
            Confidence label: 'low', 'medium', or 'high'
        """
        if score >= 0.5:
            return "high"
        elif score >= 0.25:
            return "medium"
        else:
            return "low"
    
    def find_best_match(self, user_input: str) -> Dict:
        """
        Find the best matching FAQ entry for user input.
        FIXED FAQ QUESTIONS HAVE PRIORITY OVER ALL OTHER MATCHING.
        
        Args:
            user_input: User's question/input
            
        Returns:
            Dictionary with match results
        """
        if not user_input or not user_input.strip():
            return {
                "matched_question": None,
                "answer": self.fallback_response,
                "confidence_score": 0.0,
                "confidence_label": "low",
                "match_found": False
            }
        
        # PRIORITY 1: Check fixed FAQ questions first
        fixed_result = check_fixed_faq(user_input)
        if fixed_result and fixed_result.get("matched"):
            return {
                "matched_question": fixed_result["question"],
                "answer": fixed_result["answer"],
                "confidence_score": fixed_result["confidence"],
                "confidence_label": "high" if fixed_result["confidence"] >= 0.5 else "medium",
                "match_found": True,
                "source": "fixed_faq",
                "faq_id": fixed_result.get("faq_id")
            }
        
        # PRIORITY 2: Search in general FAQ data
        best_score = 0.0
        best_entry = None
        best_breakdown = {}
        
        # Score all FAQ entries
        for entry in self.faq_data:
            score, breakdown = self.calculate_total_score(user_input, entry)
            
            if score > best_score:
                best_score = score
                best_entry = entry
                best_breakdown = breakdown
        
        # Determine if match is acceptable (threshold: 0.15)
        min_threshold = 0.15
        
        if best_entry and best_score >= min_threshold:
            return {
                "matched_question": best_entry.get('question'),
                "answer": best_entry.get('answer'),
                "confidence_score": round(best_score, 3),
                "confidence_label": self.get_confidence_label(best_score),
                "match_found": True,
                "score_breakdown": best_breakdown,
                "faq_id": best_entry.get('id')
            }
        
        # No good match found
        return {
            "matched_question": best_entry.get('question') if best_entry else None,
            "answer": self.fallback_response,
            "confidence_score": round(best_score, 3),
            "confidence_label": self.get_confidence_label(best_score),
            "match_found": False,
            "score_breakdown": best_breakdown if best_breakdown else None
        }
    
    def chat(self, user_input: str) -> str:
        """
        Simple chat interface - returns just the answer.
        
        Args:
            user_input: User's question/input
            
        Returns:
            Chatbot response string
        """
        result = self.find_best_match(user_input)
        return result.get('answer', self.fallback_response)


# Global chatbot instance (initialized with default path)
chatbot: Optional[ChatbotEngine] = None


def initialize_chatbot(faq_path: str) -> ChatbotEngine:
    """
    Initialize the global chatbot instance.
    
    Args:
        faq_path: Path to the faq.json file
        
    Returns:
        Initialized ChatbotEngine instance
    """
    global chatbot
    chatbot = ChatbotEngine(faq_path)
    return chatbot


def get_chatbot() -> ChatbotEngine:
    """
    Get the global chatbot instance.
    
    Returns:
        ChatbotEngine instance
        
    Raises:
        RuntimeError: If chatbot not initialized
    """
    if chatbot is None:
        raise RuntimeError("Chatbot not initialized. Call initialize_chatbot() first.")
    return chatbot
