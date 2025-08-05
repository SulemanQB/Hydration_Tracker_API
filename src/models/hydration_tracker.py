from pydantic import BaseModel
from datetime import date
from typing import Optional
from bson import ObjectId

class CreateHydrationTracker(BaseModel):
    id_owner: str
    weight_at_time: int
    date: date
    goal: int
    missing: int
    consumed: int
    goal_percent: float
    goal_reached: bool

class HydrationTracker(CreateHydrationTracker):
    id: Optional[str]
