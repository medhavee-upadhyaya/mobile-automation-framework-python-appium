from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_FIELD = (By.ID, "com.example.sample:id/input_username")
    PASSWORD_FIELD = (By.ID, "com.example.sample:id/input_password")
    LOGIN_BUTTON = (By.ID, "com.example.sample:id/button_login")
    ERROR_MESSAGE = (By.ID, "com.example.sample:id/text_error")

    def login(self, username: str, password: str) -> None:
        self.logger.info("Attempting login with username=%s", username)
        self.type(self.USERNAME_FIELD, username)
        self.type(self.PASSWORD_FIELD, password)
        self.click(self.LOGIN_BUTTON)

    def is_login_successful(self) -> bool:
        # TODO: Replace placeholder with correct success condition once the home screen identifiers are known.
        self.logger.debug("Checking login success placeholder using error message visibility")
        return not self.is_visible(self.ERROR_MESSAGE, timeout=5)

    def has_validation_error(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE, timeout=5)
