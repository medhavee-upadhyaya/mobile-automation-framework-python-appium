import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage
from utils.logger import get_logger


@pytest.mark.usefixtures("driver")
class TestFunctionalSuite:
    def setup_method(self):
        self.logger = get_logger(self.__class__.__name__)

    def _perform_login(self, driver, username: str = LoginPage.DEFAULT_USERNAME, password: str = LoginPage.DEFAULT_PASSWORD):
        login_page = LoginPage(driver)
        products_page = ProductsPage(driver)
        login_page.login(username=username, password=password)
        assert products_page.is_loaded(), "Expected inventory screen to be visible after login"
        return login_page, products_page

    @pytest.mark.smoke
    def test_login_successful(self, driver):
        """Validate a standard user can sign into the app."""
        _, products_page = self._perform_login(driver)
        assert products_page.is_loaded()

    @pytest.mark.regression
    def test_login_negative_locked_out_user(self, driver):
        """Ensure locked out user receives inline error messaging."""
        login_page = LoginPage(driver)
        login_page.login(username="locked_out_user", password=LoginPage.DEFAULT_PASSWORD)
        login_page.wait_for_error_banner(timeout=20)
        assert login_page.has_validation_error(timeout=5), "Expected locked out user to be prevented from logging in"
        error_message = login_page.get_error_message(timeout=5).lower()
        assert "locked out" in error_message

    @pytest.mark.regression
    def test_logout_flow(self, driver):
        """User can log out via menu and return to login screen."""
        login_page = LoginPage(driver)
        login_page.login()
        home_page = HomePage(driver)
        assert home_page.is_user_logged_in(), "Expected user to be logged in before logout"
        home_page.logout()
        assert login_page.is_visible(LoginPage.LOGIN_BUTTON, description="login button"), "Expected to see login screen after logout"

    @pytest.mark.regression
    def test_add_item_to_cart(self, driver):
        """Add product to cart from product grid."""
        _, products_page = self._perform_login(driver)
        products_page.add_first_item_to_cart()
        # Wait for badge to appear to ensure state was updated
        assert products_page.is_visible(ProductsPage.CART_BADGE, timeout=15, description="cart badge"), "Cart badge should appear after adding an item"
        products_page.go_to_cart()
        cart_page = CartPage(driver)
        assert cart_page.is_loaded(), "Cart page should be visible"
        cart_page.wait_for_items(timeout=20)
        assert cart_page.has_items(), "Cart page should contain added item"

    @pytest.mark.regression
    def test_remove_item_from_cart(self, driver):
        """Remove cart item from product list."""
        _, products_page = self._perform_login(driver)
        products_page.add_first_item_to_cart()
        products_page.go_to_cart()
        cart_page = CartPage(driver)
        assert cart_page.has_items()
        cart_page.remove_first_item()
        cart_page.wait_until_empty()
        assert not cart_page.has_items(), "Cart should be empty after removing the only item"

    @pytest.mark.regression
    def test_product_details_information(self, driver):
        """Validate product details surface metadata and pricing."""
        _, products_page = self._perform_login(driver)
        products_page.open_first_product()
        detail_page = ProductDetailPage(driver)
        detail_page.wait_until_loaded(timeout=20)
        title = detail_page.get_title()
        description = detail_page.get_description()
        price = detail_page.get_price()
        assert title, "Title should be populated on the product details screen"
        assert description, "Description should be populated for the selected product"
        assert price.startswith("$"), "Price should contain currency symbol"
        detail_page.go_back_to_products()
        assert products_page.is_loaded(), "Expected to return to products page"

    @pytest.mark.regression
    @pytest.mark.smoke
    def test_checkout_flow_success(self, driver):
        """Full checkout journey from adding item to confirming order."""
        _, products_page = self._perform_login(driver)
        products_page.add_first_item_to_cart()
        products_page.go_to_cart()
        cart_page = CartPage(driver)
        cart_page.proceed_to_checkout()
        checkout_page = CheckoutPage(driver)
        checkout_page.enter_shipping_information("Test", "User", "12345")
        checkout_page.continue_to_overview()
        checkout_page.finish()
        assert checkout_page.is_order_complete(), "Order completion banner should be visible"

    @pytest.mark.regression
    def test_checkout_missing_information_shows_error(self, driver):
        """Checkout should block progress when required fields are empty."""
        _, products_page = self._perform_login(driver)
        products_page.add_first_item_to_cart()
        products_page.go_to_cart()
        cart_page = CartPage(driver)
        cart_page.proceed_to_checkout()
        checkout_page = CheckoutPage(driver)
        checkout_page.type(CheckoutPage.LAST_NAME_FIELD, "User")
        checkout_page.type(CheckoutPage.POSTAL_CODE_FIELD, "12345")
        checkout_page.continue_to_overview()
        assert checkout_page.is_visible(CheckoutPage.ERROR_MESSAGE, description="checkout error"), "Expected inline error for missing first name"
        error_copy = checkout_page.get_error_text().lower()
        if error_copy:
            assert "first name" in error_copy
