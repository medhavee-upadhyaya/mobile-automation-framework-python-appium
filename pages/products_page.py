from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

from pages.base_page import BasePage
from utils.helpers import scroll_to_text


class ProductsPage(BasePage):
    """Inventory listing that appears after login."""

    SCREEN_TITLE = (AppiumBy.ACCESSIBILITY_ID, "test-Cart drop zone")
    MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Menu")
    CART_ICON = (AppiumBy.ACCESSIBILITY_ID, "test-Cart")
    CART_BADGE = (AppiumBy.ACCESSIBILITY_ID, "test-Cart badge")
    PRODUCT_TITLE = (AppiumBy.ACCESSIBILITY_ID, "test-Item title")
    ADD_TO_CART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART")
    REMOVE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-REMOVE")

    def is_loaded(self) -> bool:
        """Confirm the inventory list is visible."""
        return self.is_visible(self.MENU_BUTTON, description="Inventory menu button")

    def open_first_product(self) -> None:
        """Tap on the first visible product card."""
        self.click(self.PRODUCT_TITLE, description="first product title")

    def add_first_item_to_cart(self) -> None:
        """Add the first visible product to the cart."""
        self.click(self.ADD_TO_CART_BUTTON, description="add first product to cart")

    def remove_first_item_from_cart(self) -> None:
        """Remove the first visible product from the cart."""
        self.click(self.REMOVE_BUTTON, description="remove first product from cart")

    def go_to_cart(self) -> None:
        """Navigate to cart summary screen."""
        self.click(self.CART_ICON, description="cart icon")

    def has_items_in_cart(self) -> bool:
        return self.is_visible(self.CART_BADGE, description="cart badge")

    def get_first_product_name(self) -> str:
        elements = self.driver.find_elements(*self.PRODUCT_TITLE)
        if not elements:
            return ""
        return (elements[0].text or "").strip()

    def open_product_by_name(self, product_name: str) -> None:
        escaped = product_name.replace('"', '\\"')
        locator = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{escaped}")',
        )
        try:
            element = self.driver.find_element(*locator)
        except NoSuchElementException:
            element = scroll_to_text(self.driver, product_name)
        element.click()
