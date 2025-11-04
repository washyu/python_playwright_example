from playwright.sync_api import Page


class InventoryPage:

    def __init__(self, page: Page):
        self.page = page
        self.inventory_list = page.locator(".inventory_list")
        self.shopping_cart = page.locator("#shopping_cart_container")

    def is_loaded(self):
        """Verify the inventory page is loaded."""
        return self.inventory_list.is_visible()

    def get_product_count(self):
        """Get the number of products displayed."""
        return self.page.locator(".inventory_item").count()
