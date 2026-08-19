# 预留状态机（后续扩展）
class StateMachine:
    def __init__(self, vision, config):
        self.vision = vision
        self.config = config
        self.current_state = "unknown"

    def recognize_state(self, screenshot_gray):
        # 用模板匹配识别界面状态
        # 目前只返回'unknown'
        return "unknown"