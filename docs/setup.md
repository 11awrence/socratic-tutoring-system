# Setup

This page explains how to run the current prototype locally.

## Requirements

- Python 3.10+
- Apple Silicon recommended if using the local MLX backend
- The models expected by `socratic_tutor.py` already available on the machine

## Installation

```bash
git clone https://github.com/11awrence/socratic-tutoring-system.git
cd socratic-tutoring-system

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Running the system

The system is split into an API backend and a Chainlit frontend.
Run them in two separate terminals.

### Terminal 1 — API

```bash
uvicorn api:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
chainlit run chainlit.py --port 8001
```
Then open the URL shown by Chainlit, usually:

```
http://localhost:8001
```

## Notes
- The backend expects local MLX models. If you are not on Apple Silicon, the model-loading code will need to be adapted.
- The frontend talks to the API through http://localhost:8000/turn.
- Use New Problem in the UI to reset a session cleanly during testing.

## Project layout
- socratic_tutor.py — LangGraph multi-agent backend
- api.py — FastAPI endpoint
- chainlit.py — Chainlit UI
- app.py — optional alternative frontend entry

Once this is in, the documentation skeleton is complete.  
Then you can push the docs and, if you want, set up GitHub Pages later.
