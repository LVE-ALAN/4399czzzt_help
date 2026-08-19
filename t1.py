import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.clicker import Clicker
from tasks.tech_donate_task import TechDonateTask

def check_template(template_path):
    """检查模板文件是否存在"""
    if not os.path.exists(template_path):
        print(f"⚠️ 模板文件不存在: {template_path}")
        return False
    return True

def main():
    print("=" * 60)
    print("🧪 科技大厅捐献模块测试")
    print("=" * 60)
    print("请确保：")
    print("1. 游戏已打开，并且当前在主界面")
    print("2. 游戏窗口未被遮挡，且未最小化")
    print("3. 所有模板图片已放入 templates/buttons/ 目录")
    print("=" * 60)

    # 检查必需的模板文件
    templates = [
        "templates/buttons/联盟图标.png",
        "templates/buttons/科技大厅.png",
        "templates/buttons/捐献按钮.png",
        "templates/buttons/关闭.png",
        "templates/buttons/回城.png",
    ]

    missing = []
    for tpl in templates:
        if not check_template(tpl):
            missing.append(tpl)

    if missing:
        print(f"\n❌ 缺少 {len(missing)} 个模板文件，请补充后再运行")
        for m in missing:
            print(f"   - {m}")
        return

    print("\n✅ 所有模板文件已就绪")

    confirm = input("\n⚠️ 测试将模拟鼠标点击，请确保游戏窗口可见！\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("测试取消")
        return

    # ====== 配置测试参数 ======
    # 科技索引对应：1=士兵防御+4%, 2=士兵生命+1%, 3=士兵攻击+0% ...
    # 只勾选前2个可捐献的（默认）
    selected_techs = [2]

    # 四种捐献的次数
    counts = {"金币": 1, "钻石": 0, "红钻": 0, "将魂": 0}

    print(f"\n📋 测试配置：")
    print(f"   - 捐献科技索引: {selected_techs}")
    print(f"   - 捐献次数: {counts}")
    print("\n🚀 开始执行任务...")

    engine = {'clicker': Clicker({})}
    task = TechDonateTask(engine, {'selected_techs': selected_techs, 'counts': counts})

    result = task.execute()
    print(f"\n📌 任务结果: {result}")

if __name__ == "__main__":
    main()