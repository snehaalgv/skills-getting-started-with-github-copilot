"""
Tests for the Mergington High School Activities API (FastAPI application)
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and regional tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in school concerts",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore advanced scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities"""
        # Arrange: No setup needed for this test
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that each activity includes required fields"""
        # Arrange: No setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert response.status_code == 200
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_includes_participant_list(self, client, reset_activities):
        """Test that participant list is included in activity data"""
        # Arrange: No setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data["Chess Club"]["participants"], list)
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert email in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert email in data[activity_name]["participants"]

    def test_signup_duplicate_student_returns_error(self, client, reset_activities):
        """Test that signing up twice returns an error"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]

    def test_signup_already_registered_student_error(self, client, reset_activities):
        """Test that existing participant cannot sign up again"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for nonexistent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]

    def test_signup_valid_email_format(self, client, reset_activities):
        """Test signup with various valid email formats"""
        # Arrange
        activity_name = "Gym Class"
        email = "john.doe@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities_response = client.get("/activities")
        data = activities_response.json()
        
        # Assert
        assert response.status_code == 200
        assert email in data[activity_name]["participants"]

    def test_signup_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        # Arrange
        student_email = "multi@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Art Studio"
        
        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={student_email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={student_email}")
        data = client.get("/activities").json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student_email in data[activity1]["participants"]
        assert student_email in data[activity2]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert email not in data[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_error(self, client, reset_activities):
        """Test that unregistering a non-signed-up student returns an error"""
        # Arrange
        activity_name = "Chess Club"
        email = "notsignup@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregistering from nonexistent activity returns 404"""
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]

    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants from same activity"""
        # Arrange
        activity_name = "Music Band"
        emails = ["lucas@mergington.edu", "ava@mergington.edu"]
        
        # Act
        client.delete(f"/activities/{activity_name}/signup?email={emails[0]}")
        client.delete(f"/activities/{activity_name}/signup?email={emails[1]}")
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data[activity_name]["participants"]) == 0

    def test_unregister_then_resign_allowed(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        # Arrange
        activity_name = "Tennis Club"
        student_email = "flexible@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup?email={student_email}")
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        
        # Act - Sign up again
        signin_response = client.post(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        
        # Assert
        assert unregister_response.status_code == 200
        assert signin_response.status_code == 200
