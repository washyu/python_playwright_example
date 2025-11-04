import pytest
from playwright.sync_api import Page


@pytest.fixture(autouse=True)
def configure_page(page: Page):
    """Configure page settings."""
    page.set_default_timeout(10000)  # 10 seconds timeout
    yield
