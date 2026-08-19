import tkinter as tk
from tkinter import messagebox
import threading

from tasks.answer_task import run_answer_task
from tasks.union_contribute_task import UnionContributeTask
from tasks.tech_donate_task import TechDonateTask
from core.clicker import Clicker

class MenuWindow:
    def __init__(self, root):
        self.root = root
        root.title("🎮 村长征战团 · 自动化任务中心")
        root.geometry("600x550")  # 加大窗口
        root.resizable(False, False)
        root.attributes('-topmost', True)

        # 标题
        tk.Label(root, text="请选择要执行的任务", font=("微软雅黑", 16, "bold")).pack(pady=15)

        # 两列网格布局
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10, padx=20, fill='both', expand=True)

        btn_style = {"height": 2, "font": ("微软雅黑", 10)}

        # 定义所有任务按钮（名称, 颜色, 回调函数, 列位置）
        tasks = [
            ("📖 答题助手", "#4CAF50", self.start_answer, 0, 0),
            ("🤝 联盟大厅捐献", "#2196F3", self.start_union, 0, 1),
            ("🏛️科技大厅捐献", "#FF9800", self.start_tech, 0, 2),
            ("💰 收金币", "#9C27B0", self.start_collect, 1, 0),
            ("⚔️ 跨服战", "#E91E63", self.start_future, 1, 1),
            ("🏰 盟战", "#00BCD4", self.start_future, 1, 2),
            ("🎯 武将竞技", "#8BC34A", self.start_future, 2, 0),
            ("📦 护送使者", "#FF5722", self.start_future, 2, 1),
            ("🔄 演武场", "#607D8B", self.start_daily, 2, 2),
            ("🚪 退出", "#f44336", root.quit, 3, 0),
        ]

        for name, color, cmd, row, col in tasks:
            btn = tk.Button(btn_frame, text=name, command=cmd,
                           bg=color, fg="white", width=18, **btn_style)
            btn.grid(row=row, column=col, padx=10, pady=6, sticky='ew')

        # 配置列权重
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        # 状态栏
        self.status = tk.Label(root, text="就绪", fg="gray", font=("微软雅黑", 10))
        self.status.pack(side='bottom', pady=12)

    def set_status(self, text, color="gray"):
        self.status.config(text=text, fg=color)

    # ==================== 答题助手 ====================
    def start_answer(self):
        self.set_status("正在启动答题助手...", "orange")
        self.root.withdraw()
        try:
            run_answer_task()
        except Exception as e:
            messagebox.showerror("错误", f"答题任务启动失败：{e}")
        finally:
            self.root.deiconify()
            self.set_status("答题助手已关闭", "gray")

    # ==================== 联盟大厅捐献 ====================
    def start_union(self):
        self._show_union_dialog()

    def _show_union_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("设置联盟大厅捐献次数")
        dialog.geometry("400x380")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        dialog.grab_set()

        tk.Label(dialog, text="设置四种捐献的次数：", font=("微软雅黑", 12, "bold")).pack(pady=12)

        gold_var = tk.IntVar(value=10)
        diamond_var = tk.IntVar(value=10)
        red_var = tk.IntVar(value=0)
        soul_var = tk.IntVar(value=15)

        def create_row(label_text, var):
            frame = tk.Frame(dialog)
            frame.pack(pady=6, fill='x', padx=30)
            tk.Label(frame, text=label_text, width=10, anchor='w', font=("微软雅黑", 10)).pack(side='left')
            tk.Spinbox(frame, from_=0, to=99, width=10, font=("微软雅黑", 10), textvariable=var).pack(side='right')

        create_row("💰 金币捐献:", gold_var)
        create_row("💎 钻石捐献:", diamond_var)
        create_row("🔴 红钻捐献:", red_var)
        create_row("💀 将魂捐献:", soul_var)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=18)

        def on_confirm():
            gold = gold_var.get()
            diamond = diamond_var.get()
            red = red_var.get()
            soul = soul_var.get()
            if any(x < 0 for x in [gold, diamond, red, soul]):
                messagebox.showerror("错误", "次数不能为负数！")
                return
            dialog.destroy()
            counts = {"金币": gold, "钻石": diamond, "红钻": red, "将魂": soul}
            self.set_status("正在执行联盟大厅捐献任务...", "orange")
            threading.Thread(target=self._run_union_task, args=(counts,), daemon=True).start()

        def on_cancel():
            dialog.destroy()
            self.set_status("已取消", "gray")

        tk.Button(btn_frame, text="✅ 确认", command=on_confirm, width=10, bg="#4CAF50", fg="white").pack(side='left', padx=15)
        tk.Button(btn_frame, text="❌ 取消", command=on_cancel, width=10, bg="#f44336", fg="white").pack(side='left', padx=15)

    def _run_union_task(self, counts):
        engine = {'clicker': Clicker({})}
        task = UnionContributeTask(engine, {'counts': counts})
        result = task.execute()
        self.root.after(0, lambda: self._show_task_result(result))

    # ==================== 科技大厅捐献 ====================
    def start_tech(self):
        self._show_tech_dialog()

    def _show_tech_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("设置科技大厅捐献")
        dialog.geometry("480x600")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        dialog.grab_set()

        # 主容器（带滚动条）
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 标题
        tk.Label(scrollable_frame, text="选择要捐献的科技（勾选即捐献）", font=("微软雅黑", 12, "bold")).pack(pady=10)

        # 科技列表
        tech_names = [
            "士兵防御+4%",
            "士兵生命+1%",
            "士兵攻击+0% (Lv5解锁)",
            "武将防御+0% (Lv7解锁)",
            "武将生命+0% (Lv10解锁)",
            "武将攻击+0% (Lv15解锁)",
            "全体防御+0% (Lv20解锁)",
            "全体生命+0% (Lv25解锁)",
            "全体攻击+0% (Lv30解锁)",
        ]

        tech_vars = []
        for i, name in enumerate(tech_names):
            var = tk.IntVar(value=1 if i < 2 else 0)
            cb = tk.Checkbutton(scrollable_frame, text=name, variable=var,
                               anchor='w', font=("微软雅黑", 10))
            cb.pack(fill='x', padx=25, pady=3)
            tech_vars.append(var)

        tk.Frame(scrollable_frame, height=2, bg='gray').pack(fill='x', pady=10)

        # 捐献次数设置
        tk.Label(scrollable_frame, text="每次捐献次数", font=("微软雅黑", 11, "bold")).pack(pady=5)

        gold_var = tk.IntVar(value=10)
        diamond_var = tk.IntVar(value=10)
        red_var = tk.IntVar(value=0)
        soul_var = tk.IntVar(value=15)

        def create_row(parent, label_text, var):
            frame = tk.Frame(parent)
            frame.pack(pady=4, fill='x', padx=25)
            tk.Label(frame, text=label_text, width=10, anchor='w', font=("微软雅黑", 10)).pack(side='left')
            tk.Spinbox(frame, from_=0, to=99, width=10, font=("微软雅黑", 10), textvariable=var).pack(side='right')

        create_row(scrollable_frame, "💰 金币:", gold_var)
        create_row(scrollable_frame, "💎 钻石:", diamond_var)
        create_row(scrollable_frame, "🔴 红钻:", red_var)
        create_row(scrollable_frame, "💀 将魂:", soul_var)

        btn_frame = tk.Frame(scrollable_frame)
        btn_frame.pack(pady=15)

        def on_confirm():
            selected = [i+1 for i, var in enumerate(tech_vars) if var.get() == 1]
            if not selected:
                messagebox.showwarning("提示", "请至少选择一个科技！")
                return
            counts = {
                "金币": gold_var.get(),
                "钻石": diamond_var.get(),
                "红钻": red_var.get(),
                "将魂": soul_var.get()
            }
            dialog.destroy()
            self.set_status("正在执行科技大厅捐献任务...", "orange")
            threading.Thread(
                target=self._run_tech_task,
                args=(selected, counts),
                daemon=True
            ).start()

        def on_cancel():
            dialog.destroy()
            self.set_status("已取消", "gray")

        tk.Button(btn_frame, text="✅ 确认", command=on_confirm, width=10, bg="#4CAF50", fg="white").pack(side='left', padx=10)
        tk.Button(btn_frame, text="❌ 取消", command=on_cancel, width=10, bg="#f44336", fg="white").pack(side='left', padx=10)

        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 居中
        dialog.update()
        x = (dialog.winfo_screenwidth() - 480) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f"+{x}+{y}")

    def _run_tech_task(self, selected_techs, counts):
        engine = {'clicker': Clicker({})}
        task = TechDonateTask(engine, {'selected_techs': selected_techs, 'counts': counts})
        result = task.execute()
        self.root.after(0, lambda: self._show_task_result(result))

    # ==================== 通用结果展示 ====================
    def _show_task_result(self, result):
        messagebox.showinfo("任务结果", result)
        self.set_status("就绪", "gray")

    # ==================== 预留任务（未来扩展） ====================
    def start_future(self):
        self.set_status("此任务开发中...", "orange")
        messagebox.showinfo("提示", "此任务尚未实现，敬请期待！")
        self.set_status("就绪", "gray")

    def start_collect(self):
        self.start_future()

    def start_daily(self):
        self.start_future()