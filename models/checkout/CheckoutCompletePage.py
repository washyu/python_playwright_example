from playwright.sync_api import Page

from models.base import BasePage


class CheckoutCompletePage(BasePage):
    """Page Object Model for Checkout Complete - Order Confirmation."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.complete_header = page.locator(".complete-header")
        self.complete_text = page.locator(".complete-text")
        self.pony_express_image = page.locator(".pony_express")
        self.back_home_button = page.locator("[data-test='back-to-products']")

    def is_loaded(self):
        """Verify the checkout complete page is loaded."""
        return self.complete_header.is_visible()

    def get_header_text(self):
        """Get the confirmation header text.

        Returns:
            str: Header text (typically "Thank you for your order!")
        """
        return self.complete_header.inner_text()

    def get_confirmation_text(self):
        """Get the confirmation message text.

        Returns:
            str: Confirmation message text
        """
        return self.complete_text.inner_text()

    def is_pony_express_visible(self):
        """Check if the pony express image/icon is visible.

        Returns:
            bool: True if image is visible, False otherwise
        """
        return self.pony_express_image.is_visible()

    def is_success(self):
        """Check if the order was completed successfully.

        Returns:
            bool: True if success indicators are present
        """
        return self.is_loaded() and "thank you" in self.get_header_text().lower()

    def back_to_home(self):
        """Click back home button to return to inventory page.

        Returns:
            InventoryPage: The inventory page object
        """
        from models.inventory import InventoryPage

        self.back_home_button.click()
        return InventoryPage(self.page)

    def verify_order_complete(self):
        """Verify that all order completion elements are present.

        Returns:
            dict: Verification results
        """
        return {
            "page_loaded": self.is_loaded(),
            "header_visible": self.complete_header.is_visible(),
            "message_visible": self.complete_text.is_visible(),
            "image_visible": self.is_pony_express_visible(),
            "button_visible": self.back_home_button.is_visible(),
        }
