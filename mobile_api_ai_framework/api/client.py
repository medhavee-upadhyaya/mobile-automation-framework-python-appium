"""API client layer for orchestrating fake backend data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .endpoints import ApiEndpoints

DATA_PATH = Path(__file__).resolve().parent / "data" / "products.json"


@dataclass
class Product:
    name: str
    price: str
    description: str


class MobileApiClient:
    """Facade that simulates backend operations for test orchestration."""

    def __init__(self, data_path: Path = DATA_PATH):
        self.data_path = data_path
        self._payload = self._load_payload()

    def _load_payload(self) -> Dict:
        with self.data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _get_product_map(self) -> Dict[str, Product]:
        return {
            entry["name"]: Product(
                name=entry["name"],
                price=entry["price"],
                description=entry["description"],
            )
            for entry in self._payload[ApiEndpoints.PRODUCTS]
        }

    def get_featured_product(self, user_type: str = "standard_user") -> Product:
        product_name = self._payload[ApiEndpoints.FEATURED][user_type]
        return self._get_product_map()[product_name]

    def get_recommended_bundle(self, user_type: str = "standard_user") -> List[Product]:
        bundle = self._payload[ApiEndpoints.BUNDLES][user_type]
        product_map = self._get_product_map()
        return [product_map[name] for name in bundle]

    def build_cart_payload(self, user_type: str = "standard_user") -> Dict:
        products = [product.__dict__ for product in self.get_recommended_bundle(user_type)]
        return {
            "user": user_type,
            "products": products,
            "total": sum(float(p["price"].replace("$", "")) for p in products),
        }

    def refresh_data(self) -> None:
        """Reload JSON payload to pick up on-the-fly fixture tweaks."""
        self._payload = self._load_payload()


__all__ = ["MobileApiClient", "Product"]
