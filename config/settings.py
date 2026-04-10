"""
应用程序配置管理
从环境变量加载配置信息
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Settings:
    """应用程序配置类"""
    
    # API 配置
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai/qwen3.5-plus")
    
    # 文件路径配置
    QUESTION_FILE: str = os.getenv("QUESTION_FILE", "d:/ADK/question.md")
    LOG_DIR: str = os.getenv("LOG_DIR", "d:/ADK/phyagent/logs")
    
    # Wolfram 配置
    WOLFRAMSCRIPT_PATH: str = os.getenv("WOLFRAMSCRIPT_PATH", "wolframscript")
    WOLFRAM_TIMEOUT: int = int(os.getenv("WOLFRAM_TIMEOUT", "30"))
    
    # 工作流程配置
    MAX_PLAN_ATTEMPTS: int = int(os.getenv("MAX_PLAN_ATTEMPTS", "2"))
    MAX_REVISION_ATTEMPTS: int = int(os.getenv("MAX_REVISION_ATTEMPTS", "3"))
    HIGH_TEMPERATURE: float = float(os.getenv("HIGH_TEMPERATURE", "0.8"))
    
    # 应用配置
    APP_NAME: str = "physics_app"
    USER_ID: str = "12345"
    SESSION_ID: str = "123344"
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
        if not cls.QUESTION_FILE:
            raise ValueError("QUESTION_FILE 环境变量未设置")
        return True
    
    @classmethod
    def get_model_config(cls) -> dict:
        """获取模型配置字典"""
        return {
            "model": cls.DEFAULT_MODEL,
            "api_base": cls.API_BASE_URL,
            "api_key": cls.DASHSCOPE_API_KEY
        }


# 创建全局配置实例
settings = Settings()
