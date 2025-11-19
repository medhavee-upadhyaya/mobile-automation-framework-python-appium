from typing import Callable, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ai_locators.fallback_locator import AILocatorFallback
from utils.helpers import (
    attach_screenshot,
    get_text,
    scroll_to_element,
    tap_element,
    type_text,
    wait_for_element,
    wait_for_element_to_be_clickable,
)
from utils.logger import get_logger

Locator = tuple[str, str]


class BasePage:
    """Base class exposing common mobile interactions."""

    DEFAULT_TIMEOUT = 15

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)
        self.ai_locator = AILocatorFallback(driver)

    def _resolve_timeout(self, timeout: Optional[int]) -> int:
        return timeout if timeout is not None else self.DEFAULT_TIMEOUT

    def _execute_with_logging(
        self,
        action: str,
        locator: Locator,
        func: Callable[[Locator], WebElement | bool | None],
        use_fallback: bool = False,
        description: Optional[str] = None,
    ):
        try:
            return func(locator)
        except (TimeoutException, NoSuchElementException) as exc:
            if use_fallback:
                self.logger.warning(
                    "Primary locator %s failed for action '%s'. Attempting AI fallback.",
                    locator,
                    action,
                )
                try:
                    fallback_locator = self.ai_locator.find_with_fallback(locator, description or action)
                except Exception as fallback_exc:  # pylint: disable=broad-except
                    self.logger.error(
                        "AI fallback failed for action '%s' on locator %s: %s",
                        action,
                        locator,
                        fallback_exc,
                    )
                    attach_screenshot(self.driver, name=f"{action.replace(' ', '_')}_failure")
                    raise

                self.logger.info(
                    "Retrying action '%s' using fallback locator %s", action, fallback_locator
                )
                return self._execute_with_logging(
                    action,
                    fallback_locator,
                    func,
                    use_fallback=False,
                    description=description,
                )

            self.logger.error("Failed to %s on locator %s: %s", action, locator, exc)
            attach_screenshot(self.driver, name=f"{action.replace(' ', '_')}_failure")
            raise
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error("Failed to %s on locator %s: %s", action, locator, exc)
            attach_screenshot(self.driver, name=f"{action.replace(' ', '_')}_failure")
            raise

    def find_element(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        actual_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Finding element %s with timeout %ss", locator, actual_timeout)
        return self._execute_with_logging(
            "find element",
            locator,
            lambda target: wait_for_element(self.driver, target, actual_timeout),
        )

    def wait_for_clickable(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        actual_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Waiting for element %s to be clickable for %ss", locator, actual_timeout)
        return self._execute_with_logging(
            "wait for clickable",
            locator,
            lambda target: wait_for_element_to_be_clickable(self.driver, target, actual_timeout),
        )

    def click(self, locator: Locator, timeout: Optional[int] = None, description: Optional[str] = None) -> None:
        actual_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Clicking element %s with timeout %ss", locator, actual_timeout)
        self._execute_with_logging(
            "click",
            locator,
            lambda target: tap_element(self.driver, target, actual_timeout),
            use_fallback=True,
            description=description,
        )

    def type(
        self,
        locator: Locator,
        text: str,
        timeout: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        actual_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Typing '%s' into element %s with timeout %ss", text, locator, actual_timeout)
        self._execute_with_logging(
            "type",
            locator,
            lambda target: type_text(self.driver, target, text, actual_timeout),
            use_fallback=True,
            description=description,
        )

    def get_text(self, locator: Locator, timeout: Optional[int] = None) -> str:
        actual_timeout = self._resolve_timeout(timeout)
        self.logger.debug("Getting text from element %s with timeout %ss", locator, actual_timeout)
        return self._execute_with_logging(
            "get text",
            locator,
            lambda target: get_text(self.driver, target, actual_timeout),
        )

    def is_visible(
        self,
        locator: Locator,
        timeout: Optional[int] = None,
        description: Optional[str] = None,
    ) -> bool:
        actual_timeout = self._resolve_timeout(timeout)

        def _check(target: Locator) -> bool:
            element = wait_for_element(self.driver, target, actual_timeout)
            visible = element.is_displayed()
            self.logger.debug("Element %s visible: %s", target, visible)
            return visible

        try:
            return bool(
                self._execute_with_logging(
                    "visibility check",
                    locator,
                    _check,
                    use_fallback=True,
                    description=description,
                )
            )
        except TimeoutException:
            self.logger.debug("Element %s not visible within %ss", locator, actual_timeout)
            return False

    def scroll_to(self, locator: Locator) -> WebElement:
        self.logger.debug("Scrolling to element %s", locator)
        return self._execute_with_logging(
            "scroll to",
            locator,
            lambda target: scroll_to_element(self.driver, target),
        )

    def wait_for(self, locator: Locator, timeout: Optional[int] = None) -> WebElement:
        return self.find_element(locator, timeout)

    def capture_screenshot(self, name: str = "page_state") -> None:
        """Capture a screenshot with an explicit name for debugging."""
        attach_screenshot(self.driver, name=name)
