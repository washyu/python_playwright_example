from playwright.sync_api import Page
from models.base import BasePage


class CartPage(BasePage):
    """Page Object Model for the Shopping Cart page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_list = page.locator(".cart_list")
        self.cart_items = page.locator(".cart_item")
        self.continue_shopping_button = page.locator("[data-test='continue-shopping']")
        self.checkout_button = page.locator("[data-test='checkout']")

    def is_loaded(self):
        """Verify the cart page is loaded."""
        return self.cart_list.is_visible()

    def get_item_count(self):
        """Get the number of items in the cart."""
        return self.cart_items.count()

    def get_item_names(self):
        """Get list of all item names in cart."""
        return self.page.locator(".inventory_item_name").all_inner_texts()

    def get_item_prices(self):
        """Get list of all item prices in cart."""
        price_elements = self.page.locator(".inventory_item_price").all_inner_texts()
        # Convert to float for comparison, removing '$' sign
        return [float(price.replace("$", "")) for price in price_elements]

    def get_item_descriptions(self):
        """Get list of all item descriptions in cart."""
        return self.page.locator(".inventory_item_desc").all_inner_texts()

    def get_item_details(self, index: int = 0):
        """Get details of a specific cart item by index.

        Args:
            index: Index of the cart item (0-based)

        Returns:
            dict: Item details including name, description, and price
        """
        item = self.cart_items.nth(index)
        return {
            "name": item.locator(".inventory_item_name").inner_text(),
            "description": item.locator(".inventory_item_desc").inner_text(),
            "price": item.locator(".inventory_item_price").inner_text()
        }

    def remove_item_by_name(self, product_name: str):
        """Remove an item from cart by product name.

        Args:
            product_name: Name of the product to remove
        """
        # Product names are normalized: lowercase, spaces to hyphens
        normalized_name = product_name.lower().replace(" ", "-")
        button = self.page.locator(f"[data-test='remove-{normalized_name}']")
        button.click()

    def remove_item_by_index(self, index: int):
        """Remove an item from cart by index.

        Args:
            index: Index of the item to remove (0-based)
        """
        remove_button = self.cart_items.nth(index).locator("button")
        remove_button.click()

    def is_cart_empty(self):
        """Check if the cart is empty."""
        return self.cart_items.count() == 0

    def continue_shopping(self):
        """Click continue shopping button to return to inventory."""
        from models.inventory import InventoryPage
        self.continue_shopping_button.click()
        return InventoryPage(self.page)

    def proceed_to_checkout(self):
        """Click checkout button to proceed to checkout step 1."""
        from models.checkout import CheckoutStepOnePage
        self.checkout_button.click()
        return CheckoutStepOnePage(self.page)

    def clear_cart(self):
        """Remove all items from the cart."""
        while not self.is_cart_empty():
            self.remove_item_by_index(0)
