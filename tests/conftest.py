import pytest

from utils.driver_manager import get_driver, quit_driver
from utils.helpers import attach_screenshot
from utils.logger import get_logger

LOGGER = get_logger(__name__)


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="qa", help="Target test environment")
    parser.addoption("--platform", action="store", default="android", help="Mobile platform to run against")


@pytest.fixture(scope="function")
def driver(request):
    driver_instance = get_driver()
    yield driver_instance

    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        LOGGER.error("Test %s failed. Capturing screenshot.", request.node.name)
        attach_screenshot(driver_instance, name=request.node.name)

    quit_driver(driver_instance)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
