import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np

from utils.logger import get_logger

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_DIR = REPO_ROOT / "visual" / "baseline"
ACTUAL_DIR = REPO_ROOT / "reports" / "visual" / "actual"
DIFF_DIR = REPO_ROOT / "reports" / "visual" / "diff"


@dataclass
class VisualComparisonResult:
    matched: bool
    score: float
    baseline_path: Path
    actual_path: Path
    diff_path: Optional[Path]
    baseline_created: bool = False

    def to_dict(self) -> Dict[str, str | float | bool | None]:
        return {
            "matched": self.matched,
            "score": round(self.score, 4),
            "baseline_path": str(self.baseline_path),
            "actual_path": str(self.actual_path),
            "diff_path": str(self.diff_path) if self.diff_path else None,
            "baseline_created": self.baseline_created,
        }


class VisualValidator:
    """
    Visual regression helper leveraging OpenCV.
    Features:
      * Baseline screenshot management
      * Similarity scoring with configurable thresholds
      * Automatic diff highlighting for regressions
    """

    def __init__(
        self,
        baseline_dir: Path = BASELINE_DIR,
        actual_dir: Path = ACTUAL_DIR,
        diff_dir: Path = DIFF_DIR,
    ):
        self.baseline_dir = Path(baseline_dir)
        self.actual_dir = Path(actual_dir)
        self.diff_dir = Path(diff_dir)
        for folder in (self.baseline_dir, self.actual_dir, self.diff_dir):
            folder.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger(self.__class__.__name__)

    def capture_screenshot(self, driver, name: str) -> Path:
        """Capture a screenshot via Appium driver and store under actual directory."""
        timestamp = int(time.time() * 1000)
        path = self.actual_dir / f"{name}_{timestamp}.png"
        driver.save_screenshot(str(path))
        self.logger.info("Captured screenshot at %s", path)
        return path

    def compare_with_baseline(
        self,
        current_image_path: Path,
        baseline_name: str,
        threshold: float = 0.98,
        update_baseline: bool = False,
    ) -> VisualComparisonResult:
        """
        Compare provided screenshot with stored baseline.
        Optionally create/update baseline if it does not exist.
        """
        baseline_path = self.baseline_dir / baseline_name
        actual_path = Path(current_image_path)

        if not baseline_path.exists():
            if update_baseline:
                shutil.copy(actual_path, baseline_path)
                self.logger.info("Baseline created at %s", baseline_path)
                return VisualComparisonResult(
                    matched=True,
                    score=1.0,
                    baseline_path=baseline_path,
                    actual_path=actual_path,
                    diff_path=None,
                    baseline_created=True,
                )
            raise FileNotFoundError(
                f"Baseline image '{baseline_name}' missing at {baseline_path}. "
                "Run with update_baseline=True to create it."
            )

        baseline_img = self._load_image(baseline_path)
        actual_img = self._load_image(actual_path)
        actual_img = self._ensure_same_size(baseline_img, actual_img)

        score, diff_mask = self._calculate_similarity(baseline_img, actual_img)
        matched = score >= threshold
        diff_path = None

        if not matched:
            diff_image = self._highlight_differences(actual_img, diff_mask)
            diff_path = self._save_diff_image(diff_image, baseline_name)
            self.logger.warning(
                "Visual regression detected for %s (score %.4f < %.2f). Diff stored at %s",
                baseline_name,
                score,
                threshold,
                diff_path,
            )

        return VisualComparisonResult(
            matched=matched,
            score=score,
            baseline_path=baseline_path,
            actual_path=actual_path,
            diff_path=diff_path,
        )

    def _load_image(self, path: Path) -> np.ndarray:
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:  # pragma: no cover - defensive
            raise ValueError(f"Failed to read image at {path}")
        return image

    def _ensure_same_size(self, baseline: np.ndarray, actual: np.ndarray) -> np.ndarray:
        if baseline.shape == actual.shape:
            return actual
        resized = cv2.resize(actual, (baseline.shape[1], baseline.shape[0]))
        self.logger.debug("Resized actual image from %s to %s", actual.shape, baseline.shape)
        return resized

    def _calculate_similarity(self, baseline: np.ndarray, actual: np.ndarray) -> tuple[float, np.ndarray]:
        diff = cv2.absdiff(baseline, actual)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

        # Similarity score is inverse of normalized diff magnitude
        score = 1.0 - (float(np.sum(thresh)) / (thresh.size * 255))
        score = max(0.0, min(score, 1.0))
        return score, thresh

    def _highlight_differences(self, actual: np.ndarray, diff_mask: np.ndarray) -> np.ndarray:
        diff_mask = cv2.dilate(diff_mask, None, iterations=2)
        contours, _ = cv2.findContours(diff_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        overlay = actual.copy()
        for contour in contours:
            if cv2.contourArea(contour) < 80:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), 2)
        return overlay

    def _save_diff_image(self, image: np.ndarray, baseline_name: str) -> Path:
        diff_path = self.diff_dir / f"diff_{baseline_name}"
        cv2.imwrite(str(diff_path), image)
        return diff_path
