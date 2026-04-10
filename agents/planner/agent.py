"""
规划代理（Planner Agent）
负责生成多个具有优先级的解题思路
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

try:
    from ...config.settings import settings
except ImportError:
    from config.settings import settings


def load_prompt() -> str:
    """加载提示词"""
    from pathlib import Path
    prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'planner.txt'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_planner_agent(model: LiteLlm = None) -> LlmAgent:
    """
    创建规划代理
    
    Args:
        model: LiteLlm 模型实例
    
    Returns:
        LlmAgent: 配置好的 planner 代理
    """
    if model is None:
        model = LiteLlm(**settings.get_model_config())
    
    return LlmAgent(
        name="planner",
        model=model,
        instruction=load_prompt(),
        output_key="plans",
        include_contents='none',  # 不接收上下文历史，避免干扰
    )
