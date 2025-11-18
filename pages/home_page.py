from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    USER_AVATAR = (By.ID, "com.example.sample:id/image_user_avatar")
    LOGOUT_BUTTON = (By.ID, "com.example.sample:id/button_logout")

    def is_user_logged_in(self) -> bool:
        # TODO: Replace with a reliable locator/condition from the actual app.
        self.logger.debug("Checking if user avatar is visible as proof of login")
        return self.is_visible(self.USER_AVATAR, timeout=10)

    def logout(self) -> None:
        # TODO: Update action chain when app navigation flow is available.
        self.logger.info("Attempting to log out")
        self.click(self.LOGOUT_BUTTON)
