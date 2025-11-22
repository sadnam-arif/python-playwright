AutomationExercise UI & API Test Framework

=========== Overview ===========

This repository contains an automated test framework for **AutomationExercise** ([https://automationexercise.com](https://automationexercise.com)), supporting both **UI automation using Playwright** and **API automation using Python + Requests**.

It includes:

* Playwright-based UI tests
* API tests for user creation & duplicate account validation
* Cross-browser execution
* Automation-friendly Page Object Model (POM)
* CI/CD integration using **GitHub Actions**
* HTML reports, traces, videos, and downloaded invoices as artifacts

---

Project Structure

```
.
├── test_create_user.py                # API-driven user creation (UI uses the credentials)
├── test_purchase_flow.py              # Full UI purchase/invoice flow (cross-browser)
├── test_api_user_registration.py      # API tests (unique user + duplicate)
├── conftest.py                        # Browser fixture (chromium + firefox)
├── requirements.txt                   # Python dependencies
├── fixtures/
│   └── user_credentials.json          # Saved API-generated credentials
├── downloads/                         # Invoice files (CI uploaded)
├── traces/                            # Playwright trace files (CI uploaded)
├── videos/                            # Test videos (CI uploaded)
└── .github/workflows/playwright.yml   # CI/CD pipeline
```

---

Setup Instructions (Local)

1. Create virtual environment

```
python -m venv venv
source venv/bin/activate     # MacOS/Linux
venv\Scripts\activate        # Windows
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Install Playwright browsers

```
python -m playwright install
```

4. Run UI tests

```
pytest test_purchase_flow.py --headed
```

5. Run API tests

```
pytest -q test_api_user_registration.py
```

---

Run Tests in Parallel

Install xdist:

```
pip install pytest-xdist
```

Run tests in parallel:

```
pytest -n auto
```

> Playwright supports multiple browsers in parallel as long as each test creates its own browser context.

---

Run in Multiple Browsers

Your UI suite supports **Chromium** and **Firefox**, configured in `conftest.py`:

```
@pytest.fixture(params=["chromium", "firefox"])
def my_browser(request):
    return request.param
```

Tests automatically run twice, once per browser.

---

Retry Logic

Install retry plugin:

```
pip install pytest-rerunfailures
```

Run with retries:

```
pytest --reruns 2
```

---

CI/CD Pipeline (GitHub Actions)

This project includes a full CI pipeline that:

* Installs dependencies
* Runs API & UI tests
* Uploads artifacts:

  * HTML reports
  * Playwright videos
  * Playwright traces
  * Downloaded invoice files
* Supports manual & push-based triggers

---

CI/CD Status Badge

Replace `<username>` and `<repo>`:

```
![CI](https://github.com/<username>/<repo>/actions/workflows/playwright.yml/badge.svg)
```

---

Latest Successful CI Run

Add your run URL here:

```
https://github.com/<username>/<repo>/actions/runs/<run_id>
```

This allows viewers to inspect artifacts and reports.

---

Test Data Notes

* User creation via API (`test_create_user.py`)
* Credentials saved to `fixtures/user_credentials.json`
* UI tests load credentials dynamically
* Duplicate email logic validated via API tests
* Unique email generated using timestamp

---

Contributions

PRs and issue reports are welcome!
