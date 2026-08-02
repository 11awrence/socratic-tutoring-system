# Multi-Agent Socratic Tutoring System

Full-stack multi-agent math tutoring system built with LangGraph.  
It combines Socratic dialogue, metacognitive reflection, and lightweight affective scaffolding.

## Current Version

- `socratic_tutor.py` — core LangGraph multi-agent backend
- `api.py` — FastAPI layer
- `chainlit.py` — Chainlit frontend

## Features

- Multi-agent architecture (Orchestrator, MathTutor, Metacognitive, Affective)
- Socratic step-by-step guidance instead of direct answers
- Metacognitive reflection after problem solving
- Affective signal that influences tutoring tone
- Clean separation between reasoning backend and UI

## Installation

```bash
git clone https://github.com/11awrence/socratic-tutoring-system.git
cd socratic-tutoring-system

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> Note: This project uses local MLX models. Make sure the required models are available on your machine and that you are running on Apple Silicon (or adjust the model loading code accordingly).

## Running the System
You need two terminals:
Terminal 1 – Start the API
```bash
uvicorn api:app --reload --port 8000
```
Terminal 2 – Start the Chainlit frontend
```bash
chainlit run chainlit.py --port 8001
```
Then open the URL shown by Chainlit (usually http://localhost:8001).

## Status
This version focuses on a working prompt-driven multi-agent tutoring loop with a usable UI.
It demonstrates both the strengths and the current limits of relying primarily on prompting for agent coordination and state tracking.

## Future Work
- Stronger deterministic routing (less reliance on LLM decisions)
- Better progress / current-step tracking
- Improved affective adaptation
- Optional multimodal inputs
