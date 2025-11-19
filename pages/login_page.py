from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Interactions for the SwagLabs login screen."""

    USERNAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Username")
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Password")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")
    ERROR_BANNER = (AppiumBy.ACCESSIBILITY_ID, "test-Error")
    ERROR_MESSAGE_TEXT = (AppiumBy.ACCESSIBILITY_ID, "test-Error message")
    LOCKED_OUT_TEXT = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("locked out").className("android.widget.TextView")',
    )

    DEFAULT_USERNAME = "standard_user"
    DEFAULT_PASSWORD = "secret_sauce"

    def login(self, username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> None:
        self.logger.info("Attempting login with username=%s", username)
        self.type(self.USERNAME_FIELD, username, description="login username")
        self.type(self.PASSWORD_FIELD, password, description="login password")
        self.click(self.LOGIN_BUTTON, description="login button")

    def has_validation_error(self, timeout: int = 10) -> bool:
        """Return True if any inline login error locator is visible."""
        locators = (self.ERROR_BANNER, self.ERROR_MESSAGE_TEXT, self.LOCKED_OUT_TEXT)
        return any(self.is_visible(locator, timeout=timeout, description="login error") for locator in locators)

    def _extract_text(self, element) -> str:
        text = (element.text or "").strip()
        if text:
            return text
        for attr in ("text", "name", "label", "value", "contentDescription", "content-desc"):
            attr_value = (element.get_attribute(attr) or "").strip()
            if attr_value:
                return attr_value
        return ""

    def get_error_message(self, timeout: int = 10) -> str:
        """Fetch the inline validation text."""
        def _wait_for_text(locator):
            return WebDriverWait(self.driver, timeout).until(
                lambda driver: (
                    extracted
                    if (element := driver.find_element(*locator)) and (extracted := self._extract_text(element))
                    else None
                )
            )

        for locator in (self.ERROR_MESSAGE_TEXT, self.ERROR_BANNER, self.LOCKED_OUT_TEXT):
            try:
                text = _wait_for_text(locator)
                if text:
                    return text
            except Exception:  # pylint: disable=broad-except
                continue
        return ""

    def wait_for_error_banner(self, timeout: int = 15) -> None:
        """Explicitly wait until error copy is shown."""
        for locator in (self.ERROR_BANNER, self.ERROR_MESSAGE_TEXT, self.LOCKED_OUT_TEXT):
            try:
                self.wait_for(locator, timeout=timeout)
                return
            except Exception:  # pylint: disable=broad-except
                continue
        raise TimeoutError("Error banner did not appear in allotted time")

    def is_login_successful(self) -> bool:
        """SwagLabs redirects to Products page after successful login."""
        from pages.home_page import HomePage  # local import to avoid circular dependency

        return HomePage(self.driver).is_user_logged_in()
