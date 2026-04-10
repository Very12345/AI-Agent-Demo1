"""
日志工具模块
提供工作流日志记录功能
"""

import os
import json
from datetime import datetime
from typing import Any


class WorkflowLogger:
    """工作流日志记录器，保存所有关键中间步骤"""
    
    _instance = None
    
    def __new__(cls, output_dir: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, output_dir: str = None):
        if self._initialized:
            return
        
        if output_dir is None:
            try:
                from ..config.settings import settings
            except ImportError:
                from config.settings import settings
            output_dir = settings.LOG_DIR
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(output_dir, f"workflow_{self.timestamp}.txt")
        self.json_file = os.path.join(output_dir, f"workflow_{self.timestamp}.json")
        self.data = {}
        self._initialized = True
        
    def log_step(self, step_name: str, content: str, data: Any = None):
        """记录步骤到文本文件"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{step_name}]\n")
            f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            f.write(content)
            f.write(f"\n")
        
        if data is not None:
            self.data[step_name] = data
    
    def save_json(self):
        """保存所有数据到 JSON 文件"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def finalize(self, success: bool, final_solution: str = None):
        """完成日志记录"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[工作流程完成]\n")
            f.write(f"状态：{'成功' if success else '失败'}\n")
            f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            if final_solution:
                f.write(f"\n[最终解答]\n{final_solution}\n")
        
        self.data['success'] = success
        self.data['final_solution'] = final_solution
        self.save_json()
        
        print(f"info 工作流日志已保存到：{self.log_file}")
        print(f"info 工作流 JSON 数据已保存到：{self.json_file}")
