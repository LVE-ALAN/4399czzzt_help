import time
from .base_task import BaseTask

class UnionContributeTask(BaseTask):
    def __init__(self, engine, config=None):
        super().__init__("联盟大厅捐献", engine)
        self.config = config or {}
        self.default_counts = {"金币": 10, "钻石": 0, "红钻": 0, "将魂": 10}
        self.clicker = engine['clicker']

    def execute(self):
        counts = self.config.get('counts', self.default_counts)
        templates = "templates/buttons/"
        clicker = self.clicker

        # 1. 点击联盟图标
        if not clicker.click_template(templates + "联盟图标.png", wait_after=1.5):
            return "❌ 未找到联盟图标"

        # 2. 点击联盟大厅
        if not clicker.click_template(templates + "联盟大厅.png", wait_after=1.5):
            return "❌ 未找到联盟大厅"

        # 3. 点击联盟捐献
        if not clicker.click_template(templates + "联盟捐献.png", wait_after=1.5):
            return "❌ 未找到联盟捐献按钮"

        # 等待捐献界面出现
        if not clicker.wait_for_template(templates + "捐献按钮.png", timeout=5):
            return "❌ 进入联盟捐献界面超时"

        # 4. 执行四种捐献
        result = self._do_donations(counts, templates, clicker)
        if result is not None:
            return result

        # 5. 关闭捐献界面（回到联盟大厅）
        if not clicker.click_template(templates + "关闭.png", wait_after=1.0):
            print("⚠️ 未找到关闭按钮，可能已自动返回")

        # 6. 关闭联盟大厅（回到主界面）
        if not clicker.click_template(templates + "关闭.png", wait_after=1.0):
            print("⚠️ 未找到关闭按钮，可能已自动返回")

        # 7. 点击右下角回城
        if not clicker.click_template(templates + "回城.png", wait_after=1.5):
            print("⚠️ 未找到回城按钮，任务可能仍在联盟界面")

        return "✅ 联盟大厅捐献任务完成"

    def _do_donations(self, counts, templates, clicker):
        positions = clicker.find_templates_sorted(templates + "捐献按钮.png", confidence=0.6, max_results=6)

        if len(positions) < 4:
            return f"❌ 只找到 {len(positions)} 个捐献按钮，预期至少 4 个"

        button_map = {
            "金币": positions[0],
            "钻石": positions[1],
            "红钻": positions[2],
            "将魂": positions[3],
        }

        for donate_type, count in counts.items():
            if count <= 0:
                continue
            if donate_type not in button_map:
                continue
            x, y, w, h = button_map[donate_type]
            center_x = x + w // 2
            center_y = y + h // 2
            for i in range(count):
                clicker.click_coord(center_x, center_y, wait_after=0.2)
                time.sleep(0.1)

        return None