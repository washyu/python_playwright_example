"""
API tests for the Restful Booker API (https://restful-booker.herokuapp.com).

Restful Booker is a publicly available hotel booking API built specifically
for testing and automation practice. It provides a realistic REST API with
authentication, CRUD operations, and data filtering.

API Docs: https://restful-booker.herokuapp.com/apidoc/index.html

These tests demonstrate:
  - Session-scoped auth token management (avoids re-auth on every test)
  - Full CRUD lifecycle testing
  - Response schema validation without external libraries
  - Parameterized negative/validation testing
  - Clear separation of API interaction from assertions

Note: In a production project, base_url and credentials would come from
environment variables or a secrets manager, not be hardcoded.
"""

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
AUTH_CREDENTIALS = {"username": "admin", "password": "password123"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def auth_token() -> str:
    """
    Obtain and cache an auth token for the test session.

    Scoped to session so we only authenticate once regardless of how many
    tests run. In a CI environment this avoids hammering the auth endpoint
    and keeps runs fast.
    """
    response = requests.post(f"{BASE_URL}/auth", json=AUTH_CREDENTIALS)
    assert response.status_code == 200, (
        f"Auth failed with status {response.status_code}: {response.text}"
    )
    token = response.json().get("token")
    assert token, "Auth response did not include a token"
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    """Return standard headers with auth cookie for mutating requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }


@pytest.fixture
def created_booking(auth_headers: dict) -> dict:
    """
    Create a booking and yield its ID + data for use in a test.

    Cleans up (deletes) the booking after the test completes, ensuring
    test isolation and avoiding data accumulation on the shared API.
    """
    payload = {
        "firstname": "Test",
        "lastname": "User",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-06-01", "checkout": "2026-06-07"},
        "additionalneeds": "Breakfast",
    }
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    assert response.status_code == 200
    booking = response.json()

    yield {"id": booking["bookingid"], "data": payload}

    # Teardown: remove the booking so we don't leave test data behind
    requests.delete(
        f"{BASE_URL}/booking/{booking['bookingid']}",
        headers=auth_headers,
    )


# ---------------------------------------------------------------------------
# Auth Tests
# ---------------------------------------------------------------------------


class TestAuthentication:
    """Verify the auth endpoint behavior for valid and invalid credentials."""

    def test_auth_returns_token_for_valid_credentials(self):
        """Valid credentials should return a non-empty token."""
        response = requests.post(f"{BASE_URL}/auth", json=AUTH_CREDENTIALS)

        assert response.status_code == 200
        body = response.json()
        assert "token" in body, "Response body missing 'token' key"
        assert len(body["token"]) > 0, "Token should not be empty"

    def test_auth_fails_with_invalid_credentials(self):
        """Invalid credentials should return an error reason, not a token."""
        response = requests.post(
            f"{BASE_URL}/auth",
            json={"username": "wrong", "password": "wrong"},
        )

        assert response.status_code == 200  # API returns 200 with error body
        body = response.json()
        assert "reason" in body, "Expected error reason in response"
        assert "token" not in body, "Should not return token for bad credentials"


# ---------------------------------------------------------------------------
# GET Tests
# ---------------------------------------------------------------------------


class TestGetBookings:
    """Tests for retrieving booking data."""

    def test_get_all_bookings_returns_list(self):
        """Booking list endpoint should return a non-empty array of IDs."""
        response = requests.get(f"{BASE_URL}/booking")

        assert response.status_code == 200
        bookings = response.json()
        assert isinstance(bookings, list), "Expected a list of bookings"
        assert len(bookings) > 0, "Expected at least one booking to exist"

    def test_get_all_bookings_response_schema(self):
        """Each item in the booking list should have a bookingid field."""
        response = requests.get(f"{BASE_URL}/booking")
        bookings = response.json()

        for booking in bookings[:5]:  # Spot-check first 5 to keep it fast
            assert "bookingid" in booking, (
                f"Booking missing 'bookingid' field: {booking}"
            )
            assert isinstance(booking["bookingid"], int), (
                f"bookingid should be an int, got: {type(booking['bookingid'])}"
            )

    def test_get_booking_by_id_returns_correct_data(self, created_booking: dict):
        """Fetching a specific booking by ID should return its exact data."""
        booking_id = created_booking["id"]
        expected = created_booking["data"]

        response = requests.get(
            f"{BASE_URL}/booking/{booking_id}",
            headers={"Accept": "application/json"},
        )

        assert response.status_code == 200
        body = response.json()

        assert body["firstname"] == expected["firstname"]
        assert body["lastname"] == expected["lastname"]
        assert body["totalprice"] == expected["totalprice"]
        assert body["depositpaid"] == expected["depositpaid"]
        assert body["bookingdates"]["checkin"] == expected["bookingdates"]["checkin"]
        assert body["bookingdates"]["checkout"] == expected["bookingdates"]["checkout"]

    def test_get_nonexistent_booking_returns_404(self):
        """Requesting a booking ID that doesn't exist should return 404."""
        response = requests.get(
            f"{BASE_URL}/booking/999999999",
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "filter_params, description",
        [
            ({"firstname": "Test"}, "first name filter"),
            ({"lastname": "User"}, "last name filter"),
            (
                {"checkin": "2000-01-01", "checkout": "2099-01-01"},
                "date range filter",
            ),
        ],
    )
    def test_get_bookings_with_filter(
        self, created_booking: dict, filter_params: dict, description: str
    ):
        """
        Verify each filter parameter correctly narrows booking results.

        The created_booking fixture ensures at least one matching record exists,
        so we can assert the filtered list is non-empty.
        """
        response = requests.get(f"{BASE_URL}/booking", params=filter_params)

        assert response.status_code == 200, f"Filter by {description} failed"
        results = response.json()
        assert len(results) > 0, (
            f"Filter by {description} returned no results — expected at least one match"
        )


# ---------------------------------------------------------------------------
# POST Tests
# ---------------------------------------------------------------------------


class TestCreateBooking:
    """Tests for the booking creation endpoint."""

    def test_create_booking_returns_201_or_200(self):
        """
        Creating a valid booking should succeed.

        Note: The Restful Booker API returns 200 on creation (non-standard
        but common in older APIs). We accept both 200 and 201.
        """
        payload = {
            "firstname": "Jane",
            "lastname": "Smith",
            "totalprice": 200,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-05"},
        }
        response = requests.post(
            f"{BASE_URL}/booking",
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        assert response.status_code in (200, 201)
        body = response.json()
        assert "bookingid" in body
        assert isinstance(body["bookingid"], int)

    def test_create_booking_response_includes_submitted_data(self):
        """The creation response should echo back the submitted booking data."""
        payload = {
            "firstname": "Echo",
            "lastname": "Test",
            "totalprice": 99,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-08-01", "checkout": "2026-08-03"},
            "additionalneeds": "Late checkout",
        }
        response = requests.post(
            f"{BASE_URL}/booking",
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        assert response.status_code in (200, 201)
        body = response.json()
        booking = body["booking"]

        assert booking["firstname"] == payload["firstname"]
        assert booking["lastname"] == payload["lastname"]
        assert booking["totalprice"] == payload["totalprice"]
        assert booking["additionalneeds"] == payload["additionalneeds"]


# ---------------------------------------------------------------------------
# PUT/PATCH Tests
# ---------------------------------------------------------------------------


class TestUpdateBooking:
    """Tests for full and partial booking updates."""

    def test_full_update_replaces_booking_data(
        self, created_booking: dict, auth_headers: dict
    ):
        """PUT should replace all booking fields with the new payload."""
        booking_id = created_booking["id"]
        updated_payload = {
            "firstname": "Updated",
            "lastname": "Name",
            "totalprice": 999,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-09-01", "checkout": "2026-09-10"},
            "additionalneeds": "None",
        }

        response = requests.put(
            f"{BASE_URL}/booking/{booking_id}",
            json=updated_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["firstname"] == "Updated"
        assert body["totalprice"] == 999
        assert body["depositpaid"] is False

    def test_partial_update_changes_only_specified_fields(
        self, created_booking: dict, auth_headers: dict
    ):
        """PATCH should update only the provided fields, leaving others intact."""
        booking_id = created_booking["id"]
        original_lastname = created_booking["data"]["lastname"]

        patch_payload = {"firstname": "PatchedFirst"}

        response = requests.patch(
            f"{BASE_URL}/booking/{booking_id}",
            json=patch_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["firstname"] == "PatchedFirst"
        # Last name should be unchanged
        assert body["lastname"] == original_lastname

    def test_update_without_auth_is_rejected(self, created_booking: dict):
        """PUT without an auth token should be rejected with 403."""
        booking_id = created_booking["id"]
        payload = {
            "firstname": "Unauthorized",
            "lastname": "Attempt",
            "totalprice": 0,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
        }

        response = requests.put(
            f"{BASE_URL}/booking/{booking_id}",
            json=payload,
            headers={"Content-Type": "application/json"},  # No auth cookie
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# DELETE Tests
# ---------------------------------------------------------------------------


class TestDeleteBooking:
    """Tests for the booking deletion endpoint."""

    def test_delete_booking_succeeds_with_auth(self, auth_headers: dict):
        """
        An authenticated DELETE should remove the booking successfully.

        Creates its own booking for isolation — does not use created_booking
        fixture since that fixture handles its own cleanup.
        """
        # Create a booking specifically to delete
        payload = {
            "firstname": "Delete",
            "lastname": "Me",
            "totalprice": 1,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
        }
        create_resp = requests.post(
            f"{BASE_URL}/booking",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        booking_id = create_resp.json()["bookingid"]

        delete_resp = requests.delete(
            f"{BASE_URL}/booking/{booking_id}",
            headers=auth_headers,
        )

        assert delete_resp.status_code in (200, 201, 204)

        # Verify it's gone
        get_resp = requests.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_resp.status_code == 404

    def test_delete_without_auth_is_rejected(self, created_booking: dict):
        """Unauthenticated DELETE should be rejected with 403."""
        booking_id = created_booking["id"]

        response = requests.delete(f"{BASE_URL}/booking/{booking_id}")
        assert response.status_code == 403