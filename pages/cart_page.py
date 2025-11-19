from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class CartPage(BasePage):
    """Represents the cart summary screen."""

    TITLE = (AppiumBy.ACCESSIBILITY_ID, "test-Cart")
    CART_ITEM_LOCATORS = (
        (AppiumBy.ACCESSIBILITY_ID, "test-Item title"),
        (AppiumBy.ACCESSIBILITY_ID, "test-Item"),
    )
    REMOVE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-REMOVE")
    CHECKOUT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-CHECKOUT")
    CONTINUE_SHOPPING_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-CONTINUE SHOPPING")

    def is_loaded(self) -> bool:
        return self.is_visible(self.TITLE, description="cart title")

    def _first_item_locator(self):
        return self.CART_ITEM_LOCATORS[0]

    def _all_item_elements(self):
        elements = []
        for locator in self.CART_ITEM_LOCATORS:
            elements.extend(self.driver.find_elements(*locator))
        return elements

    def get_item_count(self) -> int:
        return len(self._all_item_elements())

    def wait_for_items(self, timeout: int = 10) -> None:
        for locator in self.CART_ITEM_LOCATORS:
            try:
                self.wait_for(locator, timeout=timeout)
                return
            except Exception:  # pylint: disable=broad-except
                continue
        raise TimeoutError("Cart items failed to appear")

    def has_items(self) -> bool:
        return self.get_item_count() > 0

    def wait_until_empty(self, timeout: int = 5) -> None:
        WebDriverWait(self.driver, timeout).until(lambda d: len(self._all_item_elements()) == 0)

    def get_item_names(self) -> list[str]:
        return [(element.text or "").strip() for element in self._all_item_elements() if (element.text or "").strip()]

    def remove_first_item(self) -> None:
        self.click(self.REMOVE_BUTTON, description="remove cart item")

    def continue_shopping(self) -> None:
        self.click(self.CONTINUE_SHOPPING_BUTTON, description="continue shopping")

    def proceed_to_checkout(self) -> None:
        self.click(self.CHECKOUT_BUTTON, description="checkout button")
