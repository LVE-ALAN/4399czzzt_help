import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import numpy as np
import pyautogui
from core.ocr_engine import capture_and_search

class MainWindow:
    """答题主窗口（自动扫描、显示结果）"""
    def __init__(self, root, data, region):
        self.root = root
        self.data = data
        self.region = region
        self.last_result = ""
        self.running = True
        self._scanning = False
        self._last_frame = None
        self.scan_interval_ms = 2500

        root.title("📖 村长征战团 · 答题秒查器")
        root.geometry("500x440")
        root.attributes('-topmost', True)
        root.resizable(False, False)

        info_label = tk.Label(
            root,
            text=f"📊 数据已加载：{len(data)} 条 | 区域: {region[0]},{region[1]} {region[2]}x{region[3]}",
            font=("微软雅黑", 9),
            fg="gray"
        )
        info_label.pack(pady=(8, 0))

        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(pady=5)

        self.auto_var = tk.BooleanVar(value=True)
        auto_check = tk.Checkbutton(ctrl_frame, text="⏳ 自动扫描", variable=self.auto_var,
                                    font=("微软雅黑", 10), command=self.toggle_auto)
        auto_check.pack(side='left', padx=5)

        scan_btn = tk.Button(ctrl_frame, text="🔄 手动扫描", font=("微软雅黑", 10),
                             command=self.do_manual_scan)
        scan_btn.pack(side='left', padx=5)

        clear_btn = tk.Button(ctrl_frame, text="🗑️ 清空", font=("微软雅黑", 10),
                              command=self.do_clear)
        clear_btn.pack(side='left', padx=5)

        tk.Label(ctrl_frame, text="间隔(ms)", font=("微软雅黑", 9)).pack(side='left', padx=(8, 2))
        self.interval_var = tk.StringVar(value="2500")
        interval_spin = tk.Spinbox(ctrl_frame, from_=500, to=10000, increment=500,
                                   width=6, textvariable=self.interval_var,
                                   font=("微软雅黑", 9))
        interval_spin.pack(side='left')

        self.result_box = scrolledtext.ScrolledText(
            root, font=("微软雅黑", 13), wrap=tk.WORD, height=10
        )
        self.result_box.pack(padx=15, pady=5, fill='both', expand=True)
        self.result_box.insert(tk.END, "🟢 自动扫描已启动\n等待题目出现...")
        self.result_box.config(state='disabled')

        self.status = tk.Label(root, text="✅ 自动扫描中 (每2.5秒)", fg="green", font=("微软雅黑", 9))
        self.status.pack(side='bottom', pady=3)

        self._tick()

    def _tick(self):
        if not self.running:
            return
        if self.auto_var.get() and not self._scanning:
            try:
                self.scan_interval_ms = max(500, min(10000, int(self.interval_var.get())))
            except:
                pass
            self._auto_scan()
        self.root.after(self.scan_interval_ms, self._tick)

    def _frame_changed(self, img_np, threshold=0.02):
        if self._last_frame is None:
            self._last_frame = img_np
            return True
        diff = np.abs(img_np.astype(np.int16) - self._last_frame.astype(np.int16))
        changed_ratio = float((diff > 10).mean())
        self._last_frame = img_np
        return changed_ratio > threshold

    def _auto_scan(self):
        if not self.region:
            return
        self._scanning = True
        def do_ocr():
            try:
                img_np = np.array(pyautogui.screenshot(region=self.region))
                if not self._frame_changed(img_np):
                    return
                result = capture_and_search(self.region, self.data, img_np=img_np)
                if result and result != self.last_result:
                    self.last_result = result
                    self.root.after(0, lambda: self._update_result(result))
            finally:
                self._scanning = False
        threading.Thread(target=do_ocr, daemon=True).start()

    def _update_result(self, result):
        self.result_box.config(state='normal')
        self.result_box.delete('1.0', tk.END)
        self.result_box.insert(tk.END, result)
        self.result_box.config(state='disabled')
        self.status.config(text="✅ 已更新", fg="green")

    def do_manual_scan(self):
        if not self.region:
            return
        if self._scanning:
            self.status.config(text="⏳ 正在扫描中...", fg="orange")
            return
        self._scanning = True
        self.status.config(text="⏳ 手动扫描中...", fg="orange")
        def do():
            try:
                self._last_frame = None
                result = capture_and_search(self.region, self.data, verbose=True)
                self.root.after(0, lambda: self._update_result(result))
                self.root.after(0, lambda: self.status.config(text="✅ 手动扫描完成", fg="green"))
            finally:
                self._scanning = False
        threading.Thread(target=do, daemon=True).start()

    def do_clear(self):
        self.result_box.config(state='normal')
        self.result_box.delete('1.0', tk.END)
        self.result_box.insert(tk.END, "已清空，等待新题目...")
        self.result_box.config(state='disabled')
        self.last_result = ""
        self._last_frame = None
        self.status.config(text="已清空", fg="gray")

    def toggle_auto(self):
        if self.auto_var.get():
            self.status.config(text="✅ 自动扫描已开启", fg="green")
        else:
            self.status.config(text="⏸️ 自动扫描已暂停", fg="orange")

    def on_closing(self):
        self.running = False
        self.root.destroy()