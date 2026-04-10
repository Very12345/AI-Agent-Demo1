"""
Agents 模块
包含所有子 agent 组件
"""

try:
    # 尝试相对导入（作为包使用时）
    from .describer.agent import create_describer_agent
    from .planner.agent import create_planner_agent
    from .solver.agent import create_solver_agent
    from .verifier.physics_verifier import create_physics_verifier_agent
    from .verifier.general_verifier import create_general_verifier_agent
    from .reviewer.agent import create_reviewer_agent
    from .base_agent import PhysicsFlowAgent
except ImportError:
    # 回退到绝对导入（直接运行时）
    from describer.agent import create_describer_agent
    from planner.agent import create_planner_agent
    from solver.agent import create_solver_agent
    from verifier.physics_verifier import create_physics_verifier_agent
    from verifier.general_verifier import create_general_verifier_agent
    from reviewer.agent import create_reviewer_agent
    from base_agent import PhysicsFlowAgent

__all__ = [
    'create_describer_agent',
    'create_planner_agent',
    'create_solver_agent',
    'create_physics_verifier_agent',
    'create_general_verifier_agent',
    'create_reviewer_agent',
    'PhysicsFlowAgent'
]
