import os
from typing import Tuple

import cv2
import numpy as np


class VisualValidator:
    """
    Simple visual assertion helper using OpenCV template matching.
    Used to compare expected UI fragments (icons, buttons, banners) against screenshots.
    """

    def __init__(self, baseline_dir: str = "visual/baseline"):
        self.baseline_dir = baseline_dir
        os.makedirs(self.baseline_dir, exist_ok=True)

    def _load_image(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to read image: {path}")
        return img

    def assert_template_present(
        self,
        screenshot_path: str,
        template_name: str,
        threshold: float = 0.85,
    ) -> Tuple[bool, float]:
        """
        Returns (is_match, max_score)
        - screenshot_path: full path to current screenshot from tests
        - template_name: file name inside baseline_dir (e.g. 'login_button.png')
        """
        screenshot = self._load_image(screenshot_path)
        template_path = os.path.join(self.baseline_dir, template_name)
        template = self._load_image(template_path)

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        is_match = max_val >= threshold
        return is_match, max_val
