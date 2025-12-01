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

- **Search & Filter**: Query accidents by year and fatality/crash metrics
- **Add Records**: Insert new accident records via the web form
- **Edit Records**: Update existing records with new data
- **Delete Records**: Remove records from the database
- **Yearly Trends**: View accident counts and fatalities by year
- **Factor Analysis**: Analyze accidents by top fatality years
- **Forecasting**: Predict future fatalities using linear regression
- **Simulation**: Run what-if scenarios with custom fatality rate and population changes
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
- `GET /accidents/<stat_id>` — Fetch a single national statistics record by its `stat_id`. Returns `200` with the record or `404` if not found.
- `PUT /accidents/<stat_id>` — Update a national statistics record. Accepts a JSON body with any updatable fields (e.g., `year`, `total_fatalities`, `fatal_crashes`, etc.). Returns `200` on success, `404` if record not found, or `409` if attempting to update `year` to a value already used by another record.
- `DELETE /accidents/<stat_id>` — Delete a national statistics record by its `stat_id`. Returns `200` on success or `404` if the record is not found.

### Examples

**Fetch a single record:**

```bash
curl -i http://127.0.0.1:5000/accidents/123
```

Response on success:

```json
HTTP/1.1 200 OK
{
  "stat_id": 123,
  "year": 2023,
  "total_fatalities": 42514,
  "fatal_crashes": 39107,
  "drivers_killed": 21564,
  "licensed_drivers": 228000000,
  "resident_population": 333287557
}
```

**Update a record:**

```bash
curl -i -X PUT http://127.0.0.1:5000/accidents/123 \
  -H "Content-Type: application/json" \
  -d '{"total_fatalities": 42500, "fatal_crashes": 39050}'
```

Response on success:

```json
HTTP/1.1 200 OK
{
  "success": true,
  "updated_id": 123
}
```

Response if year conflicts with another record:

```json
HTTP/1.1 409 Conflict
{
  "error": "Another record already uses year 2022"
}
```

**Delete a record:**

```bash
curl -i -X DELETE http://127.0.0.1:5000/accidents/123
```

Response on success:

```json
HTTP/1.1 200 OK
{
  "success": true,
  "deleted_id": 123
}
```

## Database Schema

Table: `NHTSA_NATIONAL_STATS`

Columns: `stat_id`, `year`, `state`, `severity`, `num_vehicles`, `accident_datetime`, and various casualty/statistic fields.

## Next Steps

- Add authentication and user roles
- Expand frontend with advanced visualizations (maps, heatmaps)
- Add forecasting models for trend prediction
- Implement data export functionality (CSV, PDF)
- Add unit and integration tests
