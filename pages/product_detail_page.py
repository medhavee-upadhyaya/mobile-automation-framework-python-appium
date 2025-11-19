from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    """Detailed information for a particular product."""

    TITLE_LOCATORS = (
        (AppiumBy.ACCESSIBILITY_ID, "test-Item title"),
        (AppiumBy.ACCESSIBILITY_ID, "test-Item"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("test-Item title")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.TextView").index(1)'),
    )
    DESCRIPTION_LOCATORS = (
        (AppiumBy.ACCESSIBILITY_ID, "test-Description"),
        (AppiumBy.ACCESSIBILITY_ID, "test-Item description"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Description")'),
    )
    PRICE_LOCATORS = (
        (AppiumBy.ACCESSIBILITY_ID, "test-Price"),
        (AppiumBy.ACCESSIBILITY_ID, "test-Item price"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("$")'),
    )
    ADD_TO_CART = (AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART")
    REMOVE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-REMOVE")
    BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-BACK TO PRODUCTS")

    def wait_until_loaded(self, timeout: int = 20) -> None:
        self._wait_for_any_locator(self.TITLE_LOCATORS, timeout=timeout)
        self._wait_for_any_locator(self.DESCRIPTION_LOCATORS, timeout=timeout)
        self._wait_for_any_locator(self.PRICE_LOCATORS, timeout=timeout)

    def add_to_cart(self) -> None:
        self.click(self.ADD_TO_CART, description="product details add to cart")

    def remove_from_cart(self) -> None:
        self.click(self.REMOVE_BUTTON, description="product detail remove")

    def go_back_to_products(self) -> None:
        self.click(self.BACK_BUTTON, description="back to products")

    def _wait_for_any_locator(self, locators, timeout: int = 10):
        for locator in locators:
            try:
                return self.wait_for(locator, timeout=timeout)
            except Exception:  # pylint: disable=broad-except
                continue
        raise TimeoutError(f"Unable to locate any of {locators}")

    def _get_text_from_locators(self, locators, timeout: int = 15) -> str:
        for locator in locators:
            try:
                element = self.wait_for(locator, timeout=timeout)
            except Exception:  # pylint: disable=broad-except
                continue
            text = self._extract_text(element)
            if text:
                return text
        raise TimeoutError(f"Text not found for locators {locators}")

    def _extract_text(self, element) -> str:
        candidates = [
            (element.text or "").strip(),
            (element.get_attribute("name") or "").strip(),
            (element.get_attribute("contentDescription") or "").strip(),
            (element.get_attribute("content-desc") or "").strip(),
        ]
        for value in candidates:
            if value:
                return value
        return ""

    def get_title(self) -> str:
        return self._get_text_from_locators(self.TITLE_LOCATORS)

    def get_description(self) -> str:
        return self._get_text_from_locators(self.DESCRIPTION_LOCATORS)

    def get_price(self) -> str:
        return self._get_text_from_locators(self.PRICE_LOCATORS)
