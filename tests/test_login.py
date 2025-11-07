import json
import re
from playwright.sync_api import Page, expect
import pytest
from models import LoginPage

@pytest.fixture
def test_users():
    with open('test_data/users.json') as f:
        return json.load(f)

def test_login(page: Page, test_users):
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    # Login returns the InventoryPage
    inventory_page = login_page.login(user['username'], user['password'])

    # Verify we're on the inventory page
    expect(page).to_have_url(re.compile(".*inventory.html"))
    assert inventory_page.is_loaded(), "Inventory page should be loaded"

    # Verify products are displayed
    product_count = inventory_page.get_product_count()
    assert product_count > 0, f"Expected products to be displayed, found {product_count}"

def test_blocked_login(page: Page, test_users):
    user = test_users['locked_out_user']
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login(user['username'], user['password'])

    # Verify error is displayed
    assert login_page.has_error(), "Expected error message to be displayed"

    # Optionally verify the specific error text
    error_text = login_page.get_error_text()
    assert "locked out" in error_text.lower(), f"Expected 'locked out' in error message, got: {error_text}"

def test_no_username(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login("", "test")

    assert login_page.has_error(), "Expected error message to be displayed"
    error_text = login_page.get_error_text()
    assert "username" in error_text.lower(), f"Expected 'Username' in the error message, got: {error_text}"

def test_no_password(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login("test", "")

    assert login_page.has_error(), "Expected error message to be displayed"
    error_text = login_page.get_error_text()
    assert "password" in error_text.lower(), f"Expected 'Password' in the error message, got: {error_text}"

#Kind of pointless but we should test to see if behavor changes.
def test_no_username_or_password(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login("", "")

    assert login_page.has_error(), "Expected error message to be displayed"
    error_text = login_page.get_error_text()
    assert "username" in error_text.lower(), f"Expected 'Username' in the error message, got: {error_text}"

def test_invalid_username(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login("invalid_user", "secret_sauce")

    assert login_page.has_error(), "Expected error message to be displayed"
    error_text = login_page.get_error_text()
    assert "do not match" in error_text.lower() or "not match" in error_text.lower(), f"Expected 'not match' in error message, got: {error_text}"

def test_invalid_password(page: Page, test_users):
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login(user['username'], "wrong_password")

    assert login_page.has_error(), "Expected error message to be displayed"
    error_text = login_page.get_error_text()
    assert "do not match" in error_text.lower() or "not match" in error_text.lower(), f"Expected 'not match' in error message, got: {error_text}"

def test_case_sensitive_username(page: Page, test_users):
    user = test_users['standard_user']
    login_page = LoginPage(page)
    login_page.navigate()

    login_page.login(user['username'].upper(), user['password'])

    assert login_page.has_error(), "Expected error for case-sensitive username"
    error_text = login_page.get_error_text()
    assert "do not match" in error_text.lower() or "not match" in error_text.lower(), f"Expected 'not match' in error message, got: {error_text}"

def test_sql_injection_attempt(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    # Test SQL injection in username field
    login_page.login("admin' OR '1'='1", "secret_sauce")

    # Should show error, not bypass authentication
    assert login_page.has_error(), "SQL injection should not bypass authentication"

def test_xss_attempt_in_login(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()

    # Test XSS in username field
    xss_payload = "<script>alert('XSS')</script>"
    login_page.login(xss_payload, "secret_sauce")

    # Should show error without executing script
    assert login_page.has_error(), "XSS payload should not execute"
    # Page should not have alert (script should be sanitized)
    assert "script" not in page.content().lower() or xss_payload not in page.content()