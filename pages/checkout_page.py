from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Handles the multi-step checkout journey."""

    FIRST_NAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-First Name")
    LAST_NAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Last Name")
    POSTAL_CODE_FIELD = (AppiumBy.ACCESSIBILITY_ID, "test-Zip/Postal Code")
    CONTINUE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-CONTINUE")
    FINISH_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-FINISH")
    ERROR_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, "test-Error message")
    ORDER_COMPLETE_TEXT = (AppiumBy.ACCESSIBILITY_ID, "test-CHECKOUT: COMPLETE!")

    def enter_shipping_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.type(self.FIRST_NAME_FIELD, first_name, description="checkout first name")
        self.type(self.LAST_NAME_FIELD, last_name, description="checkout last name")
        self.type(self.POSTAL_CODE_FIELD, postal_code, description="checkout postal code")

    def continue_to_overview(self) -> None:
        self.click(self.CONTINUE_BUTTON, description="checkout continue button")

    def finish(self) -> None:
        self.click(self.FINISH_BUTTON, description="checkout finish button")

    def get_error_text(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_order_complete(self) -> bool:
        return self.is_visible(self.ORDER_COMPLETE_TEXT, description="order complete message")
