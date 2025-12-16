import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Check that we have activities
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Use an activity that starts empty
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Basketball Team" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Basketball Team"]["participants"]


def test_signup_duplicate():
    """Test signing up for the same activity twice"""
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up
    client.post("/activities/Art%20Club/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Art%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Art Club" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Art Club"]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering a student who is not signed up"""
    response = client.delete("/activities/Drama%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]


def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test root endpoint redirects to static page"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI TestClient follows redirects by default, so we get the HTML content
    assert "Mergington High School" in response.text