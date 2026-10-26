
import json

from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:8000"


def open_endpoint(page: Page, method: str, path: str):
    """Find and open an endpoint in Swagger UI."""

    endpoint = (
        page.locator(".opblock")
        .filter(
            has=page.locator(
                ".opblock-summary-method",
                has_text=method.upper(),
            )
        )
        .filter(
            has=page.locator(
                ".opblock-summary-path",
                has_text=path,
            )
        )
        .first
    )

    expect(endpoint).to_be_visible(timeout=15000)
    endpoint.scroll_into_view_if_needed()

    # Expand the endpoint if it is collapsed
    if endpoint.locator(".opblock-body").count() == 0:
        endpoint.locator(".opblock-summary").click()

    # Enable request editing
    try_button = endpoint.get_by_role(
        "button", name="Try it out"
    )

    if try_button.is_visible():
        try_button.click()

    return endpoint


def execute_request(endpoint, body=None):
    """Execute a request through Swagger and return its live response."""

    # Fill the request body when provided
    if body is not None:
        request_editor = endpoint.locator(
            "textarea.body-param__text"
        )
        request_editor.fill(json.dumps(body))

    # Click Execute in the browser
    endpoint.get_by_role(
        "button", name="Execute"
    ).click()

    # Locate the live server response
    live_response = endpoint.locator(
        ".live-responses-table"
    )

    expect(live_response).to_be_visible(timeout=15000)

    # Read the status from the table body, not its "Code" header
    status_code = live_response.locator(
        "tbody .response-col_status"
    ).first

    expect(status_code).to_be_visible(timeout=15000)

    actual_status = status_code.inner_text().strip()
    print(f"HTTP STATUS: {actual_status}")

    return live_response



def get_response_json(live_response):
    """Extract JSON from Swagger's live response body."""

    response_body = live_response.locator(
        ".highlight-code"
    ).last

    expect(response_body).to_be_visible(timeout=10000)

    response_text = response_body.inner_text().strip()

    # Swagger may prepend "Download" before the JSON.
    # Start parsing at the first opening brace or bracket.
    json_start = min(
        (
            pos
            for pos in (
                response_text.find("{"),
                response_text.find("["),
            )
            if pos != -1
        ),
        default=-1,
    )

    assert json_start != -1, (
        f"No JSON found in Swagger response: {response_text}"
    )

    response_text = response_text[json_start:]

    print("RESPONSE JSON:", response_text)

    return json.loads(response_text)



def assert_status(response, expected_status):
    """Assert the HTTP status returned by the server."""

    status_code = response.locator(
        "tbody .response-col_status"
    ).first

    expect(status_code).to_have_text(str(expected_status))


def test_qa_manager_visible_workflow(page: Page):
    # Open the API documentation in Chromium
    page.goto(f"{BASE_URL}/docs")

    expect(page.locator("h1")).to_contain_text(
        "Mini QA Test Manager"
    )

    # --------------------------------------------------
    # 1. CREATE a test case
    # --------------------------------------------------
    print("\nSTEP 1: Creating a test case")

    create = open_endpoint(
        page, "post", "/test-cases"
    )

    create_response = execute_request(
        create,
        {
            "title": "Visible Playwright test",
            "description": "Created through Swagger UI",
            "expected_result": "Test case is saved",
        },
    )

    assert_status(create_response, 201)

    created_case = get_response_json(create_response)

    assert "id" in created_case, (
        f"Expected an ID in the create response: {created_case}"
    )

    test_case_id = created_case["id"]

    print(f"Created test case ID: {test_case_id}")

    # --------------------------------------------------
    # 2. RETRIEVE the test case
    # --------------------------------------------------
    print("\nSTEP 2: Retrieving the test case")

    get_case = open_endpoint(
        page, "get", "/test-cases/{test_case_id}"
    )

    get_case.locator("input").first.fill(
        str(test_case_id)
    )

    case_response = execute_request(get_case)

    assert_status(case_response, 200)

    retrieved_case = get_response_json(case_response)

    assert retrieved_case["id"] == test_case_id
    assert retrieved_case["title"] == "Visible Playwright test"

    print("Test case retrieved and verified successfully!")

    # --------------------------------------------------
    # 3. RECORD a PASS run
    # --------------------------------------------------
    print("\nSTEP 3: Recording a PASS run")

    pass_run = open_endpoint(
        page, "post", "/test-cases/{test_case_id}/runs"
    )

    pass_run.locator("input").first.fill(
        str(test_case_id)
    )

    pass_response = execute_request(
        pass_run,
        {
            "status": "PASS",
            "notes": "Visible browser test passed",
        },
    )

    assert_status(pass_response, 201)

    pass_result = get_response_json(pass_response)

    assert pass_result["status"] == "PASS"
    print("PASS run recorded successfully!")

    # --------------------------------------------------
    # 4. RECORD a FAIL run
    # --------------------------------------------------
    print("\nSTEP 4: Recording a FAIL run")

    fail_run = open_endpoint(
        page, "post", "/test-cases/{test_case_id}/runs"
    )

    fail_run.locator("input").first.fill(
        str(test_case_id)
    )

    fail_response = execute_request(
        fail_run,
        {
            "status": "FAIL",
            "notes": "Simulated failure for verification",
        },
    )

    assert_status(fail_response, 201)

    fail_result = get_response_json(fail_response)

    assert fail_result["status"] == "FAIL"
    print("FAIL run recorded successfully!")

    # --------------------------------------------------
    # 5. RETRIEVE and verify both runs
    # --------------------------------------------------
    print("\nSTEP 5: Verifying recorded runs")

    get_runs = open_endpoint(
        page, "get", "/test-cases/{test_case_id}/runs"
    )

    get_runs.locator("input").first.fill(
        str(test_case_id)
    )

    runs_response = execute_request(get_runs)

    assert_status(runs_response, 200)

    runs = get_response_json(runs_response)

    assert len(runs) == 2, (
        f"Expected exactly 2 runs, received {len(runs)}: {runs}"
    )

    assert [run["status"] for run in runs] == [
        "PASS",
        "FAIL",
    ]

    print("Both PASS and FAIL runs verified successfully!")
    print("\nALL WORKFLOW STEPS COMPLETED SUCCESSFULLY!")

    # Keep the browser open briefly so you can see the final result
    page.wait_for_timeout(5000)
