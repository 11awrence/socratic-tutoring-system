# Setup

This page explains how to run the current prototype locally.

## Requirements

- Python 3.10+
- Apple Silicon recommended if using the local MLX backend
- The models expected by `socratic_tutor.py` already available on the machine

## Hardware requirements

This version runs on Apple Silicon using MLX. 

## Models

- Orchestrator / MathTutor / Metacognitive: [Qwen3.5-122B-A10B-4bit](https://huggingface.co/mlx-community/Qwen3.5-122B-A10B-4bit)
- Affective: [Qwen2.5-3B](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)

## Installation

```bash
git clone https://github.com/11awrence/socratic-tutoring-system.git
cd socratic-tutoring-system

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env # set ORCHESTRATOR_MODEL and AFFECTIVE_MODEL
```

For conda environment
```bash
git clone https://github.com/11awrence/socratic-tutoring-system.git
cd socratic-tutoring-system

conda create -n tutor_env python=3.10
conda activate tutor_env
pip install -r requirements.txt

cp .env.example .env
# set ORCHESTRATOR_MODEL and AFFECTIVE_MODEL
```

## Running the system

The system is split into an API backend and a Chainlit frontend. 
You can run the system with run.sh if you are using conda environment:
```bash
conda activate tutor_env
bash run.sh
```

If not, you can use two terminals:

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
- The backend expects local MLX models if `PROVIDER=mlx`. If you are not on Apple Silicon, the model-loading code will need to be adapted.
- The frontend talks to the API through http://localhost:8000/turn.
- Use New Problem in the UI to reset a session cleanly during testing.
- `PROVIDER=openai` / `mock` exist in `.env` OpenAI is a placeholder unless you implement the API call in generate_response. mock needs no model. Neither was used for the ablation.

## Project layout
- socratic_tutor.py — LangGraph multi-agent backend
- api.py — FastAPI endpoint
- chainlit.py — Chainlit UI
- .env.example - environment for setting up local or cloud models
