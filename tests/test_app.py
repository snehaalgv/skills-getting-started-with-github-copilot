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
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that each activity includes required fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_includes_participant_list(self, client, reset_activities):
        """Test that participant list is included in activity data"""
        response = client.get("/activities")
        data = response.json()
        
        assert isinstance(data["Chess Club"]["participants"], list)
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_duplicate_student_returns_error(self, client, reset_activities):
        """Test that signing up twice returns an error"""
        # First signup
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Second signup with same email
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_already_registered_student_error(self, client, reset_activities):
        """Test that existing participant cannot sign up again"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_valid_email_format(self, client, reset_activities):
        """Test signup with various valid email formats"""
        response = client.post(
            "/activities/Gym Class/signup?email=john.doe@mergington.edu"
        )
        
        assert response.status_code == 200
        assert "john.doe@mergington.edu" in client.get("/activities").json()["Gym Class"]["participants"]

    def test_signup_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        student_email = "multi@mergington.edu"
        
        response1 = client.post(f"/activities/Chess Club/signup?email={student_email}")
        response2 = client.post(f"/activities/Art Studio/signup?email={student_email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data = client.get("/activities").json()
        assert student_email in data["Chess Club"]["participants"]
        assert student_email in data["Art Studio"]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_returns_error(self, client, reset_activities):
        """Test that unregistering a non-signed-up student returns an error"""
        response = client.delete(
            "/activities/Chess Club/signup?email=notsignup@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants from same activity"""
        client.delete("/activities/Music Band/signup?email=lucas@mergington.edu")
        client.delete("/activities/Music Band/signup?email=ava@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Music Band"]["participants"]) == 0

    def test_unregister_then_resign_allowed(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        student_email = "flexible@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Tennis Club/signup?email={student_email}")
        
        # Unregister
        response1 = client.delete(
            f"/activities/Tennis Club/signup?email={student_email}"
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            f"/activities/Tennis Club/signup?email={student_email}"
        )
        assert response2.status_code == 200
