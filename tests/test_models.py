from datetime import date

import pytest
from pydantic import ValidationError

from src.models.hydration_tracker import HydrationTracker
from src.models.user import CreateUser, UpdateUser


def test_user_requires_a_positive_realistic_weight():
    user = CreateUser(name="Ada", weight=65)

    assert user.name == "Ada"
    assert user.weight == 65

    with pytest.raises(ValidationError):
        CreateUser(name="Ada", weight=0)


def test_user_updates_validate_only_supplied_fields():
    assert UpdateUser(weight=70).model_dump(exclude_unset=True) == {"weight": 70}

    with pytest.raises(ValidationError):
        UpdateUser(weight=0)


def test_tracker_accepts_a_valid_daily_measurement():
    tracker = HydrationTracker(
        id="tracker-id",
        id_owner="user-id",
        weight_at_time=65,
        date=date(2026, 9, 29),
        goal=2275,
        missing=1025,
        consumed=1250,
        goal_percent=54.95,
        goal_reached=False,
    )

    assert tracker.date == date(2026, 9, 29)
    assert tracker.missing >= 0