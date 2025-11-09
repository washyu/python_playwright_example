from playwright.sync_api import Page
from models.base import BasePage


class CheckoutStepTwoPage(BasePage):
    """Page Object Model for Checkout Step 2 - Order Overview/Summary."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_items = page.locator(".cart_item")
        self.finish_button = page.locator("[data-test='finish']")
        self.cancel_button = page.locator("[data-test='cancel']")
        self.subtotal_label = page.locator(".summary_subtotal_label")
        self.tax_label = page.locator(".summary_tax_label")
        self.total_label = page.locator(".summary_total_label")
        self.payment_info = page.locator("[data-test='payment-info-value']")
        self.shipping_info = page.locator("[data-test='shipping-info-value']")

    def is_loaded(self):
        """Verify the checkout step 2 page is loaded."""
        return self.finish_button.is_visible()

    def get_item_count(self):
        """Get the number of items in the order."""
        return self.cart_items.count()

    def get_item_names(self):
        """Get list of all item names in the order."""
        return self.page.locator(".inventory_item_name").all_inner_texts()

    def get_item_prices(self):
        """Get list of all item prices in the order."""
        price_elements = self.page.locator(".inventory_item_price").all_inner_texts()
        # Convert to float for comparison, removing '$' sign
        return [float(price.replace("$", "")) for price in price_elements]

    def get_item_details(self, index: int = 0):
        """Get details of a specific order item by index.

        Args:
            index: Index of the order item (0-based)

        Returns:
            dict: Item details including name, description, price, and quantity
        """
        item = self.cart_items.nth(index)
        return {
            "name": item.locator(".inventory_item_name").inner_text(),
            "description": item.locator(".inventory_item_desc").inner_text(),
            "price": item.locator(".inventory_item_price").inner_text(),
            "quantity": item.locator(".cart_quantity").inner_text()
        }

    def get_subtotal(self):
        """Get the subtotal amount (before tax).

        Returns:
            float: Subtotal amount
        """
        # Format: "Item total: $XX.XX"
        text = self.subtotal_label.inner_text()
        # Extract number after '$'
        return float(text.split("$")[1])

    def get_tax(self):
        """Get the tax amount.

        Returns:
            float: Tax amount
        """
        # Format: "Tax: $X.XX"
        text = self.tax_label.inner_text()
        return float(text.split("$")[1])

    def get_total(self):
        """Get the total amount (subtotal + tax).

        Returns:
            float: Total amount
        """
        # Format: "Total: $XX.XX"
        text = self.total_label.inner_text()
        return float(text.split("$")[1])

    def get_payment_info(self):
        """Get the payment information text."""
        return self.payment_info.inner_text()

    def get_shipping_info(self):
        """Get the shipping information text."""
        return self.shipping_info.inner_text()

    def finish_order(self):
        """Click finish button to complete the order."""
        from models.checkout import CheckoutCompletePage
        self.finish_button.click()
        return CheckoutCompletePage(self.page)

    def cancel_order(self):
        """Click cancel button to return to inventory."""
        from models.inventory import InventoryPage
        self.cancel_button.click()
        return InventoryPage(self.page)

    def verify_calculations(self):
        """Verify that subtotal + tax equals total.

        Returns:
            bool: True if calculations are correct, False otherwise
        """
        subtotal = self.get_subtotal()
        tax = self.get_tax()
        total = self.get_total()

        # Allow small floating point differences
        calculated_total = round(subtotal + tax, 2)
        return abs(calculated_total - total) < 0.01
