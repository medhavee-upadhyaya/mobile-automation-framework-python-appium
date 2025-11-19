"""Endpoint definitions for the fake backend powering tests."""


class ApiEndpoints:
    PRODUCTS = "products"
    FEATURED = "featured"
    BUNDLES = "bundles"

    _PATHS = {
        PRODUCTS: "/products",
        FEATURED: "/featured",
        BUNDLES: "/bundles",
    }

    @classmethod
    def resolve(cls, name: str) -> str:
        return cls._PATHS.get(name, "")


__all__ = ["ApiEndpoints"]
