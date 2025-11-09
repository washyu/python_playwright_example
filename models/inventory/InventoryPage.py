from playwright.sync_api import Page

from models.base import BasePage


class InventoryPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.inventory_list = page.locator(".inventory_list")
        self.shopping_cart = page.locator("#shopping_cart_container")
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.sort_dropdown = page.locator(".product_sort_container")

    def is_loaded(self):
        """Verify the inventory page is loaded."""
        return self.inventory_list.is_visible()

    def get_product_count(self):
        """Get the number of products displayed."""
        return self.page.locator(".inventory_item").count()

    def get_product_list_element(self, position: int):
        return self.inventory_list[position]

    def add_to_cart_by_name(self, product_name: str):
        """Add a product to cart by its name."""
        # Product names are normalized: lowercase, spaces to hyphens
        normalized_name = product_name.lower().replace(" ", "-")
        button = self.page.locator(f"[data-test='add-to-cart-{normalized_name}']")
        button.click()

    def remove_from_cart_by_name(self, product_name: str):
        """Remove a product from cart by its name."""
        normalized_name = product_name.lower().replace(" ", "-")
        button = self.page.locator(f"[data-test='remove-{normalized_name}']")
        button.click()

    def get_cart_badge_count(self):
        """Get the number displayed on the shopping cart badge."""
        if not self.cart_badge.is_visible():
            return 0
        return int(self.cart_badge.inner_text())

    def is_cart_badge_visible(self):
        """Check if cart badge is visible."""
        return self.cart_badge.is_visible()

    def click_cart(self):
        """Click the shopping cart icon."""
        from models.cart import CartPage

        self.shopping_cart.click()
        return CartPage(self.page)

    def sort_products(self, sort_option: str):
        """Sort products by given option.
        Options: 'az' (A to Z), 'za' (Z to A), 'lohi' (low to high), 'hilo' (high to low)
        """
        self.sort_dropdown.select_option(sort_option)

    def get_product_names(self):
        """Get list of all product names in current order."""
        names = self.page.locator(".inventory_item_name").all_inner_texts()
        return names

    def get_product_prices(self):
        """Get list of all product prices in current order."""
        price_elements = self.page.locator(".inventory_item_price").all_inner_texts()
        # Convert to float for comparison, removing '$' sign
        return [float(price.replace("$", "")) for price in price_elements]

    def click_product_name(self, product_name: str):
        """Click on a product name to go to product details."""
        from models.product_details import ProductDetailsPage

        product = self.page.locator(".inventory_item_name", has_text=product_name)
        product.click()
        return ProductDetailsPage(self.page)

    def click_product_image(self, index: int = 0):
        """Click on a product image by index."""
        from models.product_details import ProductDetailsPage

        images = self.page.locator(".inventory_item_img")
        images.nth(index).click()
        return ProductDetailsPage(self.page)

    def get_product_details(self, index: int):
        """Get details of a product by index."""
        items = self.page.locator(".inventory_item")
        item = items.nth(index)

        return {
            "name": item.locator(".inventory_item_name").inner_text(),
            "description": item.locator(".inventory_item_desc").inner_text(),
            "price": item.locator(".inventory_item_price").inner_text(),
        }
