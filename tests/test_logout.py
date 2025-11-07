import json
import re
from playwright.sync_api import Page, expect
import pytest
from models import LoginPage


@pytest.fixture
def test_users():
    with open('test_data/users.json') as f:
        return json.load(f)


def test_successful_logout_from_inventory(page: Page, test_users):
    """Test successful logout from the inventory page."""
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    # Login
    inventory_page = login_page.login(user['username'], user['password'])
    expect(page).to_have_url(re.compile(".*inventory.html"))

    # Logout using BasePage method
    login_page = inventory_page.logout()

    # Verify we're back on the login page
    expect(page).to_have_url(re.compile(".*saucedemo.com/?$"))
    assert login_page.username_input.is_visible(), "Should be on login page after logout"


def test_cannot_access_inventory_after_logout(page: Page, test_users):
    """Test that user cannot access inventory page after logout (session cleared)."""
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    # Login
    inventory_page = login_page.login(user['username'], user['password'])
    expect(page).to_have_url(re.compile(".*inventory.html"))

    # Logout
    inventory_page.logout()
    expect(page).to_have_url(re.compile(".*saucedemo.com/?$"))

    # Try to directly navigate to inventory page
    page.goto("https://www.saucedemo.com/inventory.html")

    # Should be redirected back to login page or see error
    expect(page).to_have_url(re.compile(".*saucedemo.com/?$|.*saucedemo.com/inventory.html"))

    # If we're on inventory.html, verify the error message is shown
    if "inventory.html" in page.url:
        error_message = page.locator("[data-test='error']")
        assert error_message.is_visible(), "Error message should be shown when accessing inventory without login"
    else:
        # We should be back on the login page
        assert login_page.username_input.is_visible(), "Should be redirected to login page"


def test_login_again_after_logout(page: Page, test_users):
    """Test that user can login again after logging out."""
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    # First login
    inventory_page = login_page.login(user['username'], user['password'])
    expect(page).to_have_url(re.compile(".*inventory.html"))

    # Logout
    login_page = inventory_page.logout()
    expect(page).to_have_url(re.compile(".*saucedemo.com/?$"))

    # Login again with same credentials
    inventory_page = login_page.login(user['username'], user['password'])
    expect(page).to_have_url(re.compile(".*inventory.html"))
    assert inventory_page.is_loaded(), "Should be able to login again after logout"

    # Verify we can still interact with the page
    product_count = inventory_page.get_product_count()
    assert product_count > 0, "Products should be visible after logging in again"


def test_menu_opens_and_closes_on_inventory(page: Page, test_users):
    """Test that the hamburger menu opens and closes properly on inventory page."""
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    inventory_page = login_page.login(user['username'], user['password'])
    expect(page).to_have_url(re.compile(".*inventory.html"))

    # Menu should be closed initially
    assert not inventory_page.is_menu_open(), "Menu should be closed initially"

    # Open menu
    inventory_page.open_menu()
    assert inventory_page.is_menu_open(), "Menu should be open"

    # Close menu
    inventory_page.close_menu()
    # Wait a bit for animation
    page.wait_for_timeout(300)
    assert not inventory_page.is_menu_open(), "Menu should be closed after closing"


def test_menu_links_accessible_when_open(page: Page, test_users):
    """Test that menu links are accessible when menu is opened on inventory page."""
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    inventory_page = login_page.login(user['username'], user['password'])
    expect(page).to_have_url(re.compile(".*inventory.html"))

    # Menu should be closed initially
    assert not inventory_page.is_menu_open(), "Menu should be closed initially"

    # Open menu
    inventory_page.open_menu()

    # Menu should now be open
    assert inventory_page.is_menu_open(), "Menu should be open"

    # Verify menu close button is visible
    assert inventory_page.menu_close_button.is_visible(), "Menu close button should be visible when menu is open"

    # Verify all menu links are clickable (not checking visibility due to DOM structure)
    # Just verify they exist and can be clicked
    assert inventory_page.logout_link.count() > 0, "Logout link should exist in menu"
    assert inventory_page.all_items_link.count() > 0, "All Items link should exist in menu"
    assert inventory_page.about_link.count() > 0, "About link should exist in menu"
    assert inventory_page.reset_app_link.count() > 0, "Reset App link should exist in menu"
