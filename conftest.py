import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import pytest
from playwright.sync_api import Page

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, pytestconfig):
    """Configure browser launch arguments based on environment variables.

    This fixture extends pytest-playwright's browser_type_launch_args to respect
    the HEADED and SLOWMO environment variables from .env file.

    Priority order:
    1. Command-line arguments (--headed, --slowmo)
    2. Environment variables from .env (HEADED, SLOWMO)
    3. Default values (headless, no slowmo)
    """
    # Start with playwright's default args
    launch_args = browser_type_launch_args.copy()

    # Check if HEADED environment variable is set
    headed_env = os.getenv("HEADED", "").lower() in ("true", "1", "yes")
    slowmo_env = int(os.getenv("SLOWMO", "0"))

    # Only override if not already set by command line
    # pytest-playwright sets headless based on --headed flag
    # If user didn't pass --headed flag, check environment variable
    if headed_env and launch_args.get("headless", True):
        launch_args["headless"] = False

    # Set slowmo from environment if not already set
    if slowmo_env > 0 and "slow_mo" not in launch_args:
        launch_args["slow_mo"] = slowmo_env

    return launch_args


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


# ============================================================================
# Custom Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_data():
    """We are loading this from some json file for now but it would be better to pull this data from the backend database."""
    """Load test data from JSON files."""
    data = {}

    # Load users data
    users_path = Path(__file__).parent / "test_data" / "users.json"
    if users_path.exists():
        with open(users_path) as f:
            data['users'] = json.load(f)

    # Load products data
    products_path = Path(__file__).parent / "test_data" / "products.json"
    if products_path.exists():
        with open(products_path) as f:
            data['products'] = json.load(f)

    # Load checkout data
    checkout_path = Path(__file__).parent / "test_data" / "checkout.json"
    if checkout_path.exists():
        with open(checkout_path) as f:
            data['checkout'] = json.load(f)

    # Load expected data
    expected_path = Path(__file__).parent / "test_data" / "expected_data.json"
    if expected_path.exists():
        with open(expected_path) as f:
            data['expected'] = json.load(f)

    return data


@pytest.fixture(autouse=True)
def configure_page(page: Page):
    """Configure page settings for all tests."""
    page.set_default_timeout(10000)  # 10 seconds timeout
    yield


@pytest.fixture
def authenticated_page(page: Page):
    """Fixture that returns a page already logged in as standard_user.

    This fixture reduces test setup code by handling login automatically.
    Use this for tests that need to start from an authenticated state.

    Example:
        def test_checkout(authenticated_page):
            # Page is already logged in, start testing from inventory page
            inventory = InventoryPage(authenticated_page)
            inventory.add_to_cart_by_name("Sauce Labs Backpack")
    """
    from models import LoginPage

    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("standard_user", "secret_sauce")

    return page


@pytest.fixture
def cart_with_items(authenticated_page: Page):
    """Fixture that returns a page with items already added to cart.

    Pre-loads the cart with two items:
    - Sauce Labs Backpack
    - Sauce Labs Bike Light

    Use this for tests that need to start with items in cart (e.g., checkout tests).

    Example:
        def test_checkout_flow(cart_with_items):
            # Cart already has items, user already logged in
            cart_page = CartPage(cart_with_items)
            cart_page.proceed_to_checkout()
    """
    from models import InventoryPage

    inventory = InventoryPage(authenticated_page)
    inventory.add_to_cart_by_name("Sauce Labs Backpack")
    inventory.add_to_cart_by_name("Sauce Labs Bike Light")

    return authenticated_page
