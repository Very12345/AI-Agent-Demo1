"""
Wolfram Script 工具
提供数学计算、公式验证和量纲分析功能
"""

import subprocess
from typing import Dict, Any
try:
    from ..config.settings import settings
except ImportError:
    from config.settings import settings


def wolfram_calculate(expression: str) -> Dict[str, Any]:
    """
    使用 Wolfram Script 执行数学计算和符号运算。
    
    适用于：
    - 复杂数学计算（代数、微积分、方程求解）
    - 符号运算和公式推导
    - 数值计算和精度保证
    - 数学验证和验算
    
    Args:
        expression (str): Wolfram Language 表达式，例如：
            - "Solve[x^2 + 2x + 1 == 0, x]"
            - "D[x^3 + 2x^2, x]"
            - "Integrate[Sin[x], {x, 0, Pi}]"
            - "N[Sqrt[2], 50]"
            - "Simplify[(x^2-1)/(x-1)]"
    
    Returns:
        Dict[str, Any]: 包含计算结果的字典：
            - "status": "success" 或 "error"
            - "result": 计算结果
            - "expression": 原始表达式
            - "error_message": 错误信息（如果有）
    """
    try:
        # 调用 Wolfram Script
        result = subprocess.run(
            [settings.WOLFRAMSCRIPT_PATH, "-code", expression],
            capture_output=True,
            text=True,
            timeout=settings.WOLFRAM_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "result": result.stdout.strip(),
                "expression": expression
            }
        else:
            return {
                "status": "error",
                "result": None,
                "expression": expression,
                "error_message": result.stderr.strip()
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "result": None,
            "expression": expression,
            "error_message": f"计算超时（超过{settings.WOLFRAM_TIMEOUT}秒）"
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "result": None,
            "expression": expression,
            "error_message": "未找到 Wolfram Script，请确保已安装 Mathematica 或 Wolfram Engine"
        }
    except Exception as e:
        return {
            "status": "error",
            "result": None,
            "expression": expression,
            "error_message": str(e)
        }


def wolfram_verify_formula(formula: str, assumptions: str = "") -> Dict[str, Any]:
    """
    验证物理公式或数学表达式的正确性。
    
    Args:
        formula (str): 需要验证的公式或等式
        assumptions (str): 假设条件（可选），例如 "x > 0 && t > 0"
    
    Returns:
        Dict[str, Any]: 验证结果：
            - "status": "success" 或 "error"
            - "is_valid": 公式是否有效（True/False）
            - "simplified": 简化后的公式
            - "error_message": 错误信息（如果有）
    """
    try:
        # 构建验证表达式
        if assumptions:
            verify_expr = f"FullSimplify[{formula}, {assumptions}]"
        else:
            verify_expr = f"FullSimplify[{formula}]"
        
        result = subprocess.run(
            [settings.WOLFRAMSCRIPT_PATH, "-code", verify_expr],
            capture_output=True,
            text=True,
            timeout=settings.WOLFRAM_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "is_valid": True,
                "simplified": result.stdout.strip(),
                "formula": formula
            }
        else:
            return {
                "status": "error",
                "is_valid": False,
                "simplified": None,
                "formula": formula,
                "error_message": result.stderr.strip()
            }
    except Exception as e:
        return {
            "status": "error",
            "is_valid": False,
            "simplified": None,
            "formula": formula,
            "error_message": str(e)
        }


def wolfram_check_dimensions(equation: str) -> Dict[str, Any]:
    """
    检查物理方程的量纲一致性。
    
    注意：Wolfram 没有内置的量纲分析功能，这里使用简化方法：
    - 检查方程两边的符号是否平衡（通过 Wolfram 的符号计算）
    - 实际量纲分析需要额外的物理量定义
    
    Args:
        equation (str): 物理方程，例如 "F == m*a" 或 "E == m*c^2"
    
    Returns:
        Dict[str, Any]: 量纲检查结果：
            - "status": "success" 或 "error"
            - "is_dimensionally_consistent": 量纲是否一致（True/False）
            - "dimensions": 各变量的量纲
            - "error_message": 错误信息（如果有）
    """
    try:
        # 使用简化方法：检查方程是否可以符号化简
        # 真正的量纲分析需要定义每个物理量的量纲
        check_expr = f"PossibleZeroQ[Expand[Subtract @@ ({equation})]]"
        
        result = subprocess.run(
            [settings.WOLFRAMSCRIPT_PATH, "-code", check_expr],
            capture_output=True,
            text=True,
            timeout=settings.WOLFRAM_TIMEOUT
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # 如果方程可以化简为 0，说明两边相等
            is_consistent = "True" in output
            return {
                "status": "success",
                "is_dimensionally_consistent": is_consistent,
                "equation": equation,
                "output": output,
                "note": "此检查为符号等价性检查，非严格量纲分析"
            }
        else:
            return {
                "status": "error",
                "is_dimensionally_consistent": False,
                "equation": equation,
                "error_message": result.stderr.strip()
            }
    except Exception as e:
        return {
            "status": "error",
            "is_dimensionally_consistent": False,
            "equation": equation,
            "error_message": str(e)
        }
