
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db


@pytest.fixture
def client():
    # Create a separate in-memory SQLite database for testing
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    # Create tables in the test database
    Base.metadata.create_all(bind=test_engine)

    # Override the application's database dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Start the application and provide the test client
    with TestClient(app) as test_client:
        yield test_client

    # Clean up after the test
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.mark.parametrize(
    "title, description, expected_result, expected_status",
    [
        (
            "Valid login test",
            "Test valid login credentials",
            "User reaches dashboard",
            201,
        ),
        (
            "Invalid password test",
            "Test incorrect password",
            "Login is rejected",
            201,
        ),
        (
            "",
            "Test missing title",
            "Validation error expected",
            422,
        ),
        (
            "Empty expected result",
            "Test missing expected result",
            "",
            422,
        ),
        (
            "x" * 201,
            "Test title exceeding maximum length",
            "Validation error expected",
            422,
        ),
    ],
)
def test_create_test_case_inputs(
    client, title, description, expected_result, expected_status
):
    response = client.post(
        "/test-cases",
        json={
            "title": title,
            "description": description,
            "expected_result": expected_result,
        },
    )

    assert response.status_code == expected_status

    # For successful requests, verify the returned data
    if expected_status == 201:
        response_data = response.json()
        assert response_data["title"] == title
        assert response_data["expected_result"] == expected_result

#CRUD operations

def test_test_case_crud_workflow(client):
    # 1. CREATE a test case
    create_response = client.post(
        "/test-cases",
        json={
            "title": "Login functionality test",
            "description": "Verify that a user can log in",
            "expected_result": "User reaches the dashboard",
        },
    )

    assert create_response.status_code == 201
    test_case_id = create_response.json()["id"]

    # 2. READ the test case
    get_response = client.get(f"/test-cases/{test_case_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Login functionality test"

    # 3. UPDATE the test case
    update_response = client.patch(
        f"/test-cases/{test_case_id}",
        json={
            "title": "Updated login test",
            "description": "Verify login with valid credentials",
            "expected_result": "User reaches the home dashboard",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated login test"
    assert (
        update_response.json()["expected_result"]
        == "User reaches the home dashboard"
    )

    # 4. RECORD a test run
    run_response = client.post(
        f"/test-cases/{test_case_id}/runs",
        json={
            "status": "PASS",
            "notes": "Login worked with valid credentials",
        },
    )

    assert run_response.status_code == 201
    assert run_response.json()["status"] == "PASS"

    # 5. READ the test run
    runs_response = client.get(f"/test-cases/{test_case_id}/runs")

    assert runs_response.status_code == 200
    assert len(runs_response.json()) == 1
    assert runs_response.json()[0]["notes"] == (
        "Login worked with valid credentials"
    )

    # 6. DELETE the test case
    delete_response = client.delete(f"/test-cases/{test_case_id}")

    assert delete_response.status_code == 204

    # 7. VERIFY the deleted test case cannot be found
    missing_response = client.get(f"/test-cases/{test_case_id}")

    assert missing_response.status_code == 404

# negative test cases


def test_create_run_for_nonexistent_test_case(client):
    response = client.post(
        "/test-cases/9999/runs",
        json={
            "status": "PASS",
            "notes": "This test case does not exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Test case not found"


def test_create_run_with_invalid_status(client):
    # First create a valid test case
    create_response = client.post(
        "/test-cases",
        json={
            "title": "Login test",
            "description": "Check login functionality",
            "expected_result": "Dashboard is displayed",
        },
    )

    test_case_id = create_response.json()["id"]

    # Try to record a run with an invalid status
    response = client.post(
        f"/test-cases/{test_case_id}/runs",
        json={
            "status": "PENDING",
            "notes": "Testing invalid status",
        },
    )

    assert response.status_code == 422


def test_delete_nonexistent_test_case(client):
    response = client.delete("/test-cases/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Test case not found"
