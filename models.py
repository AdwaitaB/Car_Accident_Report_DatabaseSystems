from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Accident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    accident_datetime: datetime
    state: str
    county: Optional[str] = None
    city: Optional[str] = None
    road_type: Optional[str] = None
    weather: Optional[str] = None
    num_vehicles: Optional[int] = None
    cause: Optional[str] = None
    severity: Optional[str] = None
    casualties: Optional[int] = None
    description: Optional[str] = None
