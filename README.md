# Accident Trends Prototype

This prototype implements a minimal FastAPI backend with a SQLite database and a simple static dashboard to visualize yearly accident trends. It is intended as a starting point for the project described: tracking rising trends in car accidents with filtering, visualization, and forecasting.

Quick start (macOS, zsh):

1. Create and activate a Python environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

3. Open the dashboard:

Visit `http://127.0.0.1:8000/` in your browser.

4. Ingest the sample data (optional):

```bash
python ingest.py data/sample_data.csv
```

Files added:
- `main.py` — FastAPI app and routes
- `models.py` — SQLModel data model for accidents
- `database.py` — SQLite engine and helpers
- `ingest.py` — CSV ingestion script
- `static/index.html` — simple dashboard (Chart.js)
- `data/sample_data.csv` — small sample dataset
- `requirements.txt` — Python dependencies

Next steps:
- Add authentication and role-based access for researchers and policymakers
- Expand frontend with React for advanced filtering and map visualizations
- Add production DB (Postgres) and migrations
- Add forecasting improvements (time-series models)

If you want, I can run the server here, add tests, or expand the frontend into a React app. Which should I do next?
