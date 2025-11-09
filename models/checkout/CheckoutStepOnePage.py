from playwright.sync_api import Page

from models.base import BasePage


class CheckoutStepOnePage(BasePage):
    """Page Object Model for Checkout Step 1 - Customer Information."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.first_name_input = page.locator("[data-test='firstName']")
        self.last_name_input = page.locator("[data-test='lastName']")
        self.postal_code_input = page.locator("[data-test='postalCode']")
        self.continue_button = page.locator("[data-test='continue']")
        self.cancel_button = page.locator("[data-test='cancel']")
        self.error_message = page.locator("[data-test='error']")

    def is_loaded(self):
        """Verify the checkout step 1 page is loaded."""
        return self.first_name_input.is_visible()

    def fill_customer_info(self, first_name: str, last_name: str, postal_code: str):
        """Fill in customer information form.

        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            postal_code: Customer's postal/zip code
        """
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    def continue_to_step_two(self):
        """Click continue button to proceed to checkout step 2."""
        from models.checkout import CheckoutStepTwoPage

        self.continue_button.click()
        return CheckoutStepTwoPage(self.page)

    def cancel_checkout(self):
        """Click cancel button to return to cart."""
        from models.cart import CartPage

        self.cancel_button.click()
        return CartPage(self.page)

    def has_error(self):
        """Check if an error message is displayed."""
        return self.error_message.is_visible()

    def get_error_text(self):
        """Get the error message text."""
        return self.error_message.inner_text()

    def clear_error(self):
        """Clear/dismiss the error message."""
        error_close_button = self.page.locator("[data-test='error'] button")
        if error_close_button.is_visible():
            error_close_button.click()

    def submit_form(self, first_name: str, last_name: str, postal_code: str):
        """Fill and submit the customer information form.

        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            postal_code: Customer's postal/zip code

        Returns:
            CheckoutStepTwoPage if successful, None if error
        """
        self.fill_customer_info(first_name, last_name, postal_code)
        self.continue_button.click()

        # Check if we moved to step 2 or if there's an error
        if self.has_error():
            return None

        from models.checkout import CheckoutStepTwoPage

        return CheckoutStepTwoPage(self.page)
