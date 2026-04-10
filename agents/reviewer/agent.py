"""
审阅代理（Reviewer Agent）
负责综合审阅结果并做出决策
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
    prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'reviewer.txt'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_reviewer_agent(model: LiteLlm = None) -> LlmAgent:
    """
    创建审阅代理
    
    Args:
        model: LiteLlm 模型实例
    
    Returns:
        LlmAgent: 配置好的 reviewer 代理
    """
    if model is None:
        model = LiteLlm(**settings.get_model_config())
    
    return LlmAgent(
        name="Reviewer",
        model=model,
        instruction=load_prompt(),
        output_key="reviewer_decision_raw",
        include_contents='none',  # 不接收上下文历史，避免干扰
    )
