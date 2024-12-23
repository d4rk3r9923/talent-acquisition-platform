set -a && source .env && source PYTHONPATH=. && set +a
streamlit run frontend/chat.py
# uvicorn main:app --host 0.0.0.0 --port:8000 --reload
