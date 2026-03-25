"""
Validation system for testing chatbot accuracy.
Provides detailed response analysis for manual testing.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class ValidationRequest(BaseModel):
    """Request model for validation endpoint."""
    question: str


class ValidationResult(BaseModel):
    """Response model for validation endpoint."""
    matched_question: Optional[str] = None
    answer: str
    confidence_score: float
    confidence_label: str
    match_found: bool
    score_breakdown: Optional[Dict[str, float]] = None
    faq_id: Optional[str] = None  # Changed from int to str to support "fixed_1", "fixed_2", etc.


class ChatbotValidator:
    """
    Validator class for testing chatbot accuracy.
    Provides detailed analysis of chatbot responses.
    """
    
    def __init__(self, chatbot_engine):
        """
        Initialize validator with chatbot engine.
        
        Args:
            chatbot_engine: ChatbotEngine instance
        """
        self.chatbot = chatbot_engine
    
    def validate_question(self, question: str) -> Dict[str, Any]:
        """
        Validate a question and return detailed analysis.
        
        Args:
            question: User question to validate
            
        Returns:
            Dictionary with validation results
        """
        if not question or not question.strip():
            return {
                "matched_question": None,
                "answer": self.chatbot.fallback_response,
                "confidence_score": 0.0,
                "confidence_label": "low",
                "match_found": False,
                "error": "Empty question provided"
            }
        
        # Get match result from chatbot
        result = self.chatbot.find_best_match(question.strip())
        
        return result
    
    def batch_validate(self, questions: list) -> list:
        """
        Validate multiple questions at once.
        
        Args:
            questions: List of questions to validate
            
        Returns:
            List of validation results
        """
        results = []
        for question in questions:
            result = self.validate_question(question)
            result["original_question"] = question
            results.append(result)
        return results
    
    def get_accuracy_stats(self, test_cases: list) -> Dict[str, Any]:
        """
        Calculate accuracy statistics from test cases.
        
        Args:
            test_cases: List of dicts with 'question' and 'expected_id' keys
            
        Returns:
            Dictionary with accuracy statistics
        """
        if not test_cases:
            return {"error": "No test cases provided"}
        
        correct = 0
        total = len(test_cases)
        confidence_distribution = {"high": 0, "medium": 0, "low": 0}
        
        for case in test_cases:
            result = self.validate_question(case.get("question", ""))
            
            # Check if correct
            if result.get("faq_id") == case.get("expected_id"):
                correct += 1
            
            # Track confidence distribution
            label = result.get("confidence_label", "low")
            confidence_distribution[label] = confidence_distribution.get(label, 0) + 1
        
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        return {
            "total_test_cases": total,
            "correct_matches": correct,
            "accuracy_percentage": round(accuracy, 2),
            "confidence_distribution": confidence_distribution
        }


# Global validator instance
validator: Optional[ChatbotValidator] = None


def initialize_validator(chatbot_engine) -> ChatbotValidator:
    """
    Initialize the global validator instance.
    
    Args:
        chatbot_engine: ChatbotEngine instance
        
    Returns:
        Initialized ChatbotValidator instance
    """
    global validator
    validator = ChatbotValidator(chatbot_engine)
    return validator


def get_validator() -> ChatbotValidator:
    """
    Get the global validator instance.
    
    Returns:
        ChatbotValidator instance
        
    Raises:
        RuntimeError: If validator not initialized
    """
    if validator is None:
        raise RuntimeError("Validator not initialized. Call initialize_validator() first.")
    return validator
