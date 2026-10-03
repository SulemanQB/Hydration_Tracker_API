from pydantic import BaseModel, Field
from typing import Optional

class CreateUser(BaseModel):
    """Input required to create a hydration-tracker user."""

    name: str = Field(..., min_length=1, max_length=100)
    weight: int = Field(..., gt=0, le=500, description="Body weight in kilograms")


class UpdateUser(BaseModel):
    """Fields that may be changed on an existing user."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    weight: Optional[int] = Field(None, gt=0, le=500, description="Body weight in kilograms")


class User(CreateUser):
    """Public user representation returned by the API."""

    id: Optional[str]
