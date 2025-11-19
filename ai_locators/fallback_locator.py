from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from utils.logger import get_logger

Locator = Tuple[str, str]
TARGET_ATTRIBUTES = ("resource-id", "content-desc", "text", "class")


@dataclass
class LocatorCandidate:
    locator: Locator
    score: float
    attributes: Dict[str, str]


class AILocatorFallback:
    """
    AI-powered (heuristic) fallback finder.
    Collects current DOM snapshot, performs fuzzy matching across
    resource-id, text, content-desc, and class attributes, and returns
    the best matching locator when the primary locator fails.
    """

    MIN_SIMILARITY = 0.55

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)

    def find_with_fallback(self, primary: Locator, description: str = "") -> Locator:
        """
        Validate the primary locator and, when it fails, retry using the
        best-match locator from a fuzzy DOM scan.
        """
        try:
            self.driver.find_element(*primary)
            return primary
        except NoSuchElementException as exc:
            self.logger.debug("Primary locator %s failed: %s", primary, exc)
            candidate = self._search_dom(primary, description)
            if candidate:
                self.logger.info(
                    "AI fallback resolved '%s' to %s (score %.2f)",
                    description or primary,
                    candidate.locator,
                    candidate.score,
                )
                return candidate.locator
            raise NoSuchElementException(
                f"Element not found using {primary} and AI fallback "
                f"could not resolve locator for '{description}'."
            ) from exc

    def _search_dom(self, primary: Locator, description: str) -> Optional[LocatorCandidate]:
        page_source = self.driver.page_source
        try:
            root = ET.fromstring(page_source)
        except ET.ParseError as exc:  # pragma: no cover - defensive logging
            self.logger.error("Failed to parse page source for AI fallback: %s", exc)
            return None

        queries = self._build_queries(primary, description)
        best_candidate: Optional[LocatorCandidate] = None

        for element in root.iter():
            attrs = {attr: element.attrib.get(attr, "") for attr in TARGET_ATTRIBUTES}
            if not any(attrs.values()):
                continue

            score = self._score_candidate(attrs, queries)
            if score < self.MIN_SIMILARITY:
                continue

            locator = self._build_locator(attrs)
            if not locator:
                continue

            candidate = LocatorCandidate(locator=locator, score=score, attributes=attrs)
            if not best_candidate or score > best_candidate.score:
                best_candidate = candidate

        return best_candidate

    def _build_queries(self, primary: Locator, description: str) -> List[str]:
        queries = set()
        queries.update(self._tokenize(primary[1]))
        if description:
            queries.update(self._tokenize(description))
        return [query.lower() for query in queries if query]

    def _tokenize(self, value: str) -> List[str]:
        parts = re.split(r"[:/_\-\s]+", value)
        clean_parts = [part for part in parts if part]
        return [value, *clean_parts]

    def _score_candidate(self, attrs: Dict[str, str], queries: List[str]) -> float:
        best_score = 0.0

        for attr_name in TARGET_ATTRIBUTES:
            attr_value = attrs.get(attr_name) or ""
            if not attr_value:
                continue

            normalized_attr = attr_value.lower()
            for query in queries:
                ratio = SequenceMatcher(None, query, normalized_attr).ratio()
                weight = 1.1 if attr_name in ("resource-id", "content-desc") else 1.0
                if attr_name == "class":
                    weight = 0.9
                best_score = max(best_score, min(ratio * weight, 1.0))

        return best_score

    def _build_locator(self, attrs: Dict[str, str]) -> Optional[Locator]:
        content_desc = attrs.get("content-desc")
        if content_desc:
            return (AppiumBy.ACCESSIBILITY_ID, content_desc)

        resource_id = attrs.get("resource-id")
        if resource_id:
            return (AppiumBy.ID, resource_id)

        text_value = attrs.get("text")
        if text_value:
            sanitized = text_value.replace('"', '\\"')
            return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{sanitized}")')

        class_value = attrs.get("class")
        if class_value:
            return (AppiumBy.CLASS_NAME, class_value)

        return None
