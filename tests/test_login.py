import re
from playwright.sync_api import Page, expect
from models import LoginPage


def test_login(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    # Login returns the InventoryPage
    inventory_page = login_page.login("standard_user", "secret_sauce")

    # Verify we're on the inventory page
    expect(page).to_have_url(re.compile(".*inventory.html"))
    assert inventory_page.is_loaded(), "Inventory page should be loaded"

    # Verify products are displayed
    product_count = inventory_page.get_product_count()
    assert product_count > 0, f"Expected products to be displayed, found {product_count}"

def test_blocked_login(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login("locked_out_user", "secret_sauce")

    # Verify error is displayed
    assert login_page.has_error(), "Expected error message to be displayed"

    # Optionally verify the specific error text
    error_text = login_page.get_error_text()
    assert "locked out" in error_text.lower(), f"Expected 'locked out' in error message, got: {error_text}"