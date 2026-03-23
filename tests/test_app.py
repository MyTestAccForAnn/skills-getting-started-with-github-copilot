"""
Tests for the Mergington High School API

Tests are structured using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test fixtures and preconditions
- Act: Execute the API call
- Assert: Verify the response and behavior
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a TestClient for the application"""
    return TestClient(app)


# ============================================================================
# GET /activities - Retrieve all available activities
# ============================================================================

def test_get_activities_returns_all_activities(client):
    """
    Arrange: TestClient is ready
    Act: GET /activities
    Assert: Returns 200 with all activities in the dictionary
    """
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_get_activities_returns_correct_structure(client):
    """
    Arrange: TestClient is ready
    Act: GET /activities
    Assert: Returns activities with expected field structure
    """
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    
    # Verify each activity has the required fields
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


# ============================================================================
# GET / - Root endpoint redirect
# ============================================================================

def test_root_redirects_to_static_index(client):
    """
    Arrange: TestClient is ready
    Act: GET /
    Assert: Returns 302 redirect to /static/index.html
    """
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ============================================================================
# POST /activities/{activity_name}/signup - Sign up for an activity
# ============================================================================

def test_signup_success_adds_participant(client):
    """
    Arrange: Valid activity name and new email address
    Act: POST /activities/Chess Club/signup with new email
    Assert: Returns 200, email is added to participants list
    """
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )
    
    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Signed up" in response.json()["message"]
    
    # Verify the email was actually added to participants
    activities = client.get("/activities").json()
    assert new_email in activities[activity_name]["participants"]


def test_signup_activity_not_found_returns_404(client):
    """
    Arrange: Invalid activity name
    Act: POST /activities/Nonexistent Activity/signup
    Assert: Returns 404 with "Activity not found" error
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_enrolled_returns_400(client):
    """
    Arrange: Valid activity and email already in participants list
    Act: POST /activities/Chess Club/signup with existing participant email
    Assert: Returns 400 with "already signed up" error
    """
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # Already in Chess Club participants
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ============================================================================
# DELETE /activities/{activity_name}/unregister - Unregister from an activity
# ============================================================================

def test_unregister_success_removes_participant(client):
    """
    Arrange: Valid activity name and email currently enrolled
    Act: DELETE /activities/Chess Club/unregister with existing participant
    Assert: Returns 200, email is removed from participants list
    """
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"  # Currently enrolled
    
    # Verify email is in participants before unregister
    activities_before = client.get("/activities").json()
    assert participant_email in activities_before[activity_name]["participants"]
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": participant_email}
    )
    
    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Unregistered" in response.json()["message"]
    
    # Verify the email was actually removed from participants
    activities_after = client.get("/activities").json()
    assert participant_email not in activities_after[activity_name]["participants"]


def test_unregister_activity_not_found_returns_404(client):
    """
    Arrange: Invalid activity name
    Act: DELETE /activities/Nonexistent Activity/unregister
    Assert: Returns 404 with "Activity not found" error
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{invalid_activity}/unregister",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_enrolled_returns_400(client):
    """
    Arrange: Valid activity and email NOT in participants list
    Act: DELETE /activities/Tennis Club/unregister with non-participant email
    Assert: Returns 400 with "not signed up" error
    """
    # Arrange
    activity_name = "Tennis Club"
    non_enrolled_email = "nobody@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": non_enrolled_email}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
