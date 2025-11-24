# Accident Trends Prototype
Our application is the rising trend in the number of car accidents that have happened in the US per year. Its purpose is to help researchers, policymakers, transportation departments, and the public understand patterns, causes, and rising trends in car accidents. This is useful because policymakers can use the data to design safer roads and traffic laws, transportation agencies can identify high-risk areas, and the general public can gain awareness of accident trends and contributing factors. There are similar applications like NHTSA’s Fatality Analysis Reporting System which provides raw crash data, and the Insurance Institute for Highway Safety or IIHS, which publishes car crash statistics. However, our application will provide the information by query such as year, state, cause and severity. The application will combine multiple factors such as year, location, cause, weather, and vehicle type in one place. The application will provide visual analytics such as graphs and charts of yearly trends. Our data will be accident ID, date and time, state, county, city, road type, weather condition, number of vehicles involved, cause, severity, and casualties. We will get our data from NHTSA’s Fatality Analysis Reporting System, Bureau of Transportation Statistics, Insurance Institute for Highway Safety or IIHS and the State Department of Transportation.

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
