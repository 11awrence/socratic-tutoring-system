set -e
# source .venv/bin/activate
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate tutor_env
uvicorn api:app --port 8000 &
chainlit run chainlit.py --port 8001
