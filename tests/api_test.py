from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app import api
from src.models.hydration_tracker import HydrationTracker
from src.models.user import CreateUser, User

client = TestClient(api)


@pytest.fixture
def user():
    response = client.post("/user/", json=CreateUser(name="John Doe", weight=65).model_dump())
    assert response.status_code == 201
    created_user = User.model_validate(response.json())
    yield created_user
    client.delete(f"/user/{created_user.id}/")


@pytest.fixture
def tracker(user):
    response = client.get(f"/user/{user.id}/tracker/")
    assert response.status_code == 200
    return HydrationTracker.model_validate(response.json())


def test_hello_world():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_create_user(user):
    assert user.id
    assert user.name == "John Doe"


def test_get_user(user):
    response = client.get(f"/user/{user.id}/")

    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_list_users(user):
    response = client.get("/users/")

    assert response.status_code == 200
    assert any(item["id"] == user.id for item in response.json())


def test_today_tracker(tracker, user):
    assert tracker.id_owner == user.id
    assert tracker.goal > 0


def test_get_tracker(user, tracker):
    response = client.get(f"/user/{user.id}/tracker/{tracker.date}/")

    assert response.status_code == 200
    assert response.json()["id"] == tracker.id


def test_update_tracker(user, tracker):
    response = client.put(
        f"/user/{user.id}/tracker/{tracker.date}/",
        json={"cupsize": 2000},
    )

    assert response.status_code == 200
    assert response.json()["consumed"] == 2000


def test_create_specific_tracker(user, tracker):
    tracker_date = tracker.date - timedelta(days=1)
    response = client.post(f"/user/{user.id}/tracker/{tracker_date}/")

    assert response.status_code == 200
    assert response.json()["id_owner"] == user.id


def test_list_trackers(user, tracker):
    response = client.get(f"/user/{user.id}/history/")

    assert response.status_code == 200
    assert any(item["id"] == tracker.id for item in response.json())
