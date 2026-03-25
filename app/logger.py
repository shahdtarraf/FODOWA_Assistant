"""
In-memory logging system for chatbot requests.
Stores last 50 requests for monitoring and debugging.
"""

from collections import deque
from datetime import datetime
from typing import Dict, Any, Optional
import threading


class RequestLogger:
    """
    Thread-safe in-memory logger that stores the last 50 requests.
    """
    
    def __init__(self, max_size: int = 50):
        self._logs: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._max_size = max_size
    
    def log_request(
        self,
        endpoint: str,
        user_input: str,
        response: str,
        confidence: Optional[float] = None,
        matched_question: Optional[str] = None
    ) -> None:
        """
        Log a chatbot request with all relevant details.
        
        Args:
            endpoint: The API endpoint called
            user_input: The user's question/input
            response: The chatbot's response
            confidence: Confidence score (0.0-1.0)
            matched_question: The matched FAQ question (if any)
        """
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "endpoint": endpoint,
            "user_input": user_input,
            "response": response,
            "confidence": confidence,
            "matched_question": matched_question
        }
        
        with self._lock:
            self._logs.append(log_entry)
    
    def get_all_logs(self) -> list:
        """
        Retrieve all stored logs.
        
        Returns:
            List of log entries (oldest to newest)
        """
        with self._lock:
            return list(self._logs)
    
    def get_recent_logs(self, count: int = 10) -> list:
        """
        Retrieve the most recent logs.
        
        Args:
            count: Number of recent logs to retrieve
            
        Returns:
            List of most recent log entries
        """
        with self._lock:
            logs_list = list(self._logs)
            return logs_list[-count:] if logs_list else []
    
    def clear_logs(self) -> int:
        """
        Clear all stored logs.
        
        Returns:
            Number of logs that were cleared
        """
        with self._lock:
            count = len(self._logs)
            self._logs.clear()
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged requests.
        
        Returns:
            Dictionary with log statistics
        """
        with self._lock:
            logs_list = list(self._logs)
            
            if not logs_list:
                return {
                    "total_requests": 0,
                    "max_capacity": self._max_size,
                    "current_size": 0
                }
            
            # Calculate average confidence
            confidences = [
                log["confidence"] for log in logs_list 
                if log.get("confidence") is not None
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "total_requests": len(logs_list),
                "max_capacity": self._max_size,
                "current_size": len(logs_list),
                "average_confidence": round(avg_confidence, 3)
            }


# Global logger instance
request_logger = RequestLogger(max_size=50)
