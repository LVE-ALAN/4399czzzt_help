import os
import cv2
import numpy as np
import pyautogui
import tkinter as tk


# ========== 图像处理函数 ==========

def imread_chinese(path):
    """支持中文路径的图片读取"""
    if not os.path.exists(path):
        return None
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return img


def find_template_on_screen(template_path, threshold=0.7, region=None):
    """
    在屏幕上查找单个模板图片（支持中文路径）
    返回 (x, y, w, h) 或 None
    """
    template = imread_chinese(template_path)
    if template is None:
        return None
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    screenshot = pyautogui.screenshot(region=region)
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val>=threshold:
        h, w = template_gray.shape
        return (max_loc[0], max_loc[1], w, h)
    return None


def find_all_templates_on_screen(template_path, threshold=0.7, max_results=5):
    """
    在屏幕上查找所有匹配的模板位置，按垂直坐标排序，最多返回 max_results 个
    返回 [(x, y, w, h), ...]
    """
    template = imread_chinese(template_path)
    if template is None:
        return []
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h, w = template_gray.shape

    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result>=threshold)
    positions = []
    for pt in zip(*locations[::-1]):
        positions.append((pt[0], pt[1], w, h))

    positions.sort(key=lambda p: p[1])

    filtered = []
    for pos in positions:
        if not filtered:
            filtered.append(pos)
        else:
            if abs(pos[1] - filtered[-1][1])>15:
                filtered.append(pos)
        if len(filtered)>=max_results:
            break
    return filtered


# ========== 答题区域选择器 ==========

class RegionSelector:
    """拖拽选择区域（用于答题区域选择）"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")
        self.root.title("选择答题区域")

        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(
            self.root,
            text="🖱️ 按住左键在【题目+选项】区域拖出矩形框，松开即确认 | 按 ESC 取消",
            font=("微软雅黑", 14),
            bg='black',
            fg='white'
        )
        self.label.place(relx=0.5, rely=0.05, anchor='n')

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.exit(None))

    def on_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def on_drag(self, event):
        if self.start_x is not None:
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y,
                event.x_root, event.y_root,
                outline='red', width=3
            )

    def on_release(self, event):
        end_x = event.x_root
        end_y = event.y_root
        if self.start_x is None or self.start_y is None:
            return
        if abs(end_x - self.start_x)<10 or abs(end_y - self.start_y)<10:
            self.label.config(text="⚠️ 拖拽区域太小，请重新拖拽", fg="red")
            return
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        region = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
        self.exit(region)

    def exit(self, region):
        self.region = region
        self.root.quit()
        self.root.destroy()

    def get_region(self):
        self.root.mainloop()
        return self.region