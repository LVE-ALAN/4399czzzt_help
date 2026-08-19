import pyautogui
import time
from .vision import find_template_on_screen, find_all_templates_on_screen

class Clicker:
    def __init__(self, config):
        self.config = config or {}
        self.default_confidence = self.config.get('vision', {}).get('template_match_threshold', 0.7)

    def click_template(self, template_path, confidence=None, wait_after=0.5, region=None):
        """点击单个模板图片位置"""
        if confidence is None:
            confidence = self.default_confidence
        pos = find_template_on_screen(template_path, confidence, region)
        if pos is None:
            return False
        x, y, w, h = pos
        center_x = x + w//2
        center_y = y + h//2
        pyautogui.click(center_x, center_y)
        if wait_after > 0:
            time.sleep(wait_after)
        return True

    def click_coord(self, x, y, wait_after=0.5):
        """点击指定坐标"""
        pyautogui.click(x, y)
        if wait_after > 0:
            time.sleep(wait_after)

    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

    def find_template(self, template_path, confidence=None, region=None):
        """返回单个模板位置 (x, y, w, h) 或 None"""
        if confidence is None:
            confidence = self.default_confidence
        return find_template_on_screen(template_path, confidence, region)

    def find_templates_sorted(self, template_path, confidence=None, max_results=5):
        """返回所有匹配模板位置，按垂直排序"""
        if confidence is None:
            confidence = self.default_confidence
        return find_all_templates_on_screen(template_path, confidence, max_results)

    def wait_for_template(self, template_path, timeout=10, confidence=None, region=None):
        """
        等待模板出现在屏幕上，超时返回 False
        """
        if confidence is None:
            confidence = self.default_confidence
        start = time.time()
        while time.time() - start < timeout:
            pos = find_template_on_screen(template_path, confidence, region)
            if pos is not None:
                return True
            time.sleep(0.3)
        return False