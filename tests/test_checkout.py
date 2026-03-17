"""
Checkout flow tests for Sauce Demo.

Tests cover the complete purchase workflow from cart through order confirmation,
including input validation, error handling, and price verification.

Fixture dependency chain:
    page → authenticated_page → cart_with_items

The cart_with_items fixture (defined in conftest.py) pre-loads two items:
  - Sauce Labs Backpack  ($29.99)
  - Sauce Labs Bike Light ($9.99)
  Subtotal: $39.98, Tax: $3.20, Total: $43.18
"""

import pytest
from playwright.sync_api import Page, expect

from models import (
    CartPage,
    CheckoutCompletePage,
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_URLS = {
    "cart": "https://www.saucedemo.com/cart.html",
    "step_one": "https://www.saucedemo.com/checkout-step-one.html",
    "step_two": "https://www.saucedemo.com/checkout-step-two.html",
    "complete": "https://www.saucedemo.com/checkout-complete.html",
    "inventory": "https://www.saucedemo.com/inventory.html",
}


def do_checkout(page: Page, test_data: dict) -> CheckoutStepTwoPage:
    """
    Helper: navigate from a cart-loaded page through step one to the overview.

    Returns the CheckoutStepTwoPage so individual tests can assert on it
    or call finish_order() without repeating the setup steps.
    """
    customer = test_data["checkout"]["valid_customer"]

    cart_page = CartPage(page)
    cart_page.navigate()
    step_one: CheckoutStepOnePage = cart_page.proceed_to_checkout()

    step_two: CheckoutStepTwoPage = step_one.submit_form(
        first_name=customer["first_name"],
        last_name=customer["last_name"],
        postal_code=customer["postal_code"],
    )
    return step_two


# ---------------------------------------------------------------------------
# Happy path — full flow
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.checkout
def test_checkout_complete_happy_path(cart_with_items: Page, test_data: dict):
    """
    Verify a user can complete a full purchase from cart to confirmation.

    This is the primary smoke test for the purchase lifecycle.
    Detailed price assertions live in test_checkout_total_includes_tax.
    """
    step_two = do_checkout(cart_with_items, test_data)
    assert step_two is not None, "Expected to reach step two — form may have errored"

    expect(cart_with_items).to_have_url(EXPECTED_URLS["step_two"])

    complete: CheckoutCompletePage = step_two.finish_order()

    expect(cart_with_items).to_have_url(EXPECTED_URLS["complete"])
    assert complete.is_success(), "Order confirmation page should show success state"
    assert complete.get_header_text() == "Thank you for your order!"


@pytest.mark.checkout
def test_checkout_confirmation_back_home_clears_cart(
    cart_with_items: Page, test_data: dict
):
    """
    Verify Back Home after checkout lands on inventory with an empty cart.

    Cart badge should disappear after a completed purchase — regression
    guard for state not being cleared on order completion.
    """
    from models import InventoryPage

    step_two = do_checkout(cart_with_items, test_data)
    complete = step_two.finish_order()
    inventory: InventoryPage = complete.back_to_home()

    expect(cart_with_items).to_have_url(EXPECTED_URLS["inventory"])
    assert not inventory.is_cart_badge_visible(), (
        "Cart badge should not be visible after a completed purchase"
    )


# ---------------------------------------------------------------------------
# Order overview / price assertions
# ---------------------------------------------------------------------------


@pytest.mark.checkout
def test_checkout_overview_contains_correct_items(
    cart_with_items: Page, test_data: dict
):
    """
    Verify the order overview reflects the items added in cart_with_items.

    cart_with_items adds Sauce Labs Backpack and Sauce Labs Bike Light.
    Both should appear in the step-two item list.
    """
    expected_items = test_data["checkout"]["expected_cart_items"]
    step_two = do_checkout(cart_with_items, test_data)

    overview_items = step_two.get_item_names()
    for expected in expected_items:
        assert expected in overview_items, (
            f"Expected '{expected}' in order overview, got: {overview_items}"
        )


@pytest.mark.checkout
def test_checkout_total_includes_tax(cart_with_items: Page, test_data: dict):
    """
    Verify the displayed total equals subtotal + tax.

    Uses CheckoutStepTwoPage.verify_calculations() which allows a 0.01
    floating-point tolerance. Also asserts each component is positive —
    catches regressions where a value silently becomes 0.
    """
    step_two = do_checkout(cart_with_items, test_data)

    subtotal = step_two.get_subtotal()
    tax = step_two.get_tax()
    total = step_two.get_total()

    assert subtotal > 0, "Subtotal should be a positive value"
    assert tax > 0, "Tax should be a positive value"
    assert total > 0, "Total should be a positive value"
    assert step_two.verify_calculations(), (
        f"Total ${total} should equal subtotal ${subtotal} + tax ${tax}"
    )


@pytest.mark.checkout
def test_checkout_payment_and_shipping_info_displayed(
    cart_with_items: Page, test_data: dict
):
    """
    Verify the payment and shipping info labels are populated on step two.

    These come from expected_data.json so the assertion is data-driven
    and will catch changes to the display values.
    """
    expected = test_data["expected"]["checkout"]
    step_two = do_checkout(cart_with_items, test_data)

    assert step_two.get_payment_info() == expected["payment_info"], (
        f"Payment info mismatch: got '{step_two.get_payment_info()}'"
    )
    assert step_two.get_shipping_info() == expected["shipping_info"], (
        f"Shipping info mismatch: got '{step_two.get_shipping_info()}'"
    )


# ---------------------------------------------------------------------------
# Cancel / navigation
# ---------------------------------------------------------------------------


@pytest.mark.checkout
def test_cancel_from_step_one_returns_to_cart(cart_with_items: Page):
    """
    Verify Cancel on step one returns to cart with items still present.

    Sauce Demo's Cancel on step one goes back to /cart.html, not inventory.
    Items should be preserved — cart state must survive an abandoned checkout.
    """
    cart_page = CartPage(cart_with_items)
    cart_page.navigate()
    step_one: CheckoutStepOnePage = cart_page.proceed_to_checkout()

    returned_cart: CartPage = step_one.cancel_checkout()

    expect(cart_with_items).to_have_url(EXPECTED_URLS["cart"])
    assert returned_cart.get_item_count() > 0, (
        "Cart should still contain items after cancelling from step one"
    )


@pytest.mark.checkout
def test_cancel_from_step_two_returns_to_inventory(
    cart_with_items: Page, test_data: dict
):
    """
    Verify Cancel on step two returns to the inventory page.

    Note: this is intentionally different from step one cancel behaviour —
    Sauce Demo returns to /inventory.html here, not /cart.html.
    See testing_strategy.md navigation section.
    """
    from models import InventoryPage

    step_two = do_checkout(cart_with_items, test_data)
    inventory: InventoryPage = step_two.cancel_order()

    expect(cart_with_items).to_have_url(EXPECTED_URLS["inventory"])
    assert inventory.is_loaded(), "Should land on a loaded inventory page"


# ---------------------------------------------------------------------------
# Form validation
# ---------------------------------------------------------------------------


@pytest.mark.checkout
@pytest.mark.parametrize(
    "first_name, last_name, postal_code, expected_error",
    [
        ("", "Doe", "12345", "First Name is required"),
        ("John", "", "12345", "Last Name is required"),
        ("John", "Doe", "", "Postal Code is required"),
    ],
    ids=["missing_first_name", "missing_last_name", "missing_postal_code"],
)
def test_checkout_form_validation(
    cart_with_items: Page,
    first_name: str,
    last_name: str,
    postal_code: str,
    expected_error: str,
):
    """
    Verify each required field produces the correct validation error.

    Parametrized to keep assertions DRY while still providing clear
    failure messages per field. Error text asserted via has_error() +
    get_error_text() on CheckoutStepOnePage rather than raw locators,
    keeping this test resilient to minor DOM changes.
    """
    cart_page = CartPage(cart_with_items)
    cart_page.navigate()
    step_one: CheckoutStepOnePage = cart_page.proceed_to_checkout()

    # submit_form returns None when a validation error is shown
    result = step_one.submit_form(first_name, last_name, postal_code)

    assert result is None, (
        "submit_form should return None when validation fails, "
        f"but returned a page object for inputs: "
        f"first='{first_name}' last='{last_name}' postal='{postal_code}'"
    )
    assert step_one.has_error(), "An error message should be visible"
    assert expected_error in step_one.get_error_text(), (
        f"Expected error to contain '{expected_error}', "
        f"got: '{step_one.get_error_text()}'"
    )


@pytest.mark.checkout
def test_checkout_form_error_can_be_dismissed(cart_with_items: Page):
    """
    Verify the validation error banner can be closed by the user.

    After triggering an error, clicking X should hide the banner without
    a page reload, allowing the user to correct and resubmit.
    """
    cart_page = CartPage(cart_with_items)
    cart_page.navigate()
    step_one: CheckoutStepOnePage = cart_page.proceed_to_checkout()

    step_one.submit_form("", "", "")
    assert step_one.has_error(), "Error banner should be visible after empty submit"

    step_one.clear_error()
    assert not step_one.has_error(), (
        "Error banner should be hidden after clicking the dismiss button"
    )


@pytest.mark.checkout
def test_checkout_accepts_special_characters_in_name(
    cart_with_items: Page, test_data: dict
):
    """
    Verify the form accepts international characters and apostrophes.

    Uses the special_characters entry from checkout.json (José O'Brien,
    K1A 0B1). Validates that the form submits successfully without
    triggering a validation error — we don't assert on display since
    we don't control the app's rendering of those characters.
    """
    special = test_data["checkout"]["special_characters"]

    cart_page = CartPage(cart_with_items)
    cart_page.navigate()
    step_one: CheckoutStepOnePage = cart_page.proceed_to_checkout()

    step_two = step_one.submit_form(
        first_name=special["first_name"],
        last_name=special["last_name"],
        postal_code=special["postal_code"],
    )

    assert step_two is not None, (
        "Special characters in name fields should not trigger a validation error"
    )
    expect(cart_with_items).to_have_url(EXPECTED_URLS["step_two"])