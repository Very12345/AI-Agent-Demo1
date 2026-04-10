"""
通用验证器（General Verifier）
负责验证数学运算和逻辑连贯性
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

try:
    from ...config.settings import settings
    from ...tools.wolfram_tools import (
        wolfram_calculate,
        wolfram_verify_formula,
        wolfram_check_dimensions
    )
except ImportError:
    from config.settings import settings
    from tools.wolfram_tools import (
        wolfram_calculate,
        wolfram_verify_formula,
        wolfram_check_dimensions
    )


def load_prompt() -> str:
    """加载提示词"""
    from pathlib import Path
    prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'general_verifier.txt'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_general_verifier_agent(model: LiteLlm = None) -> LlmAgent:
    """
    创建通用验证器
    
    Args:
        model: LiteLlm 模型实例
    
    Returns:
        LlmAgent: 配置好的 general verifier 代理
    """
    if model is None:
        model = LiteLlm(**settings.get_model_config())
    
    return LlmAgent(
        name="GeneralVerifier",
        model=model,
        instruction=load_prompt(),
        output_key="general_verification",
        tools=[
            wolfram_calculate,
            wolfram_verify_formula,
            wolfram_check_dimensions
        ],
        include_contents='none',  # 不接收上下文历史，避免干扰
    )
