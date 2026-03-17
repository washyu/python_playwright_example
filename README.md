# Python Playwright Sauce Demo Tests

![Playwright Tests](https://github.com/washyu/python_playwright_example/actions/workflows/playwright-tests.yml/badge.svg)

End-to-end testing for [Sauce Demo](https://www.saucedemo.com) using Playwright and Python, with Page Object Model architecture.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# (Optional) Create .env file for local configuration
cp .env.example .env
# Edit .env to set HEADED=true for visible browser mode
```

### Pre-commit Hooks

This project uses pre-commit hooks for code formatting (black, isort, ruff):

```bash
uv run pre-commit install
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests (headless, parallel)
uv run pytest

# Run specific test file
uv run pytest tests/test_login.py

# Run with verbose output
uv run pytest -v

# Run specific test by name
uv run pytest -k test_login
```

### Test Markers

```bash
# Run by category
uv run pytest -m smoke
uv run pytest -m "login or cart"
uv run pytest -m checkout
uv run pytest -m regression
```

Available markers: `smoke`, `regression`, `critical`, `slow`, `login`, `cart`, `checkout`, `ui`

### Headed vs Headless Mode

By default, tests run in **headless** mode with parallel execution (`-n auto`).

**Option 1: Using .env file (recommended for local development)**
```bash
cp .env.example .env
# Edit .env and set:
# HEADED=true
# SLOWMO=500

uv run pytest
```

**Option 2: Command line environment variables**
```bash
HEADED=true uv run pytest
HEADED=true SLOWMO=1000 uv run pytest
```

### Different Browsers

```bash
uv run pytest --browser chromium   # default
uv run pytest --browser firefox
uv run pytest --browser webkit

# Multiple browsers
uv run pytest --browser chromium --browser firefox
```

### Parallel Execution

Tests run in parallel by default (`-n auto`). To run sequentially:

```bash
uv run pytest -n 0
```

### Debugging

```bash
# Enable tracing
uv run pytest --tracing on

# Run headed with slow motion
HEADED=true SLOWMO=1000 uv run pytest -n 0
```

## Test Reports

Two report formats are generated after each test run:

- **HTML report**: `playwright-report/index.html`
- **JUnit XML**: `test-results/junit.xml`
- **Failure screenshots**: `test-results/screenshots/`

```bash
# Open HTML report (Linux)
xdg-open playwright-report/index.html

# Open HTML report (macOS)
open playwright-report/index.html
```

## Project Structure

```
.
├── tests/
│   ├── test_login.py         # Login and authentication tests
│   ├── test_logout.py        # Logout tests
│   ├── test_e2e.py           # End-to-end workflow tests
│   ├── test_checkout.py      # Checkout flow tests
│   └── api/
│       └── test_testful_booker.py  # Restful Booker API tests
├── models/                   # Page Object Models
│   ├── base/BasePage.py      # Base class with shared helpers
│   ├── login/LoginPage.py
│   ├── cart/CartPage.py
│   ├── inventory/InventoryPage.py
│   └── checkout/
│       ├── CheckoutStepOnePage.py
│       ├── CheckoutStepTwoPage.py
│       └── CheckoutCompletePage.py
├── test_data/                # JSON fixtures (users, products, checkout)
├── conftest.py               # Fixtures and pytest hooks
├── pytest.ini                # Pytest settings and markers
├── .env.example              # Environment variable template
└── pyproject.toml            # Project dependencies
```

## Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `authenticated_page` | function | Page already logged in as `standard_user` |
| `cart_with_items` | function | Authenticated page with Backpack + Bike Light in cart |
| `test_data` | session | Loaded JSON test data (users, products, checkout) |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADED` | `false` | Run tests in headed mode (visible browser) |
| `SLOWMO` | `0` | Slow down operations by milliseconds |

## GitHub Actions

Tests run automatically on:
- Push to `main`/`master`
- Pull requests
- Manual workflow dispatch

**View test reports**: After a workflow run, download the `playwright-report` artifact from the Actions tab.

## Test Application

- **Sauce Demo URL**: https://www.saucedemo.com — `standard_user` / `secret_sauce`
- **Restful Booker API**: https://restful-booker.herokuapp.com — public hotel booking API used for API test examples

## License

MIT
