"""
解题代理（Solver Agent）
负责按照选定的解题思路进行解答
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

try:
    from ...config.settings import settings
    from ...tools.wolfram_tools import wolfram_calculate
except ImportError:
    from config.settings import settings
    from tools.wolfram_tools import wolfram_calculate


def load_prompt() -> str:
    """加载提示词"""
    from pathlib import Path
    prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'solver.txt'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_solver_agent(model: LiteLlm = None) -> LlmAgent:
    """
    创建解题代理
    
    Args:
        model: LiteLlm 模型实例
    
    Returns:
        LlmAgent: 配置好的 solver 代理
    """
    if model is None:
        model = LiteLlm(**settings.get_model_config())
    
    return LlmAgent(
        name="solver",
        model=model,
        instruction=load_prompt(),
        output_key="solution",
        tools=[wolfram_calculate],
        include_contents='none',  # 不接收上下文历史，避免干扰
    )
