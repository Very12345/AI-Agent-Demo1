"""
基础 Agent 模块
定义工作流 Agent 的基础结构
"""

import asyncio
import json
import os
import sys
from typing import AsyncGenerator, Dict, Any
from typing_extensions import override

# 设置编码
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

try:
    from ..utils.logger import WorkflowLogger
except ImportError:
    from utils.logger import WorkflowLogger


class logging:
    def info(self, msg: str):
        sys.stdout.write("info " + msg + "\n")
        sys.stdout.flush()
    def warning(self, msg: str):
        sys.stdout.write("warning " + msg + "\n")
        sys.stdout.flush()
    def error(self, msg: str):
        sys.stdout.write("error " + msg + "\n")
        sys.stdout.flush()
logger = logging()


class PhysicsFlowAgent(BaseAgent):
    """
    用于物理问题处理的代理。
    工作流程：
    1. describer: 生成规范化的题目描述
    2. planner: 生成多个具有优先级的解题思路
    3. solver: 按照解题思路解题
    4. physics_verifier: 验证物理方面（公式、原理、量纲）
    5. general_verifier: 验证数学运算和逻辑连贯性
    6. reviewer: 根据审阅结果决定流程走向
    """

    # 定义子 agent 字段
    describer: LlmAgent
    planner: LlmAgent
    solver: LlmAgent
    physics_verifier: LlmAgent
    general_verifier: LlmAgent
    reviewer: LlmAgent

    # 允许任意类型的 Pydantic 模型和额外属性
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(
        self,
        name: str,
        describer: LlmAgent,
        planner: LlmAgent,
        solver: LlmAgent,
        physics_verifier: LlmAgent,
        general_verifier: LlmAgent,
        reviewer: LlmAgent,
    ):
        sub_agents_list = [
            describer,
            planner,
            solver,
            physics_verifier,
            general_verifier,
            reviewer,
        ]
        super().__init__(
            name=name,
            sub_agents=sub_agents_list,
            describer=describer,
            planner=planner,
            solver=solver,
            physics_verifier=physics_verifier,
            general_verifier=general_verifier,
            reviewer=reviewer,
        )
        # 使用 object.__setattr__ 避免 Pydantic 验证
        object.__setattr__(self, 'logger_instance', WorkflowLogger())

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        实现物理问题解决工作流程的自定义编排逻辑。
        """
        try:
            from ..config.settings import settings
        except ImportError:
            from config.settings import settings
        
        logger.info(f"[{self.name}] 开始物理问题解决工作流程。")
        
        # 初始化日志记录器
        workflow_logger = self.logger_instance
        workflow_logger.data['initial_problem'] = ctx.session.state.get('initial_problem', '')
        workflow_logger.log_step("初始问题", ctx.session.state.get('initial_problem', ''))

        # 1. 问题分析阶段 - describer
        logger.info(f"[{self.name}] 开始问题分析...")
        async for event in self.describer.run_async(ctx):
            yield event

        if "problem" not in ctx.session.state or not ctx.session.state["problem"]:
            logger.error(f"[{self.name}] 未能生成题目描述。中止工作流程。")
            workflow_logger.finalize(False)
            return

        problem_desc = ctx.session.state["problem"]
        workflow_logger.log_step("题目描述（规范化）", problem_desc, {'problem': problem_desc})
        logger.info(f"[{self.name}] 问题分析完成")

        # 2. 解题规划阶段 - planner
        logger.info(f"[{self.name}] 开始解题规划...")
        async for event in self.planner.run_async(ctx):
            yield event

        if "plans" not in ctx.session.state or not ctx.session.state["plans"]:
            logger.error(f"[{self.name}] 未能生成解题规划。中止工作流程。")
            workflow_logger.finalize(False)
            return

        plans_raw = ctx.session.state["plans"]
        
        # 解析 plans，确保是列表格式
        if isinstance(plans_raw, str):
            try:
                plans = json.loads(plans_raw)
            except json.JSONDecodeError as e:
                logger.error(f"解析 plans JSON 失败：{e}")
                # 尝试清理和修复 JSON
                try:
                    # 移除可能的 Markdown 标记
                    cleaned = plans_raw.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    plans = json.loads(cleaned)
                    logger.info(f"清理后成功解析 plans")
                except:
                    logger.warning(f"清理后仍无法解析，使用原始值作为单个 plan")
                    plans = [plans_raw]
        elif isinstance(plans_raw, list):
            plans = plans_raw
        else:
            plans = [plans_raw]
        
        num_plans = len(plans) if isinstance(plans, list) else 1
        
        # 保存规划到日志
        plans_json = json.dumps(plans, ensure_ascii=False, indent=2) if isinstance(plans, list) else str(plans)
        workflow_logger.log_step("解题思路规划", plans_json, {'plans': plans})
        
        logger.info(f"[{self.name}] 生成 {num_plans} 个解题思路")

        # 3. 解题与验证循环
        max_plan_attempts = settings.MAX_PLAN_ATTEMPTS
        max_revision_attempts = settings.MAX_REVISION_ATTEMPTS
        
        current_plan_index = 0
        plan_attempts = 0
        revision_attempts = 0
        success = False
        previous_solutions = []
        use_high_temperature = False

        while plan_attempts < max_plan_attempts and not success:
            ctx.session.state["current_plan_index"] = current_plan_index
            ctx.session.state["previous_solutions"] = previous_solutions if previous_solutions else "无"
            logger.info(f"[{self.name}] 使用第 {current_plan_index + 1} 个解题思路")
            
            # 如果所有 plan 都失败了，提高 temperature 重试
            if plan_attempts > 0 and current_plan_index == 0 and not use_high_temperature:
                use_high_temperature = True
                logger.info(f"[{self.name}] 所有解题思路均已尝试失败，提升 temperature 重试...")
                
                # 动态修改 solver 和 verifier 的 temperature
                from google.genai import types
                high_temp_config = types.GenerateContentConfig(
                    temperature=settings.HIGH_TEMPERATURE,
                    top_p=0.95,
                )
                self.solver.generate_content_config = high_temp_config
                self.physics_verifier.generate_content_config = high_temp_config
                self.general_verifier.generate_content_config = high_temp_config
                self.reviewer.generate_content_config = high_temp_config
                
                logger.info(f"[{self.name}] Temperature 已提升至 {settings.HIGH_TEMPERATURE}")
            
            revision_attempts = 0
            
            while revision_attempts < max_revision_attempts and not success:
                ctx.session.state["revision_attempts"] = revision_attempts
                
                # 3.1 解题阶段 - solver
                logger.info(f"[{self.name}] 开始解题 (第 {revision_attempts + 1} 次尝试)...")
                async for event in self.solver.run_async(ctx):
                    yield event

                # 保存当前解答到历史记录
                if "solution" in ctx.session.state and ctx.session.state["solution"]:
                    previous_solutions.append({
                        "attempt": revision_attempts + 1,
                        "plan_index": current_plan_index,
                        "solution": ctx.session.state["solution"]
                    })
                    ctx.session.state["previous_solutions"] = previous_solutions
                    
                    # 保存解题步骤到日志
                    solution_content = f"使用思路索引：{current_plan_index}\n尝试次数：{revision_attempts + 1}\n\n{ctx.session.state['solution']}"
                    workflow_logger.log_step(f"解答 (第{current_plan_index+1}个思路，第{revision_attempts+1}次尝试)", 
                                           solution_content, 
                                           {'solution_attempt': revision_attempts + 1, 'solution': ctx.session.state["solution"]})

                if "solution" not in ctx.session.state or not ctx.session.state["solution"]:
                    logger.error(f"[{self.name}] 解题失败，尝试下一个思路")
                    break

                # 3.2 物理验证 - physics_verifier
                logger.info(f"[{self.name}] 开始物理验证...")
                async for event in self.physics_verifier.run_async(ctx):
                    yield event

                # 保存物理验证结果
                physics_verification = ctx.session.state.get("physics_verification", "")
                workflow_logger.log_step(f"物理验证结果 (第{revision_attempts+1}次尝试)", 
                                       physics_verification,
                                       {'physics_verification': physics_verification})

                # 3.3 通用验证 - general_verifier
                logger.info(f"[{self.name}] 开始通用验证...")
                async for event in self.general_verifier.run_async(ctx):
                    yield event

                # 保存通用验证结果
                general_verification = ctx.session.state.get("general_verification", "")
                workflow_logger.log_step(f"通用验证结果 (第{revision_attempts+1}次尝试)", 
                                       general_verification,
                                       {'general_verification': general_verification})

                # 3.4 审阅决策 - reviewer
                logger.info(f"[{self.name}] 开始审阅决策...")
                async for event in self.reviewer.run_async(ctx):
                    yield event

                # 3.5 根据 reviewer 决策执行
                # 解析 reviewer 的 JSON 输出
                reviewer_output = ctx.session.state.get("reviewer_decision_raw", "{}")
                try:
                    # 清理 reviewer 输出，提取 JSON 部分
                    reviewer_text = reviewer_output
                    if isinstance(reviewer_text, str):
                        # 清理 Markdown 代码块标记
                        if reviewer_text.startswith("```json"):
                            reviewer_text = reviewer_text[7:]
                        if reviewer_text.endswith("```"):
                            reviewer_text = reviewer_text[:-3]
                        reviewer_text = reviewer_text.strip()
                        reviewer_data = json.loads(reviewer_text)
                    else:
                        reviewer_data = reviewer_output
                    decision = reviewer_data.get("decision", "").lower()
                    logger.info(f"[{self.name}] 审阅决策：{decision}")
                    logger.info(f"[{self.name}] 决策原因：{reviewer_data.get('reason', 'N/A')}")
                    
                    # 保存审阅决策到日志
                    workflow_logger.log_step(f"审阅决策 (第{revision_attempts+1}次尝试)", 
                                           f"决策：{decision}\n原因：{reviewer_data.get('reason', 'N/A')}\n建议：{reviewer_data.get('suggestions', [])}",
                                           {'decision': decision, 'reason': reviewer_data.get('reason'), 'suggestions': reviewer_data.get('suggestions')})
                except (json.JSONDecodeError, AttributeError, TypeError) as e:
                    logger.error(f"[{self.name}] 解析 reviewer 输出失败：{e}")
                    logger.warning(f"[{self.name}] 原始输出：{reviewer_output[:200]}")
                    decision = "revise"  # 解析失败时默认修订
                    
                    # 记录解析失败的审阅决策到日志
                    workflow_logger.log_step(f"审阅决策 (第{revision_attempts+1}次尝试)", 
                                           f"决策：{decision}\n原因：解析审阅者输出失败，默认修订\n建议：[]",
                                           {'decision': decision, 'reason': '解析失败', 'suggestions': []})

                if decision == "success":
                    logger.info(f"[{self.name}] 解答通过验证，工作流程完成。")
                    success = True
                    final_solution = ctx.session.state.get("solution", "")
                    
                    if use_high_temperature:
                        workflow_logger.data['temperature_mode'] = 'high'
                        logger.info(f"[{self.name}] 本次成功解答使用了高 temperature 模式")
                    else:
                        workflow_logger.data['temperature_mode'] = 'default'
                    
                    workflow_logger.finalize(True, final_solution)
                    break
                elif decision == "switch_plan":
                    logger.info(f"[{self.name}] 思路完全错误，切换到下一个解题思路")
                    plan_attempts += 1
                    current_plan_index += 1
                    previous_solutions = []
                    if current_plan_index >= num_plans:
                        logger.error(f"[{self.name}] 已尝试所有解题思路，均失败")
                        workflow_logger.finalize(False)
                        return
                    break
                elif decision == "revise":
                    logger.info(f"[{self.name}] 存在非致命问题，尝试修订")
                    revision_attempts += 1
                    if revision_attempts >= max_revision_attempts:
                        logger.warning(f"[{self.name}] 已达到最大修订次数，切换到下一个思路")
                        plan_attempts += 1
                        current_plan_index += 1
                        if current_plan_index >= num_plans:
                            logger.error(f"[{self.name}] 已尝试所有解题思路，均失败")
                            workflow_logger.finalize(False)
                            return
                        break
                else:
                    logger.warning(f"[{self.name}] 未知的决策：{decision}，继续修订")
                    revision_attempts += 1

            if success:
                break

        if not success:
            logger.error(f"[{self.name}] 未能生成有效解答，工作流程失败。")
            
            workflow_logger.data['temperature_mode'] = 'high' if use_high_temperature else 'default'
            workflow_logger.data['failure_reason'] = f'已尝试 {plan_attempts} 个 plan，每个 plan 最多 {max_revision_attempts} 次修订'
            
            workflow_logger.finalize(False)
            return

        logger.info(f"[{self.name}] 物理问题解决工作流程完成。")
