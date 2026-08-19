import json
import os

def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        # 返回默认配置
        return {
            "vision": {"template_match_threshold": 0.7},
            "tasks": {"retry_count": 3, "wait_timeout": 10}
        }
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)