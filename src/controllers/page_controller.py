from flask import Blueprint, render_template
from datetime import date
import requests
from config.settings import settings

page_blueprint = Blueprint('page', __name__)
API_BASE_URL = settings.API_BASE_URL.rstrip('/')

def _get_json(path):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=5)
    response.raise_for_status()
    return response.json()


def get_user_from_api(user_id):
    return _get_json(f"/user/{user_id}/")

def get_tracker_from_api(user_id, tracker_date=None):
    if tracker_date is None:
        tracker_date = date.today().strftime("%Y-%m-%d")
        return _get_json(f"/user/{user_id}/tracker/")
    return _get_json(f"/user/{user_id}/tracker/{tracker_date}/")

def get_history_from_api(user_id):
    return _get_json(f"/user/{user_id}/history/")

@page_blueprint.route("/")
def home_page():
    return render_template("home_page.html")

@page_blueprint.route("/error")
def error_page():
    return render_template("error.html")

@page_blueprint.route("/<user_id>/tracker/<tracker_date>")
def user_tracker_page(user_id, tracker_date=None):
    try:
        tracker = get_tracker_from_api(user_id, tracker_date)
        user = get_user_from_api(user_id)
    except requests.RequestException:
        return render_template("error.html", message="Error connecting to API")
    
    return render_template("tracker.html", user=user, entry=tracker)

@page_blueprint.route("/<user_id>/tracker/")
def user_today_tracker_page(user_id):
    return user_tracker_page(user_id, None)

@page_blueprint.route("/<user_id>/history/")
def user_history_page(user_id):
    try:
        trackers = get_history_from_api(user_id)
        user = get_user_from_api(user_id)
    except requests.RequestException:
        return render_template("error.html", message="Error connecting to API")
    
    return render_template("history.html", user=user, entries=trackers)