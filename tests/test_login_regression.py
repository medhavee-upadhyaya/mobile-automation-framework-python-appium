import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.logger import get_logger


@pytest.mark.usefixtures("driver")
class TestLoginRegression:
    def setup_method(self):
        self.logger = get_logger(self.__class__.__name__)

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_valid_login(self, driver):
        login_page = LoginPage(driver)
        home_page = HomePage(driver)

        self.logger.info("Starting valid login flow")
        login_page.login("valid_user@example.com", "correct_password")

        # TODO: Replace placeholder assertion with reliable verification once app identifiers exist.
        assert home_page.is_user_logged_in(), "Expected user to be logged in after valid credentials"

    @pytest.mark.regression
    def test_invalid_login_wrong_password(self, driver):
        login_page = LoginPage(driver)

        self.logger.info("Attempting login with wrong password")
        login_page.login("valid_user@example.com", "wrong_password")

        # TODO: Validate specific error text once UI copy is finalized.
        assert login_page.has_validation_error(), "Expected an error when logging in with wrong password"

    @pytest.mark.regression
    @pytest.mark.smoke
    def test_login_empty_fields_validation(self, driver):
        login_page = LoginPage(driver)

        self.logger.info("Verifying validation for empty fields")
        login_page.click(LoginPage.LOGIN_BUTTON)

        # TODO: Add assertions for inline validation messaging once locators are known.
        assert login_page.has_validation_error(), "Expected validation error when submitting empty credentials"
