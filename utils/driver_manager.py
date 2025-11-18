import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options

from utils.logger import get_logger

LOGGER = get_logger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_PATH = REPO_ROOT / "config" / "capabilities.json"
CONFIG_PATH = REPO_ROOT / "config" / "config.yaml"
APPIUM_SERVER_URL = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")


def _load_capabilities() -> Dict[str, Any]:
    LOGGER.info("Loading capabilities from %s", CAPABILITIES_PATH)
    with CAPABILITIES_PATH.open("r", encoding="utf-8") as cap_file:
        return json.load(cap_file)


def _load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        LOGGER.warning("Config file not found at %s. Using defaults.", CONFIG_PATH)
        return {}

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


def get_driver() -> webdriver.Remote:
    """Instantiate and return an Appium Remote driver using repo capabilities."""
    capabilities = _load_capabilities()
    config = _load_config()

    LOGGER.info("Starting Appium session on %s", APPIUM_SERVER_URL)
    options = UiAutomator2Options().load_capabilities(capabilities)
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)

    implicit_wait = config.get("implicit_wait", 10)
    driver.implicitly_wait(implicit_wait)
    LOGGER.info("Driver started with implicit wait set to %ss", implicit_wait)
    return driver


def quit_driver(driver: webdriver.Remote) -> None:
    if not driver:
        return

    try:
        driver.quit()
        LOGGER.info("Driver session quit successfully")
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error("Failed to quit driver cleanly: %s", exc)
