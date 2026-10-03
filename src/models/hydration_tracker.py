from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class CreateHydrationTracker(BaseModel):
    """Hydration measurements stored for one user and calendar date."""

    id_owner: str
    weight_at_time: int = Field(..., gt=0)
    date: date
    goal: int = Field(..., gt=0)
    missing: int = Field(..., ge=0)
    consumed: int = Field(..., ge=0)
    goal_percent: float = Field(..., ge=0)
    goal_reached: bool


class HydrationTracker(CreateHydrationTracker):
    """Public hydration tracker representation returned by the API."""

    id: Optional[str]


class ConsumeUpdate(BaseModel):
    """Amount of water to add to a tracker's consumed total."""

    cupsize: float = Field(..., gt=0, allow_inf_nan=False)
