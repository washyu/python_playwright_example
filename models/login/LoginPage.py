from models.inventory import InventoryPage


class LoginPage:

    def __init__(self, page):
        self.page = page
        self.username_input = page.locator("#user-name")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator("[data-test='error']")

    def navigate(self):
        self.page.goto("https://www.saucedemo.com/")

    def has_error(self):
        """Check if an error message is displayed."""
        return self.error_message.is_visible()

    def get_error_text(self):
        """Get the error message text."""
        return self.error_message.inner_text()

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        # Return the next page after successful login
        return InventoryPage(self.page)
