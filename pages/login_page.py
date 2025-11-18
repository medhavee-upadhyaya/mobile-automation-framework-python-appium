from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class LoginPage(BasePage):

    USERNAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Username")
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Password")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")
    ERROR_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, "test-Error")

    DEFAULT_USERNAME = "standard_user"
    DEFAULT_PASSWORD = "secret_sauce"

    def login(self, username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> None:
        self.logger.info(f"Attempting login with username={username}")
        self.type(self.USERNAME_FIELD, username)
        self.type(self.PASSWORD_FIELD, password)
        self.click(self.LOGIN_BUTTON)

    def has_validation_error(self) -> bool:
        """Return True if an inline login error message is visible."""
        return self.is_visible(self.ERROR_MESSAGE, timeout=5)

    def is_login_successful(self) -> bool:
        """
        SwagLabs redirects to Products page after successful login.
        A reliable check is to look for an element in HomePage.
        """
        from pages.home_page import HomePage
        return HomePage(self.driver).is_user_logged_in()
