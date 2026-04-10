"""
物理验证器（Physics Verifier）
负责验证物理解答的正确性（公式、原理、量纲）
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
    prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'physics_verifier.txt'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_physics_verifier_agent(model: LiteLlm = None) -> LlmAgent:
    """
    创建物理验证器
    
    Args:
        model: LiteLlm 模型实例
    
    Returns:
        LlmAgent: 配置好的 physics verifier 代理
    """
    if model is None:
        model = LiteLlm(**settings.get_model_config())
    
    return LlmAgent(
        name="PhysicsVerifier",
        model=model,
        instruction=load_prompt(),
        output_key="physics_verification",
        include_contents='none',  # 不接收上下文历史，避免干扰
    )
