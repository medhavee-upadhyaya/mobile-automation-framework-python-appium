import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import allure
except ImportError:  # pragma: no cover - allure is optional in some environments
    allure = None  # type: ignore

from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import get_logger

LOGGER = get_logger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = REPO_ROOT / "reports" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

Locator = Tuple[str, str]
DEFAULT_TIMEOUT = 30


def wait_for_element(driver, locator: Locator, timeout: Optional[int] = None):
    wait = WebDriverWait(driver, timeout or DEFAULT_TIMEOUT)
    LOGGER.debug("Waiting for element %s for %ss", locator, timeout or DEFAULT_TIMEOUT)
    return wait.until(EC.presence_of_element_located(locator))


def wait_for_element_to_be_clickable(driver, locator: Locator, timeout: Optional[int] = None):
    wait = WebDriverWait(driver, timeout or DEFAULT_TIMEOUT)
    LOGGER.debug("Waiting for element %s to be clickable for %ss", locator, timeout or DEFAULT_TIMEOUT)
    return wait.until(EC.element_to_be_clickable(locator))


def tap_element(driver, locator: Locator, timeout: Optional[int] = None):
    element = wait_for_element_to_be_clickable(driver, locator, timeout)
    LOGGER.info("Tapping on element %s", locator)
    element.click()


def type_text(driver, locator: Locator, text: str, timeout: Optional[int] = None):
    element = wait_for_element(driver, locator, timeout)
    LOGGER.info("Typing into element %s", locator)
    element.clear()
    element.send_keys(text)


def swipe(driver, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 800):
    LOGGER.info("Swiping from (%s,%s) to (%s,%s)", start_x, start_y, end_x, end_y)
    driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
    time.sleep(1)


def scroll_to_text(driver, text: str):
    LOGGER.info("Scrolling to text containing '%s'", text)
    ui_automator = (
        "new UiScrollable(new UiSelector().scrollable(true).instance(0))"
        f".scrollIntoView(new UiSelector().textContains(\"{text}\").instance(0));"
    )
    return driver.find_element(MobileBy.ANDROID_UIAUTOMATOR, ui_automator)


def scroll_to_element(driver, locator: Locator):
    LOGGER.info("Scrolling until element %s is visible", locator)
    # Placeholder logic - to be replaced with custom scroll strategy when app is available.
    for _ in range(5):
        try:
            element = driver.find_element(*locator)
            if element.is_displayed():
                return element
        except Exception:  # pylint: disable=broad-except
            pass
        swipe(driver, 500, 1500, 500, 500)
    raise TimeoutError(f"Element {locator} not visible after scrolling attempts")


def get_text(driver, locator: Locator, timeout: Optional[int] = None) -> str:
    element = wait_for_element(driver, locator, timeout)
    text = element.text
    LOGGER.debug("Retrieved text '%s' from element %s", text, locator)
    return text


def is_element_visible(driver, locator: Locator, timeout: Optional[int] = None) -> bool:
    try:
        element = wait_for_element(driver, locator, timeout)
        visibility = element.is_displayed()
        LOGGER.debug("Element %s visibility: %s", locator, visibility)
        return visibility
    except Exception:  # pylint: disable=broad-except
        LOGGER.debug("Element %s was not visible", locator)
        return False


def attach_screenshot(driver, name: str = "screenshot") -> Optional[Path]:
    """Save and attach a screenshot to Allure reports when available."""
    timestamp = int(time.time() * 1000)
    screenshot_path = SCREENSHOT_DIR / f"{name}_{timestamp}.png"
    driver.save_screenshot(str(screenshot_path))
    LOGGER.info("Screenshot saved at %s", screenshot_path)

    if allure:
        allure.attach.file(str(screenshot_path), name=name, attachment_type=allure.attachment_type.PNG)
    return screenshot_path
