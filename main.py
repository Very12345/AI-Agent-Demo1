"""
物理问题自动解答系统 - 主程序入口
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 设置控制台和进程编码为 UTF-8
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 > nul')

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

try:
    from .config.settings import settings
    from .agents import (
        create_describer_agent,
        create_planner_agent,
        create_solver_agent,
        create_physics_verifier_agent,
        create_general_verifier_agent,
        create_reviewer_agent,
        PhysicsFlowAgent
    )
except ImportError:
    from config.settings import settings
    from agents import (
        create_describer_agent,
        create_planner_agent,
        create_solver_agent,
        create_physics_verifier_agent,
        create_general_verifier_agent,
        create_reviewer_agent,
        PhysicsFlowAgent
    )


def print_banner():
    """打印欢迎信息"""
    print("=" * 60)
    print("物理问题自动解答系统")
    print("=" * 60)


def load_question() -> str:
    """从文件加载问题"""
    try:
        with open(settings.QUESTION_FILE, 'r', encoding='utf-8') as f:
            problem = f.read().strip()
        print(f"info 从 {settings.QUESTION_FILE} 读取问题成功")
        return problem
    except FileNotFoundError:
        print(f"error 问题文件未找到：{settings.QUESTION_FILE}")
        return "一个质量为 2kg 的物体以 10m/s 的初速度水平抛出，求 2 秒后的速度和位置。"
    except Exception as e:
        print(f"error 读取问题文件失败：{e}")
        return "一个质量为 2kg 的物体以 10m/s 的初速度水平抛出，求 2 秒后的速度和位置。"


def create_physics_flow_agent() -> PhysicsFlowAgent:
    """创建物理工作流代理"""
    from google.adk.models.lite_llm import LiteLlm
    
    # 创建模型实例
    model = LiteLlm(**settings.get_model_config())
    
    # 创建各个子 agent
    describer = create_describer_agent(model)
    planner = create_planner_agent(model)
    solver = create_solver_agent(model)
    physics_verifier = create_physics_verifier_agent(model)
    general_verifier = create_general_verifier_agent(model)
    reviewer = create_reviewer_agent(model)
    
    # 创建工作流代理
    physics_flow_agent = PhysicsFlowAgent(
        name="PhysicsFlowAgent",
        describer=describer,
        planner=planner,
        solver=solver,
        physics_verifier=physics_verifier,
        general_verifier=general_verifier,
        reviewer=reviewer,
    )
    
    return physics_flow_agent


async def setup_session_and_runner(agent: PhysicsFlowAgent, problem: str):
    """
    设置会话服务和运行器
    
    Args:
        agent: PhysicsFlowAgent 实例
        problem: 物理问题文本
    
    Returns:
        tuple: (session_service, runner)
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=settings.APP_NAME,
        user_id=settings.USER_ID,
        session_id=settings.SESSION_ID,
        state={"initial_problem": problem},
    )
    print(f"info 初始会话状态：{session.state}")
    
    runner = Runner(
        agent=agent,
        app_name=settings.APP_NAME,
        session_service=session_service,
    )
    return session_service, runner


async def run_agent(problem: str):
    """
    运行代理解答物理问题
    
    Args:
        problem: 物理问题文本
    """
    print_banner()
    print(f"问题：{problem}")
    print("=" * 60)
    
    # 验证配置
    settings.validate()
    
    # 创建代理
    print("info 创建物理工作流代理...")
    physics_flow_agent = create_physics_flow_agent()
    
    # 设置会话和运行器
    print("info 设置会话服务...")
    session_service, runner = await setup_session_and_runner(physics_flow_agent, problem)
    
    # 运行代理
    print("info 开始运行物理问题解答流程...")
    content = types.Content(
        role='user',
        parts=[types.Part(text="解答这个物理问题。")]
    )
    
    events = runner.run_async(
        user_id=settings.USER_ID,
        session_id=settings.SESSION_ID,
        new_message=content
    )
    
    final_response = "未捕获到最终响应。"
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            print(f"info 来自 [{event.author}] 的潜在最终响应：{event.content.parts[0].text[:100]}...")
            final_response = event.content.parts[0].text
    
    # 输出结果
    print("\n" + "=" * 60)
    print("代理交互结果")
    print("=" * 60)
    print(f"代理最终响应：{final_response}")
    
    # 获取最终会话状态
    final_session = await session_service.get_session(
        app_name=settings.APP_NAME,
        user_id=settings.USER_ID,
        session_id=settings.SESSION_ID
    )
    print("\n最终会话状态:")
    print(json.dumps(final_session.state, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    return final_response


async def main():
    """主函数"""
    # 加载问题
    problem = load_question()
    
    # 运行代理
    await run_agent(problem)


if __name__ == "__main__":
    print(f"当前模块名称：{__name__}")
    print(f"是否为主模块：{__name__ == '__main__'}")
    asyncio.run(main())
