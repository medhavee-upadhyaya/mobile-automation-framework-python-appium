import pytest

from mobile_api_ai_framework.api.client import MobileApiClient
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage
from utils.logger import get_logger


@pytest.mark.usefixtures("driver")
class TestApiMobileIntegration:
    def setup_method(self):
        self.logger = get_logger(self.__class__.__name__)
        self.api_client = MobileApiClient()

    def _login(self, driver):
        login_page = LoginPage(driver)
        login_page.login()
        products_page = ProductsPage(driver)
        assert products_page.is_loaded(), "Products screen not loaded after login"
        return products_page

    @pytest.mark.regression
    def test_api_defined_product_details(self, driver):
        product = self.api_client.get_featured_product()
        products_page = self._login(driver)

        products_page.open_product_by_name(product.name)
        detail_page = ProductDetailPage(driver)
        detail_page.wait_until_loaded(timeout=20)
        assert detail_page.is_title_displayed(product.name), "Product title not displayed"
        assert detail_page.is_price_displayed(product.price), "Product price mismatch"
        assert detail_page.is_description_matching(product.description.split()[0]), "Description snippet missing"

    @pytest.mark.regression
    def test_api_prepared_cart_bundle(self, driver):
        bundle_payload = self.api_client.build_cart_payload()
        bundle_names = [item["name"] for item in bundle_payload["products"]]

        products_page = self._login(driver)

        for product_name in bundle_names:
            products_page.open_product_by_name(product_name)
            detail_page = ProductDetailPage(driver)
            detail_page.wait_until_loaded()
            detail_page.add_to_cart()
            detail_page.go_back_to_products()

        products_page.go_to_cart()
        cart_page = CartPage(driver)
        cart_page.wait_for_items(timeout=20)
        cart_items = cart_page.get_item_names()

        for expected in bundle_names:
            assert expected in cart_items, f"{expected} not found in cart despite API preparation"
