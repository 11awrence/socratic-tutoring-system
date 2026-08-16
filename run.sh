set -e
source .venv/bin/activate
uvicorn api:app --port 8000 &
chainlit run chainlit.py --port 8001
