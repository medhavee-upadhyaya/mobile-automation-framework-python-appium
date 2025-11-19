import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options

from utils.logger import get_logger

LOGGER = get_logger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_PATH = REPO_ROOT / "config" / "capabilities.json"
CONFIG_PATH = REPO_ROOT / "config" / "config.yaml"
APPIUM_SERVER_URL = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
ENV_CAPABILITY_PREFIX = "APPIUM_CAP_"


class DriverManager:
    """Lifecycle helper responsible for creating and disposing Appium drivers."""

    def __init__(
        self,
        capabilities_path: Path = CAPABILITIES_PATH,
        config_path: Path = CONFIG_PATH,
        server_url: str = APPIUM_SERVER_URL,
    ):
        self.capabilities_path = capabilities_path
        self.config_path = config_path
        self.server_url = server_url
        self.driver: Optional[webdriver.Remote] = None

    def _load_capabilities(self) -> Dict[str, Any]:
        LOGGER.info("Loading capabilities from %s", self.capabilities_path)
        with self.capabilities_path.open("r", encoding="utf-8") as cap_file:
            capabilities = json.load(cap_file)

        self._apply_env_overrides(capabilities)
        self._normalize_app_path(capabilities)
        return capabilities

    def _apply_env_overrides(self, capabilities: Dict[str, Any]) -> None:
        """Allow CI or developers to override any capability via environment."""
        for env_key, value in os.environ.items():
            if not env_key.startswith(ENV_CAPABILITY_PREFIX):
                continue
            cap_key = env_key.replace(ENV_CAPABILITY_PREFIX, "")
            LOGGER.info("Overriding capability %s via environment", cap_key)
            capabilities[cap_key] = value

    def _normalize_app_path(self, capabilities: Dict[str, Any]) -> None:
        app_key = next((key for key in capabilities if key.endswith(":app")), None)
        if not app_key:
            return

        app_value = capabilities.get(app_key)
        if not app_value:
            return

        app_path = Path(app_value)
        if not app_path.is_absolute():
            app_path = (REPO_ROOT / app_path).resolve()

        capabilities[app_key] = str(app_path)
        LOGGER.debug("Normalized app path for %s to %s", app_key, app_path)

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            LOGGER.warning("Config file not found at %s. Using defaults.", self.config_path)
            return {}

        with self.config_path.open("r", encoding="utf-8") as config_file:
            return yaml.safe_load(config_file) or {}

    def start(self) -> webdriver.Remote:
        """Instantiate and return an Appium Remote driver using repo capabilities."""
        if self.driver:
            LOGGER.debug("Driver already started, returning existing session.")
            return self.driver

        capabilities = self._load_capabilities()
        config = self._load_config()

        LOGGER.info("Starting Appium session on %s", self.server_url)
        options = UiAutomator2Options().load_capabilities(capabilities)
        self.driver = webdriver.Remote(self.server_url, options=options)

        implicit_wait = config.get("implicit_wait", 10)
        self.driver.implicitly_wait(implicit_wait)
        LOGGER.info("Driver started with implicit wait set to %ss", implicit_wait)
        return self.driver

    def stop(self) -> None:
        if not self.driver:
            LOGGER.debug("No active driver session to stop.")
            return

        try:
            self.driver.quit()
            LOGGER.info("Driver session quit successfully")
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.error("Failed to quit driver cleanly: %s", exc)
        finally:
            self.driver = None

    def __enter__(self) -> webdriver.Remote:
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()


def get_driver() -> webdriver.Remote:
    """Backward compatible helper for existing fixtures."""
    return DriverManager().start()


def quit_driver(driver: webdriver.Remote) -> None:
    if not driver:
        return

    try:
        driver.quit()
        LOGGER.info("Driver session quit successfully")
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error("Failed to quit driver cleanly: %s", exc)
