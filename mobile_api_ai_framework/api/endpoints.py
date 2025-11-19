"""Endpoint definitions for the mobile API client."""


class EndpointRegistry:
    """Container for service endpoint paths used by the API client."""

    def __init__(self):
        """Initialize the registry with default endpoint mappings."""
        self._endpoints = {}

    def register(self, name: str, path: str) -> None:
        """Register or overwrite an endpoint path under the provided name."""
        self._endpoints[name] = path

    def resolve(self, name: str) -> str:
        """Return the endpoint path for the given name."""
        return self._endpoints.get(name, "")
