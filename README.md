# Python Playwright Sauce Demo Tests

![Playwright Tests](https://github.com/washyu/python_playwright_example/actions/workflows/playwright-tests.yml/badge.svg)

End-to-end testing for [Sauce Demo](https://www.saucedemo.com) using Playwright and Python.

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

## Running Tests

### Basic Test Execution

```bash
# Run all tests (headless mode)
uv run pytest

# Run specific test file
uv run pytest tests/test_login.py

# Run with verbose output
uv run pytest -v

# Run specific test by name
uv run pytest -k test_login
```

### Headed vs Headless Mode

By default, tests run in **headless** mode. Control this with environment variables:

**Option 1: Using .env file (recommended for local development)**
```bash
# Create .env file
cp .env.example .env

# Edit .env and set:
# HEADED=true
# SLOWMO=500

# Run tests (reads from .env)
uv run pytest
```

**Option 2: Command line environment variables**
```bash
# Run tests in headed mode (visible browser)
HEADED=true uv run pytest

# Run in headed mode with custom slowmo
HEADED=true SLOWMO=1000 uv run pytest

# Run headless (default)
uv run pytest
```

### Different Browsers

```bash
# Firefox
uv run pytest --browser firefox

# WebKit (Safari)
uv run pytest --browser webkit

# Multiple browsers
uv run pytest --browser chromium --browser firefox
```

### Debugging

```bash
# Enable tracing
uv run pytest --tracing on

# Run in headed mode with slow motion
HEADED=true SLOWMO=1000 uv run pytest
```

## Test Reports

HTML reports are automatically generated after each test run:

- **Location**: `playwright-report/index.html`
- **View**: Open the file in your browser

```bash
# Open report (Linux)
xdg-open playwright-report/index.html

# Open report (macOS)
open playwright-report/index.html

# Open report (Windows)
start playwright-report/index.html
```

## GitHub Actions

Tests run automatically on:
- Push to `master`/`main` branch
- Pull requests
- Manual workflow dispatch

**View test reports**: After a workflow run, download the `playwright-report` artifact from the Actions tab.

## Test Application

- **URL**: https://www.saucedemo.com
- **Username**: `standard_user`
- **Password**: `secret_sauce`

## Project Structure

```
.
├── tests/              # Test files
│   └── test_login.py   # Login and authentication tests
├── models/             # Page object models
├── conftest.py         # Pytest configuration and .env loader
├── pytest.ini          # Pytest settings
├── .env.example        # Environment variable template
├── .env                # Local environment config (not in git)
└── pyproject.toml      # Project dependencies
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADED` | `false` | Run tests in headed mode (visible browser) |
| `SLOWMO` | `0` (headless) / `500` (headed) | Slow down operations by milliseconds |

## License

MIT
