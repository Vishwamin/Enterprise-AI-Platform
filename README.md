# Enterprise AI Knowledge Platform

An internal enterprise RAG platform: employees securely ask questions about
company documents and get grounded answers with citations.

This project is being built **phase by phase**, as a learning-while-building
exercise. See `PHASE.md` for what's currently implemented, `architecture.md`
for the system design, and `requirements.md` for the functional/non-functional
requirements driving it.

## Current status: Phase 2 — Configuration & Engineering Foundations

Centralized settings, structured logging, and consistent error handling
now sit underneath the same three endpoints from Phase 1. Still no
database, no auth, no AI — those come in later phases. See `PHASE.md`
for details.

## Quickstart

```bash
# 1. Create and activate a virtual environment (from inside this folder)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. (optional) copy the example env file — defaults work fine without it
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# 4. Run the app
uvicorn app.main:app --reload

# 5. Open the interactive docs
# http://127.0.0.1:8000/docs
```

## Project structure

```text
enterprise-ai-platform/
├── app/
│   ├── main.py             # FastAPI app entrypoint, global exception handler
│   ├── api/
│   │   └── v1/
│   │       ├── health.py   # GET /health, GET /
│   │       └── ask.py      # POST /api/v1/ask
│   ├── schemas/
│   │   └── ask.py          # Pydantic request/response models
│   └── core/
│       ├── config.py        # centralized Settings (Phase 2)
│       └── logging.py       # logging setup (Phase 2)
├── tests/
│   ├── test_health.py
│   ├── test_root.py
│   ├── test_ask.py
│   ├── test_config.py       # Phase 2
│   └── test_error_handling.py  # Phase 2
├── requirements.md           # Phase 0
├── architecture.md           # Phase 0
├── PHASE.md                  # what's in THIS phase
├── requirements.txt          # Python dependencies
├── .env.example
└── .gitignore
```

## Running tests

```bash
pytest
```
