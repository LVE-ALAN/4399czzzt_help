import sys
import tkinter as tk
from core.ocr_engine import load_data_from_excel
from core.vision import RegionSelector
from gui.main_window import MainWindow
from utils.config_loader import load_config
from utils.logger import setup_logger

def run_answer_task():
    """执行答题任务（独立窗口）"""
    print("=" * 50)
    print("📖 启动答题助手...")
    print("=" * 50)

    config = load_config("config.json")
    logger = setup_logger(config.get('logging', {}).get('file', 'logs/automation.log'))

    data, msg = load_data_from_excel("data/武将属性.xlsx")
    if data is None:
        print(msg)
        input("按回车键退出...")
        return

    region = config.get('window', {}).get('region')
    if region is None:
        print("🖱️ 请用鼠标拖选游戏中的【题目+选项】区域...")
        selector = RegionSelector()
        region = selector.get_region()
        if region is None:
            print("❌ 未选择区域，程序退出")
            return
        print(f"✅ 已锁定区域: {region}")

    root = tk.Tk()
    app = MainWindow(root, data, region)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()