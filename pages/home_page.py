from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class HomePage(BasePage):
    MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Menu")
    LOGOUT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Logout")

    def is_user_logged_in(self) -> bool:
        """User is logged in when the Menu button is visible."""
        self.logger.debug("Checking if Menu button is visible as proof of login")
        return self.is_visible(self.MENU_BUTTON, timeout=10)

    def logout(self) -> None:
        """Logout flow for SwagLabs mobile app."""
        self.logger.info("Attempting logout")
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_BUTTON)
