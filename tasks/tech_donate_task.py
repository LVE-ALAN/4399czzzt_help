import time
from collections import Counter
from .base_task import BaseTask

class TechDonateTask(BaseTask):
    def __init__(self, engine, config=None):
        super().__init__("科技大厅捐献", engine)
        self.config = config or {}
        self.default_counts = {"金币": 10, "钻石": 10, "红钻": 0, "将魂": 15}
        self.clicker = engine['clicker']
        self.selected_techs = self.config.get('selected_techs', [2])

    def execute(self):
        counts = self.config.get('counts', self.default_counts)
        templates = "templates/buttons/"
        clicker = self.clicker

        # 1. 从主界面点击联盟图标
        if not clicker.click_template(templates + "联盟图标.png", wait_after=1.5):
            return "❌ 未找到联盟图标"

        # 2. 点击科技大厅
        if not clicker.click_template(templates + "科技大厅.png", wait_after=1.5):
            return "❌ 未找到科技大厅按钮"

        # 3. 找到所有"捐献"按钮（科技行的）
        positions = clicker.find_templates_sorted(templates + "捐献按钮.png", confidence=0.6, max_results=12)
        if len(positions) < 1:
            return "❌ 未找到任何捐献按钮"

        # 过滤出科技行的捐献按钮（排除升级按钮）
        x_values = [p[0] for p in positions]
        counter = Counter(x_values)
        most_common_x = counter.most_common(1)[0][0]
        tech_buttons = [p for p in positions if abs(p[0] - most_common_x) < 20]
        tech_buttons.sort(key=lambda p: p[1])
        tech_buttons = tech_buttons[:9]

        if len(tech_buttons) < 1:
            return "❌ 过滤后无有效科技捐献按钮"

        print(f"✅ 找到 {len(tech_buttons)} 个科技捐献按钮")

        # 4. 遍历用户选中的科技
        for idx in self.selected_techs:
            if idx > len(tech_buttons):
                continue

            x, y, w, h = tech_buttons[idx - 1]
            center_x = x + w // 2
            center_y = y + h // 2

            # 点击该科技的捐献按钮
            clicker.click_coord(center_x, center_y, wait_after=1.0)  # 缩短为1秒

            # 等待捐献界面出现（捐献按钮重新出现）
            if not clicker.wait_for_template(templates + "捐献按钮.png", timeout=5):
                return f"❌ 进入科技 {idx} 的捐献界面超时"

            # 执行四种捐献
            result = self._do_donations(counts, templates, clicker)
            if result is not None:
                return result

            # 关闭捐献界面（第一次）
            if not clicker.click_template(templates + "关闭.png", wait_after=1.0):
                print("⚠️ 未找到关闭按钮，尝试返回")

            # 退出科技大厅子界面（第二次）
            if not clicker.click_template(templates + "关闭.png", wait_after=1.0):
                print("⚠️ 未找到关闭按钮，尝试返回")

            time.sleep(0.3)

        # 5. 点击右上角叉叉退出科技大厅主界面
        clicker.click_template(templates + "关闭.png", wait_after=1.0)

        # 6. 点击右下角回城
        clicker.click_template(templates + "回城.png", wait_after=1.5)

        return "✅ 科技大厅捐献任务完成"

    def _do_donations(self, counts, templates, clicker):
        """执行四种捐献（金币、钻石、红钻、将魂）"""
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
                clicker.click_coord(center_x, center_y, wait_after=0.2)  # 每次点击仅等待0.2秒
                time.sleep(0.1)

        return None