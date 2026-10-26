# TestPilot — Test Execution & Verification Platform

A lightweight test management platform built with **FastAPI, SQLAlchemy, SQLite, Pytest, and Playwright**. TestPilot provides REST APIs for managing test cases, recording execution outcomes, and verifying workflows through automated API and browser tests.

## Features

- **Test Case Management:** Create, retrieve, update, list, and delete test cases.
- **Execution Tracking:** Record test runs with `PASS` or `FAIL` statuses and optional notes.
- **Persistent Storage:** Store test cases and execution history using SQLite and SQLAlchemy.
- **REST API:** Expose endpoints through FastAPI with request validation using Pydantic.
- **API Testing:** Validate CRUD operations, input constraints, error handling, and execution history using Pytest.
- **Browser Automation:** Use Playwright to interact with Swagger UI in Chromium and verify live server responses.
- **End-to-End Workflow:** Create a test case, retrieve it, record execution results, and verify the stored history.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | REST API development |
| SQLAlchemy | ORM and database operations |
| SQLite | Relational data persistence |
| Pydantic | Request validation and response schemas |
| Pytest | Automated test execution |
| Playwright | Browser automation |
| Swagger UI | Interactive API documentation |

## Project Structure

```text
TestPilot/
├── main.py              # FastAPI application and endpoints
├── database.py          # Database connection and session setup
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── test_api.py          # API tests
├── test_app.py          # Browser-driven end-to-end workflow
├── requirements.txt     # Python dependencies
├── .gitignore           # Files excluded from Git
└── README.md            # Project documentation
```

The SQLite database is created locally when the application starts.

## Getting Started

### Prerequisites

- Python 3.11 or compatible version
- Git
- Chromium browser support through Playwright

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/TestPilot.git
cd TestPilot
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### 4. Start the application

```bash
uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/test-cases` | Create a test case |
| GET | `/test-cases` | List test cases |
| GET | `/test-cases/{test_case_id}` | Retrieve a test case |
| PATCH | `/test-cases/{test_case_id}` | Update a test case |
| DELETE | `/test-cases/{test_case_id}` | Delete a test case |
| POST | `/test-cases/{test_case_id}/runs` | Record a test run |
| GET | `/test-cases/{test_case_id}/runs` | Retrieve execution history |

### Example: Create a Test Case

```json
{
  "title": "Login functionality",
  "description": "Verify user login behavior",
  "expected_result": "User logs in successfully"
}
```

### Example: Record a Test Run

```json
{
  "status": "PASS",
  "notes": "Login workflow completed successfully"
}
```

Supported execution statuses are `PASS` and `FAIL`.

## Running the Tests

Ensure the application server is running before executing the browser-driven workflow.

### Run API tests

```bash
python -m pytest test_api.py -v
```

### Run browser automation tests

```bash
python -m pytest test_playwright.py -v --headed --slowmo 1000
```

### Run the end-to-end workflow

```bash
python -m pytest test_app.py -v -s --headed --slowmo 700
```

The end-to-end test interacts with Swagger UI through Chromium, creates a test case, retrieves it, records PASS and FAIL runs, and verifies the execution history.

## Current Status

- REST API implementation completed.
- SQLite persistence and relational models implemented.
- API test suite: 9 tests passing.
- Browser-driven end-to-end workflow: passing.
- Parameterized Playwright login tests: implemented.

## Future Improvements

- Build a dedicated web dashboard for test case management.
- Add execution history filters and summary statistics.
- Generate HTML test reports.
- Improve automated test data setup and cleanup.
- Add CI/CD integration with GitHub Actions.

## License

This project is available for educational and portfolio purposes. A formal open-source license can be added when the licensing terms are decided.
