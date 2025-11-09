import pytest
from playwright.sync_api import Page, expect

from models import LoginPage


@pytest.mark.smoke
@pytest.mark.critical
def test_happy_path_complete_purchase(page: Page, test_data):
    """
    End-to-end happy path test: Complete purchase flow from login to order confirmation.

    Test Steps:
        1. Login as standard_user
        2. Add Sauce Labs Backpack to cart
        3. Click on cart and verify the correct item is listed
        4. Click checkout
        5. Fill customer information
        6. Verify checkout overview (items and totals)
        7. Complete order
        8. Verify order confirmation

    Expected Results:
        - User successfully logs in
        - Item is added to cart
        - Cart displays correct item with details
        - Checkout completes successfully
        - Order totals are correct (Item: $29.99, Tax: $2.40, Total: $32.39)
        - Order confirmation page is displayed
        - Back to home button is available
    """
    # Get URLs from expected data
    urls = test_data["expected"]["urls"]

    # Step 1: Login as standard_user
    user = test_data["users"]["standard_user"]
    page.goto(urls["login"])

    login_page = LoginPage(page)
    inventory_page = login_page.login(user["username"], user["password"])

    # Verify we're on inventory page
    expect(page).to_have_url(urls["inventory"])
    assert inventory_page.is_loaded(), "Inventory page should be loaded"

    # Step 2: Add Sauce Labs Backpack to cart
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")

    # Verify cart badge shows 1 item
    assert inventory_page.get_cart_badge_count() == 1, "Cart badge should show 1 item"

    # Step 3: Click on cart and verify the correct item is listed
    cart_page = inventory_page.click_cart()
    expect(page).to_have_url(urls["cart"])
    assert cart_page.is_loaded(), "Cart page should be loaded"

    # Verify cart contains the correct item
    assert cart_page.get_item_count() == 1, "Cart should contain 1 item"

    # Verify item name
    item_names = cart_page.get_item_names()
    assert (
        "Sauce Labs Backpack" in item_names
    ), "Cart should contain Sauce Labs Backpack"

    # Verify item details
    item_details = cart_page.get_item_details(0)
    assert (
        item_details["name"] == test_data["products"]["sauce_labs_backpack"]["name"]
    ), "Item name should be Sauce Labs Backpack"
    assert (
        str(test_data["products"]["sauce_labs_backpack"]["price"])
        in item_details["price"]
    ), "Item price should be $29.99"
    assert (
        item_details["description"]
        == test_data["products"]["sauce_labs_backpack"]["description"]
    ), "Item should have a description"

    # Step 4: Click checkout
    checkout_step_one = cart_page.proceed_to_checkout()
    expect(page).to_have_url(urls["checkout_step_one"])
    assert checkout_step_one.is_loaded(), "Checkout step 1 page should be loaded"

    # Step 5: Fill customer information from test data
    customer = test_data["checkout"]["valid_customer"]
    checkout_step_two = checkout_step_one.submit_form(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )

    expect(page).to_have_url(urls["checkout_step_two"])
    assert checkout_step_two.is_loaded(), "Checkout step 2 page should be loaded"

    # Step 6: Verify checkout overview
    # Verify correct item
    order_items = checkout_step_two.get_item_names()
    assert (
        test_data["products"]["sauce_labs_backpack"]["name"] in order_items
    ), "Order should contain Sauce Labs Backpack"

    # Verify item count
    assert checkout_step_two.get_item_count() == 1, "Order should contain 1 item"

    # Verify price totals
    subtotal = checkout_step_two.get_subtotal()
    tax = checkout_step_two.get_tax()
    total = checkout_step_two.get_total()

    # Get expected values from test data
    tax_rate = test_data["expected"]["checkout"]["tax_rate"]
    product_price = test_data["products"]["sauce_labs_backpack"]["price"]

    # Calculate expected subtotal from product price (1 item in cart)
    expected_subtotal = float(product_price)
    assert (
        subtotal == expected_subtotal
    ), f"Item total should be ${expected_subtotal}, got ${subtotal}"

    # Calculate expected tax using the tax rate
    expected_tax = round(expected_subtotal * tax_rate, 2)
    assert (
        tax == expected_tax
    ), f"Tax should be ${expected_tax} ({tax_rate * 100}% of ${expected_subtotal}), got ${tax}"

    # Calculate expected total
    expected_total = round(expected_subtotal + expected_tax, 2)
    assert total == expected_total, f"Total should be ${expected_total}, got ${total}"

    # Verify calculations are correct (subtotal + tax = total)
    assert checkout_step_two.verify_calculations(), "Subtotal + Tax should equal Total"

    # Verify payment and shipping info from expected data
    payment_info = checkout_step_two.get_payment_info()
    shipping_info = checkout_step_two.get_shipping_info()
    expected_payment = test_data["expected"]["checkout"]["payment_info"]
    expected_shipping = test_data["expected"]["checkout"]["shipping_info"]

    assert (
        payment_info == expected_payment
    ), f"Payment info should be '{expected_payment}', got '{payment_info}'"
    assert (
        shipping_info == expected_shipping
    ), f"Shipping info should be '{expected_shipping}', got '{shipping_info}'"

    # Step 7: Click finish to complete order
    checkout_complete = checkout_step_two.finish_order()
    expect(page).to_have_url(urls["checkout_complete"])
    assert checkout_complete.is_loaded(), "Checkout complete page should be loaded"

    # Step 8: Verify order confirmation
    assert checkout_complete.is_success(), "Order should be completed successfully"

    # Verify success header using expected data
    header_text = checkout_complete.get_header_text()
    expected_success_header = test_data["expected"]["checkout"]["success_header"]
    assert (
        header_text == expected_success_header
    ), f"Header should be '{expected_success_header}', got: {header_text}"

    # Verify confirmation message using expected data
    confirmation_text = checkout_complete.get_confirmation_text()
    expected_success_message = test_data["expected"]["checkout"]["success_message"]
    assert (
        expected_success_message in confirmation_text
    ), f"Confirmation should contain '{expected_success_message}', got: {confirmation_text}"

    # Verify pony express image is visible (order dispatched indicator)
    assert (
        checkout_complete.is_pony_express_visible()
    ), "Order dispatch image should be visible"

    # Verify back to home button is available
    verification = checkout_complete.verify_order_complete()
    assert verification["button_visible"], "Back to home button should be visible"

    # Optional: Navigate back to home
    inventory_page = checkout_complete.back_to_home()
    expect(page).to_have_url(urls["inventory"])

    # Verify cart is cleared after successful purchase
    assert (
        not inventory_page.is_cart_badge_visible()
    ), "Cart should be empty after purchase"
