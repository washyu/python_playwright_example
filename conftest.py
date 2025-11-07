import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pytest

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def pytest_configure(config):
    """Configure pytest based on environment variables."""
    # Check if HEADED environment variable is set
    headed = os.getenv("HEADED", "").lower() in ("true", "1", "yes")

    if headed:
        # Add --headed to command line args if not already present
        if "--headed" not in sys.argv:
            sys.argv.append("--headed")

        # Set slowmo if HEADED is true
        slowmo = os.getenv("SLOWMO", "500")
        if "--slowmo" not in " ".join(sys.argv):
            sys.argv.append(f"--slowmo={slowmo}")
    else:
        # Headless mode - set slowmo to 0 unless explicitly set
        if "--slowmo" not in " ".join(sys.argv) and os.getenv("SLOWMO"):
            slowmo = os.getenv("SLOWMO", "0")
            sys.argv.append(f"--slowmo={slowmo}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure and attach to report."""
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # Only capture screenshot on test failure during call phase
    if rep.when == "call" and rep.failed:
        # Get the page fixture if it exists
        if "page" in item.funcargs:
            page = item.funcargs["page"]

            # Create screenshots directory if it doesn't exist
            screenshot_dir = Path("test-results/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            # Generate screenshot filename from test name
            test_name = item.nodeid.replace("::", "_").replace("/", "_")
            screenshot_path = screenshot_dir / f"{test_name}_failure.png"

            # Take screenshot
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)

                # Attach screenshot path to report for HTML report
                if hasattr(rep, "extra"):
                    rep.extra.append(pytest.html.extras.image(str(screenshot_path)))
                else:
                    rep.extra = [pytest.html.extras.image(str(screenshot_path))]

                print(f"\nScreenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"\nFailed to capture screenshot: {e}")
