"""UI model for interacting with the login screen."""


class LoginPage:
    """Encapsulates actions and assertions for the login experience."""

    def __init__(self, driver):
        """Store the mobile driver instance for interactions."""
        self.driver = driver

    def submit_credentials(self, username: str, password: str) -> None:
        """Submit login information to authenticate the user."""
        pass
