"""
FastAPI main application for production-ready chatbot backend.
Deployed on Render Free plan (512MB RAM).
Fixed FAQ questions have PRIORITY over all other matching.
"""

import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .chatbot import initialize_chatbot, get_chatbot
from .validator import initialize_validator, get_validator, ValidationRequest, ValidationResult
from .logger import request_logger
from .fixed_faq import FIXED_FAQ_QUESTIONS


# Configuration
FAQ_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.json')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes chatbot engine at startup.
    """
    # Startup
    print("🚀 Starting up chatbot backend...")
    
    # Initialize chatbot engine
    chatbot_engine = initialize_chatbot(FAQ_PATH)
    
    # Initialize validator
    initialize_validator(chatbot_engine)
    
    print(f"✅ Loaded {len(FIXED_FAQ_QUESTIONS)} fixed FAQ questions (PRIORITY)")
    print("✅ App Ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down chatbot backend...")


# Create FastAPI app with production-ready Swagger UI
app = FastAPI(
    title="FODOWA Chatbot API",
    description="""
## 🤖 FAQ Chatbot API

Intelligent FAQ matching with priority questions and fuzzy matching.

---

### 🎯 What This API Does
Provides instant answers to user questions using smart FAQ matching - no AI/ML required.

---

### ⚙️ How It Works

1. **Priority Matching**: 4 fixed questions always matched first with confidence = 1.0
2. **Fuzzy Matching**: Handles typos using difflib similarity (confidence 0.5-0.99)
3. **Fallback**: No match returns default message (confidence < 0.15)

---

### 📊 Confidence Score Guide

| Score | Meaning |
|-------|--------|
| **1.0** | Exact match - 100% confident |
| **0.5-0.99** | Strong match - high confidence |
| **0.15-0.49** | Weak match - may need review |
| **<0.15** | No match - fallback response |

---

### 🔒 Fixed Priority Questions

These 4 questions ALWAYS have priority:

1. **ما هي منصة فودوا؟**
2. **ما هي اللغات المتوفرة؟**
3. **هل الموقع آمن؟**
4. **كيف أبدأ؟**

---

### 🚀 Quick Test

```bash
curl -X POST https://fodowa-assistant.onrender.com/chat \\
  -H "Content-Type: application/json" \\
  -d '{"question": "ما هي منصة فودوا؟"}'
```

---

### 👥 Who Should Use This

- **Developers**: Integrate chatbot into your apps
- **Companies**: Add FAQ support to your services
- **Testers**: Use `/validate` for detailed analysis
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    tags_metadata=[
        {
            "name": "Chat",
            "description": "Chatbot interaction endpoints for asking questions.",
        },
        {
            "name": "Health",
            "description": "System health monitoring and status checks.",
        },
        {
            "name": "Validation",
            "description": "Detailed match analysis for testing and debugging.",
        },
        {
            "name": "Logs",
            "description": "Request logging and statistics retrieval.",
        },
        {
            "name": "Integration",
            "description": "Company API integration preparation endpoints.",
        },
    ]
)

# Enable CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
from pydantic import Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str = Field(
        ...,
        description="User's question to the chatbot",
        example="ما هي منصة فودوا؟",
        min_length=1,
        max_length=500
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(
        ...,
        description="Chatbot's answer to the question",
        example="فودوا هي منصة ذكية متكاملة تقدم حلولاً تقنية متقدمة للشركات والأفراد."
    )
    confidence: float = Field(
        ...,
        description="Confidence score between 0.0 and 1.0",
        example=0.95,
        ge=0.0,
        le=1.0
    )
    matched_question: Optional[str] = Field(
        None,
        description="The FAQ question that was matched",
        example="ما هي منصة فودوا؟"
    )


class CompanyIntegrationRequest(BaseModel):
    """Request model for company API integration."""
    message: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None


# API Endpoints

@app.get(
    "/",
    tags=["Core"],
    summary="Chatbot Web Interface",
    description="""
Serves the interactive chatbot web interface (HTML page).

**Returns:** HTML page with Arabic chat UI

**Note:** This endpoint returns HTML, not JSON. Visit in browser to use the chat interface.
""",
    response_class=HTMLResponse,
    responses={
        200: {
            "description": "HTML chat interface",
            "content": {"text/html": {"example": "<!DOCTYPE html>..."}}
        }
    }
)
async def root() -> HTMLResponse:
    """
    Root endpoint - serves the chat UI (HTML page).
    """
    static_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
    with open(static_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get(
    "/health",
    tags=["Health"],
    summary="Check System Health",
    description="Check system health status.",
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "faq_loaded": True,
                        "faq_count": 45,
                        "fixed_faq_count": 4,
                        "memory_usage": "low",
                        "ready": True
                    }
                }
            }
        },
        503: {"description": "System is unhealthy"}
    }
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and Render deployment.
    """
    try:
        chatbot = get_chatbot()
        return {
            "status": "healthy",
            "faq_loaded": len(chatbot.faq_data) > 0,
            "faq_count": len(chatbot.faq_data),
            "fixed_faq_count": len(FIXED_FAQ_QUESTIONS),
            "memory_usage": "low",
            "ready": True
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "ready": False
            }
        )


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Ask a Question",
    description="Send a question and receive an intelligent FAQ-based answer.",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "فودوا هي منصة ذكية متكاملة تقدم حلولاً تقنية متقدمة.",
                        "confidence": 1.0,
                        "matched_question": "ما هي منصة فودوا؟"
                    }
                }
            }
        },
        400: {"description": "Bad request - empty question"}
    }
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint - returns chatbot response for user question.
    
    Args:
        request: ChatRequest with user question
        
    Returns:
        ChatResponse with answer and optional match details
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    chatbot = get_chatbot()
    
    # Get match result
    result = chatbot.find_best_match(request.question)
    
    # Log the request
    request_logger.log_request(
        endpoint="/chat",
        user_input=request.question,
        response=result["answer"],
        confidence=result.get("confidence_score"),
        matched_question=result.get("matched_question")
    )
    
    return ChatResponse(
        answer=result["answer"],
        matched_question=result.get("matched_question"),
        confidence=result.get("confidence_score", 0.0)
    )


@app.post(
    "/validate",
    response_model=ValidationResult,
    tags=["Validation"],
    summary="Detailed Match Analysis",
    description="Get detailed match analysis for testing and debugging."
)
async def validate(request: ValidationRequest) -> ValidationResult:
    """
    Validation endpoint for testing chatbot accuracy.
    Returns detailed match analysis.
    
    Args:
        request: ValidationRequest with user question
        
    Returns:
        ValidationResult with detailed match information
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    validator = get_validator()
    
    # Get validation result
    result = validator.validate_question(request.question)
    
    # Log the validation request
    request_logger.log_request(
        endpoint="/validate",
        user_input=request.question,
        response=result["answer"],
        confidence=result.get("confidence_score"),
        matched_question=result.get("matched_question")
    )
    
    return ValidationResult(**result)


@app.get(
    "/logs",
    tags=["Logs"],
    summary="Get Request Logs",
    description="Retrieve recent chatbot request logs for debugging."
)
async def get_logs(limit: int = 50) -> Dict[str, Any]:
    """
    Retrieve recent chatbot request logs.
    
    Args:
        limit: Maximum number of logs to return (default: 50)
        
    Returns:
        Dictionary with logs and statistics
    """
    if limit < 1 or limit > 100:
        limit = 50
    
    logs = request_logger.get_recent_logs(limit)
    stats = request_logger.get_stats()
    
    return {
        "logs": logs,
        "statistics": stats,
        "returned_count": len(logs)
    }


@app.delete(
    "/logs",
    tags=["Logs"],
    summary="Clear All Logs",
    description="Clear all stored request logs."
)
async def clear_logs() -> Dict[str, Any]:
    """
    Clear all stored logs.
    
    Returns:
        Dictionary with confirmation
    """
    cleared_count = request_logger.clear_logs()
    
    return {
        "message": "Logs cleared successfully",
        "cleared_count": cleared_count
    }


# Company Integration Preparation (Not called automatically)

def send_to_company_api(
    message: str,
    api_endpoint: str,
    api_key: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Prepare message for company API integration.
    
    This function is modular and ready for future integration.
    It does NOT call any external API automatically.
    
    Args:
        message: Message to send
        api_endpoint: Company API endpoint URL
        api_key: API key for authentication
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with prepared payload (not sent)
        
    Usage:
        result = send_to_company_api(
            message="Hello",
            api_endpoint="https://company.com/api/chat",
            api_key="your-api-key"
        )
        # Then use your HTTP client to send result['payload']
    """
    import json
    from datetime import datetime
    
    # Prepare the payload
    payload = {
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "chatbot-backend",
        "version": "1.0.0"
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Source": "chatbot-backend"
    }
    
    # Return prepared data (actual HTTP call should be done by caller)
    return {
        "prepared": True,
        "endpoint": api_endpoint,
        "payload": payload,
        "headers": headers,
        "timeout": timeout,
        "note": "Use your HTTP client to POST payload to endpoint with headers"
    }


@app.post(
    "/integration/prepare",
    tags=["Integration"],
    summary="Prepare Company API Integration",
    description="Prepare a message payload for company API integration. Does NOT send the message."
)
async def prepare_company_integration(request: CompanyIntegrationRequest) -> Dict[str, Any]:
    """
    Prepare a message for company API integration.
    Does NOT send the message - returns prepared payload.
    
    Args:
        request: CompanyIntegrationRequest with message and optional API details
        
    Returns:
        Dictionary with prepared integration data
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Use default or provided API details
    api_endpoint = request.api_endpoint or "https://company.com/api/chat"
    api_key = request.api_key or "YOUR_API_KEY_HERE"
    
    result = send_to_company_api(
        message=request.message,
        api_endpoint=api_endpoint,
        api_key=api_key
    )
    
    return result


# Run with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
