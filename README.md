# US Car Accident Trends Dashboard

A Flask web application for tracking and analyzing US car accident trends with a MySQL backend. Features include accident data filtering, yearly trend visualization, cause analysis, and form-based data entry.

## Quick Start (macOS, zsh)

### Prerequisites
- Python 3.10+
- MySQL server running on localhost:3306
- Database `Accidents_Database` with table `NHTSA_NATIONAL_STATS`

### Setup

1. Create and activate a Python environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the Flask server:

```bash
python3 App.py
```

The server runs on `http://127.0.0.1:5000`

3. Open the dashboard:

Visit `http://127.0.0.1:5000/` in your browser.

## Features

- **Search & Filter**: Query accidents by state, year, and severity
- **Add Records**: Insert new accident records via the web form
- **Yearly Trends**: View accident counts and fatalities by year
- **Factor Analysis**: Analyze accidents by cause
- **Real-time Updates**: All data persisted to MySQL

## Project Structure

- `App.py` — Flask application with CORS and all API endpoints
- `static/index.html` — Interactive dashboard with forms and charts
- `requirements.txt` — Python dependencies (Flask, Flask-CORS, mysql-connector-python)

## API Endpoints

- `GET /` — Serve the dashboard
- `GET /accidents?state=...&year=...&severity=...` — Filter accident records
- `POST /accidents/form` — Add a new accident record
- `GET /trends/yearly` — Get yearly accident statistics
- `GET /statistics/factors` — Get accidents aggregated by cause

## Database Schema

Table: `NHTSA_NATIONAL_STATS`

Columns: `stat_id`, `year`, `state`, `severity`, `num_vehicles`, `accident_datetime`, and various casualty/statistic fields.

## Next Steps

- Add authentication and user roles
- Expand frontend with advanced visualizations (maps, heatmaps)
- Add forecasting models for trend prediction
- Implement data export functionality (CSV, PDF)
- Add unit and integration tests
