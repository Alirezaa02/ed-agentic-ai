# ED Agentic AI — Pro Edition
Features: Calendar, Charts, Risk Agent, Med Checker, Timeline, Audit Logging.
## Run
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install greenlet
python seed_data.py && python train_disposition.py
uvicorn app:app --reload
