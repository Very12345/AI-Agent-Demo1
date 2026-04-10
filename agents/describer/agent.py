"""
问题描述代理（Describer Agent）
负责生成规范化的物理题目描述
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
    prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'describer.txt'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_describer_agent(model: LiteLlm = None) -> LlmAgent:
    """
    创建问题描述代理
    
    Args:
        model: LiteLlm 模型实例，如果为 None 则使用默认配置
    
    Returns:
        LlmAgent: 配置好的 describer 代理
    """
    if model is None:
        model = LiteLlm(**settings.get_model_config())
    
    return LlmAgent(
        name="describer",
        model=model,
        instruction=load_prompt(),
        output_key="problem",
        include_contents='none',  # 不接收上下文历史，避免干扰
    )
