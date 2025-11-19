"""UI model for the home screen components."""


class HomePage:
    """Provides common operations on the application's home surface."""

    def __init__(self, driver):
        """Keep a reference to the active driver session."""
        self.driver = driver

    def is_loaded(self) -> bool:
        """Return whether the home screen elements are visible."""
        return False
