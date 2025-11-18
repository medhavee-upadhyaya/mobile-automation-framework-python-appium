from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from utils.helpers import (
    get_text,
    is_element_visible,
    scroll_to_element,
    tap_element,
    type_text,
    wait_for_element,
)
from utils.logger import get_logger

Locator = tuple[str, str]


class BasePage:
    """Base class exposing common mobile interactions."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)

    def find_element(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        self.logger.debug("Finding element %s", locator)
        return wait_for_element(self.driver, locator, timeout)

    def click(self, locator: Locator, timeout: Optional[int] = None) -> None:
        self.logger.debug("Clicking element %s", locator)
        tap_element(self.driver, locator, timeout)

    def type(self, locator: Locator, text: str, timeout: Optional[int] = None) -> None:
        self.logger.debug("Typing '%s' into element %s", text, locator)
        type_text(self.driver, locator, text, timeout)

    def get_text(self, locator: Locator, timeout: Optional[int] = None) -> str:
        self.logger.debug("Getting text from element %s", locator)
        return get_text(self.driver, locator, timeout)

    def is_visible(self, locator: Locator, timeout: Optional[int] = None) -> bool:
        visible = is_element_visible(self.driver, locator, timeout)
        self.logger.debug("Element %s visible: %s", locator, visible)
        return visible

    def scroll_to(self, locator: Locator) -> WebElement:
        self.logger.debug("Scrolling to element %s", locator)
        return scroll_to_element(self.driver, locator)

    def wait_for(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self.find_element(locator, timeout)
