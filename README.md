Oratio Backend - AI Bias Detection API
======================================

An AI-powered backend that analyzes text to detect biased sentences and suggests neutral, fair alternatives, helping users create more inclusive and responsible content.

Tech stack
----------
- FastAPI (Python)
- Google Gemini API (for bias detection)
- MySQL (for user management)
- SQLAlchemy (ORM)

Project layout
--------------

```
oratio_backend/
  main.py              # Single file backend with all functionality
  run.py               # Simple startup script
  setup_database.py    # MySQL database setup script
  config.py            # Configuration settings
  requirements.txt     # Dependencies
```

Quickstart
----------

1) Create and activate a virtual environment

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Setup Gemini API

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey) and set it:

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

4) Setup MySQL database

Make sure MySQL server is running, then:

```bash
python setup_database.py
```

You can configure MySQL connection in `config.py` or set environment variables:
- `MYSQL_HOST` (default: localhost)
- `MYSQL_PORT` (default: 3306)
- `MYSQL_USER` (default: root)
- `MYSQL_PASSWORD` (default: empty)
- `MYSQL_DATABASE` (default: oratio)

5) Run the server

```bash
python run.py
# OR
python main.py
```

API
---

- GET /health: Liveness check
- POST /auth/signup: User registration
- POST /auth/login: User authentication  
- GET /auth/me: Get current user info
- POST /analyze: Analyze text and return biased spans and neutral rewrites

Example request
---------------

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"The crazy old man couldn't understand simple tech."}'
```

Example response
----------------

```json
{
  "original_text": "The crazy old man couldn't understand simple tech.",
  "summary": {
    "biased_count": 1,
    "score": 0.61
  },
  "sentences": [
    {
      "sentence": "The crazy old man couldn't understand simple tech.",
      "biased_spans": [
        {"text": "crazy", "start": 4, "end": 9, "type": "ableist"}
      ],
      "suggestion": "The man had difficulty with the technology."
    }
  ]
}
```

Notes
-----
- This project uses Google's Gemini API for comprehensive bias detection
- Provides advanced AI-powered analysis of various bias types (gender, racial, ageist, ableist, etc.)
- Uses MySQL with SQLAlchemy ORM for user management
- All functionality is contained in a single main.py file for simplicity
- Requires Gemini API key and MySQL server to be running
