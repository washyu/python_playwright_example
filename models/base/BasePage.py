from playwright.sync_api import Page


class BasePage:
    """Base page class containing common elements like the menu."""

    def __init__(self, page: Page):
        self.page = page
        # Menu elements
        self.menu_button = page.locator("#react-burger-menu-btn")
        self.menu_close_button = page.locator("#react-burger-cross-btn")
        self.menu_wrap = page.locator(".bm-menu-wrap")
        self.logout_link = page.locator("#logout_sidebar_link")
        self.all_items_link = page.locator("#inventory_sidebar_link")
        self.about_link = page.locator("#about_sidebar_link")
        self.reset_app_link = page.locator("#reset_sidebar_link")

    def open_menu(self):
        """Open the hamburger menu."""
        self.menu_button.click()
        # Wait for menu to open (aria-hidden becomes "false")
        self.page.wait_for_function(
            "() => document.querySelector('.bm-menu-wrap').getAttribute('aria-hidden') === 'false'"
        )

    def close_menu(self):
        """Close the hamburger menu using the X button."""
        self.menu_close_button.click()
        # Wait for menu to close (aria-hidden becomes "true")
        self.page.wait_for_function(
            "() => document.querySelector('.bm-menu-wrap').getAttribute('aria-hidden') === 'true'"
        )

    def is_menu_open(self):
        """Check if the menu is open by checking the aria-hidden attribute."""
        # aria-hidden is "false" when open, "true" when closed
        return self.menu_wrap.get_attribute("aria-hidden") == "false"

    def logout(self):
        """Logout from the application."""
        from models.login import LoginPage

        self.open_menu()
        self.logout_link.click()
        return LoginPage(self.page)

    def click_all_items(self):
        """Navigate to inventory page via menu."""
        from models.inventory import InventoryPage

        self.open_menu()
        self.all_items_link.click()
        return InventoryPage(self.page)

    def click_about(self):
        """Click the About link (navigates to external site)."""
        self.open_menu()
        self.about_link.click()

    def reset_app_state(self):
        """Reset the application state (clears cart)."""
        self.open_menu()
        self.reset_app_link.click()
        self.close_menu()

    # Testing utilities
    def take_screenshot(self, name: str, path: str = "screenshots"):
        """Take a screenshot and save it with the given name.

        Args:
            name: Name for the screenshot file (without extension)
            path: Directory to save screenshot (default: 'screenshots')
        """
        import os

        os.makedirs(path, exist_ok=True)
        screenshot_path = os.path.join(path, f"{name}.png")
        self.page.screenshot(path=screenshot_path, full_page=True)
        return screenshot_path

    def get_current_url(self):
        """Get the current page URL."""
        return self.page.url

    def get_page_title(self):
        """Get the page title."""
        return self.page.title()
