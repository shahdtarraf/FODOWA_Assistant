# FAQ Chatbot Backend

A lightweight, production-ready FAQ chatbot built with FastAPI. Designed for Render Free Tier (512MB RAM).

**NO Machine Learning** - Uses pure Python with keyword matching, substring matching, and fuzzy matching (difflib).

## Features

- 🚀 Instant startup (<2 seconds)
- 💾 Low memory usage (<100MB)
- 🔍 Fuzzy matching with difflib
- 🎨 Beautiful chat UI
- 📊 In-memory request logging
- ✅ Automated tests with pytest

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── chatbot.py       # Matching engine with difflib
│   ├── validator.py     # Validation system
│   └── logger.py        # Request logging
├── data/
│   └── faq.json         # FAQ database
├── static/
│   └── index.html       # Chat UI
├── tests/
│   └── test_main.py     # Automated tests
├── requirements.txt
├── Dockerfile
└── README.md
```

## Quick Start

### 1. Create Virtual Environment

```bash
# Mac/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Check Memory Usage

```bash
python check_memory.py
```

### 5. Run Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000 for the chat UI.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Chat UI (HTML) |
| GET | `/health` | Health check |
| POST | `/chat` | Get chatbot response |
| POST | `/validate` | Detailed match analysis |
| GET | `/logs` | View request logs |
| GET | `/docs` | Swagger UI |

### POST /chat

**Request:**
```json
{
  "question": "What are your business hours?"
}
```

**Response:**
```json
{
  "answer": "Our business hours are Monday to Friday...",
  "confidence": 0.85,
  "matched_question": "What are your business hours?"
}
```

## Deploy to Render

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/faq-chatbot.git
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to [render.com](https://render.com) and sign up/login
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| Name | `faq-chatbot` |
| Region | Choose closest |
| Branch | `main` |
| Runtime | **Docker** |
| Instance Type | **Free** |

### Step 3: Deploy

Click **Create Web Service**. Render will automatically:
- Build the Docker image
- Deploy to port 10000
- Provide a URL like `https://faq-chatbot.onrender.com`

## Build & Start Commands (if not using Docker)

If using **Native** runtime instead of Docker:

| Command Type | Command |
|--------------|---------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port 10000` |

## Environment Variables

No environment variables required for basic operation.

## Customizing FAQ

Edit `data/faq.json` to add your own questions:

```json
{
  "faq_entries": [
    {
      "id": 1,
      "question": "Your question here?",
      "answer": "Your answer here.",
      "keywords": ["keyword1", "keyword2"]
    }
  ],
  "fallback_response": "I'm sorry, I don't have information about that."
}
```

## License

MIT
