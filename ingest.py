import sys
import pandas as pd
from sqlmodel import Session
from database import engine
from models import Accident
from datetime import datetime


def parse_datetime(v):
    if pd.isna(v):
        return None
    try:
        return pd.to_datetime(v)
    except Exception:
        return None


def ingest(csv_path: str):
    df = pd.read_csv(csv_path)
    df["accident_datetime"] = df["date_time"].apply(parse_datetime)
    records = []
    for _, row in df.iterrows():
        rec = Accident(
            accident_datetime=row.get("accident_datetime") or datetime.now(),
            state=row.get("state", "") or "",
            county=row.get("county"),
            city=row.get("city"),
            road_type=row.get("road_type"),
            weather=row.get("weather_condition"),
            num_vehicles=int(row["num_vehicles"]) if pd.notna(row.get("num_vehicles")) else None,
            cause=row.get("cause"),
            severity=row.get("severity"),
            casualties=int(row["casualties"]) if pd.notna(row.get("casualties")) else None,
        )
        records.append(rec)

    with Session(engine) as session:
        session.add_all(records)
        session.commit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py path/to/data.csv")
        sys.exit(1)
    ingest(sys.argv[1])
