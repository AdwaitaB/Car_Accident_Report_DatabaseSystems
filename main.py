from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
import pandas as pd

from database import init_db, get_session
from models import Accident

app = FastAPI(title="Accident Trends API")

# serve static files (CSS/JS/assets) and make dashboard available
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return FileResponse("static/index.html")


@app.post("/accidents/form", response_model=Accident)
async def create_accident_from_form(request: Request, session=Depends(get_session)):
    """Accepts JSON payload from the dashboard form and creates an Accident record.

    Expected keys: `accident_date` (YYYY-MM-DD), optional `accident_time` (HH:MM),
    `state`, `county`, `city`, `total_vehicles`, `total_casualties`, `primary_cause`, `description`.
    """
    payload = await request.json()
    date = payload.get("accident_date")
    time = payload.get("accident_time") or "00:00"
    try:
        # combine date and time into a datetime
        dt = datetime.fromisoformat(f"{date}T{time}")
    except Exception:
        dt = datetime.now()

    acc = Accident(
        accident_datetime=dt,
        state=payload.get("state", "") or "",
        county=payload.get("county"),
        city=payload.get("city"),
        num_vehicles=int(payload.get("total_vehicles")) if payload.get("total_vehicles") not in (None, "") else None,
        casualties=int(payload.get("total_casualties")) if payload.get("total_casualties") not in (None, "") else None,
        cause=payload.get("primary_cause"),
        description=payload.get("description"),
    )
    session.add(acc)
    session.commit()
    session.refresh(acc)
    return acc


@app.post("/accidents", response_model=Accident)
def create_accident(accident: Accident, session=Depends(get_session)):
    session.add(accident)
    session.commit()
    session.refresh(accident)
    return accident


@app.get("/accidents", response_model=List[Accident])
def list_accidents(
    state: Optional[str] = None,
    year: Optional[int] = None,
    weather: Optional[str] = None,
    cause: Optional[str] = None,
    severity: Optional[str] = None,
    q: Optional[str] = Query(None, description="free text search in city/county/cause"),
    session=Depends(get_session),
):
    stmt = select(Accident)
    if state:
        stmt = stmt.where(Accident.state == state)
    if year:
        stmt = stmt.where(Accident.accident_datetime >= datetime(year, 1, 1))
        stmt = stmt.where(Accident.accident_datetime < datetime(year + 1, 1, 1))
    if weather:
        stmt = stmt.where(Accident.weather == weather)
    if cause:
        stmt = stmt.where(Accident.cause == cause)
    if severity:
        stmt = stmt.where(Accident.severity == severity)
    if q:
        likeq = f"%{q}%"
        stmt = stmt.where(
            (Accident.city.ilike(likeq)) | (Accident.county.ilike(likeq)) | (Accident.cause.ilike(likeq))
        )
    results = session.exec(stmt).all()
    return results


@app.get("/accidents/{accident_id}", response_model=Accident)
def get_accident(accident_id: int, session=Depends(get_session)):
    acc = session.get(Accident, accident_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Accident not found")
    return acc


@app.put("/accidents/{accident_id}", response_model=Accident)
def update_accident(accident_id: int, accident: Accident, session=Depends(get_session)):
    db = session.get(Accident, accident_id)
    if not db:
        raise HTTPException(status_code=404, detail="Not found")
    accident.id = accident_id
    session.merge(accident)
    session.commit()
    session.refresh(accident)
    return accident


@app.delete("/accidents/{accident_id}")
def delete_accident(accident_id: int, session=Depends(get_session)):
    db = session.get(Accident, accident_id)
    if not db:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(db)
    session.commit()
    return {"ok": True}


@app.get("/trends/yearly")
def yearly_trends(session=Depends(get_session)):
    stmt = select(Accident)
    rows = session.exec(stmt).all()
    if not rows:
        return {"years": [], "counts": []}
    df = pd.DataFrame([{
        "datetime": r.accident_datetime,
    } for r in rows])
    df["year"] = pd.DatetimeIndex(df["datetime"]).year
    counts = df.groupby("year").size().sort_index()
    return {"years": counts.index.tolist(), "counts": counts.tolist()}


@app.get("/forecast")
def forecast_years(years_ahead: int = 5, session=Depends(get_session)):
    # Simple forecasting using linear regression on yearly totals
    from sklearn.linear_model import LinearRegression
    import numpy as np

    trend = yearly_trends(session=session)
    if not trend["years"]:
        return {"forecast_years": [], "forecast_counts": []}
    X = np.array(trend["years"]).reshape(-1, 1)
    y = np.array(trend["counts"]) 
    model = LinearRegression()
    model.fit(X, y)
    last = max(trend["years"])
    future_years = [last + i for i in range(1, years_ahead + 1)]
    preds = model.predict(np.array(future_years).reshape(-1, 1)).tolist()
    return {"forecast_years": future_years, "forecast_counts": [max(0, float(p)) for p in preds]}
