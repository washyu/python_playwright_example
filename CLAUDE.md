# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python project for end-to-end testing of https://www.saucedemo.com using Playwright. Uses `uv` for fast Python package management.

## Development Commands

### Package Management
- `uv sync` - Install/sync dependencies
- `uv add <package>` - Add a new dependency
- `uv remove <package>` - Remove a dependency
- `uv pip list` - List installed packages

### Playwright Setup
- `uv run playwright install` - Install Playwright browsers (Chromium, Firefox, WebKit)
- `uv run playwright install chromium` - Install only Chromium browser
- `uv run playwright codegen https://www.saucedemo.com` - Launch Playwright code generator for recording tests

### Running Tests
- `uv run pytest` - Run all tests (headless by default)
- `uv run pytest tests/test_file.py` - Run specific test file
- `uv run pytest -k test_name` - Run specific test by name
- `HEADED=true uv run pytest` - Run tests in headed mode (visible browser)
- `HEADED=true SLOWMO=1000 uv run pytest` - Run headed with custom slow motion
- `uv run pytest --browser firefox` - Run tests in Firefox
- `uv run pytest --browser webkit` - Run tests in WebKit (Safari)
- `uv run pytest -v` - Run with verbose output
- `uv run pytest --tracing on` - Enable tracing for debugging

### Environment Variables
- `HEADED` - Set to `true` to run tests in headed mode (default: `false`)
- `SLOWMO` - Milliseconds to slow down operations (default: `500` in headed, `0` in headless)
- Configure via `.env` file (copy from `.env.example`) or command line

### Test Reports
- HTML reports are automatically generated at `playwright-report/index.html`
- Reports include test results, timing, and failure screenshots
- Use `xdg-open playwright-report/index.html` to view

### Environment
- Python version: 3.12 (specified in `.python-version`)
- Package manager: uv (uses `pyproject.toml` and `uv.lock`)
- Virtual environment: `.venv/` (created by uv)
- Test framework: pytest with pytest-playwright plugin

## Project Structure

- `tests/` - Test directory
  - `test_login.py` - Login and authentication tests
- `models/` - Page object models directory
- `conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Pytest settings
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions
- `.python-version` - Python version specification
- `.env` - Local environment configuration (not tracked in git)

## Test Application Details

- **Base URL**: https://www.saucedemo.com
- **Valid credentials**:
  - Username: `standard_user`
  - Password: `secret_sauce`
- **Other test users**: `locked_out_user`, `problem_user`, `performance_glitch_user`, `error_user`, `visual_user`
