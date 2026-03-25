"""
Memory usage check script for FAQ Chatbot.
Run this to verify the app stays under 100MB RAM.

Usage:
    python check_memory.py
"""

import os
import sys
import tracemalloc
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"


def check_memory():
    """Check memory usage of the chatbot application."""
    print("=" * 60)
    print("MEMORY USAGE CHECK")
    print("=" * 60)
    
    # Start memory tracking
    tracemalloc.start()
    
    # Import and initialize the chatbot
    from app.chatbot import initialize_chatbot, get_chatbot
    from app.validator import initialize_validator
    
    faq_path = os.path.join(os.path.dirname(__file__), 'data', 'faq.json')
    
    print("\n📦 Initializing chatbot...")
    chatbot = initialize_chatbot(faq_path)
    initialize_validator(chatbot)
    
    # Get current memory usage
    current, peak = tracemalloc.get_traced_memory()
    
    print(f"\n📊 Memory Statistics:")
    print(f"   Current usage: {format_bytes(current)}")
    print(f"   Peak usage:    {format_bytes(peak)}")
    
    # Test some queries to see memory impact
    print("\n🔍 Testing queries...")
    test_questions = [
        "What are your business hours?",
        "How do I track my order?",
        "What is your return policy?",
        "Do you offer international shipping?",
        "xyzabc unknown question"
    ]
    
    for question in test_questions:
        result = chatbot.find_best_match(question)
        print(f"   Q: {question[:40]}... → Confidence: {result['confidence_score']:.2f}")
    
    # Get memory after queries
    current_after, peak_after = tracemalloc.get_traced_memory()
    
    print(f"\n📊 Memory After Queries:")
    print(f"   Current usage: {format_bytes(current_after)}")
    print(f"   Peak usage:    {format_bytes(peak_after)}")
    
    # Check against limits
    MAX_MEMORY_MB = 100
    peak_mb = peak_after / (1024 * 1024)
    
    print("\n" + "=" * 60)
    if peak_mb < MAX_MEMORY_MB:
        print(f"✅ PASSED: Peak memory ({peak_mb:.2f} MB) is under {MAX_MEMORY_MB} MB limit")
    else:
        print(f"⚠️  WARNING: Peak memory ({peak_mb:.2f} MB) exceeds {MAX_MEMORY_MB} MB limit")
    print("=" * 60)
    
    # Stop tracking
    tracemalloc.stop()
    
    return peak_mb < MAX_MEMORY_MB


if __name__ == "__main__":
    success = check_memory()
    sys.exit(0 if success else 1)
