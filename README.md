# 物理问题自动解答系统（PhyAgent）

## 项目简介

PhyAgent 是一个基于多 agent 协作的物理问题自动解答系统。该系统采用模块化设计，将问题描述、解题规划、解答、验证和审阅等功能分离到不同的子 agent 中，通过清晰的工作流程实现物理问题的自动求解。

## 主要特性

- **模块化架构**：按功能职责拆分为多个独立的子 agent 组件
- **提示词分离**：所有提示词以文本文件形式独立管理
- **环境变量管理**：API 密钥等敏感信息通过环境变量配置
- **完整的工作流程**：
  1. 问题描述（Describer）
  2. 解题规划（Planner）
  3. 问题解答（Solver）
  4. 物理验证（Physics Verifier）
  5. 通用验证（General Verifier）
  6. 审阅决策（Reviewer）
- **Wolfram Script 集成**：支持精确的数学计算和公式验证
- **智能 Temperature 调节**：失败时自动提升模型创造性
- **完整的日志记录**：所有中间步骤自动保存到文本和 JSON 文件

## 快速开始

### 1. 安装依赖

```bash
pip install google-adk python-dotenv
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DASHSCOPE_API_KEY=sk-your-actual-api-key-here
DEFAULT_MODEL=openai/qwen3.5-plus
API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QUESTION_FILE=d:/ADK/question.md
LOG_DIR=d:/ADK/phyagent/logs
```

### 3. 准备问题文件

在 `question.md` 文件中写入物理问题：

```markdown
一个质量为 2kg 的物体以 10m/s 的初速度水平抛出，求 2 秒后的速度和位置。
```

### 4. 运行系统

```bash
cd phyagent
python main.py
```

## 目录结构

```
phyagent/
├── README.md                     # 项目说明文档
├── .env.example                  # 环境变量示例
├── .env                          # 实际环境变量配置（需手动创建）
├── main.py                       # 主程序入口
├── config/                       # 配置模块
│   ├── __init__.py
│   ├── settings.py              # 配置管理类
│   └── prompts/                 # 提示词文件夹
│       ├── describer.txt        # 问题描述代理提示词
│       ├── planner.txt          # 规划代理提示词
│       ├── solver.txt           # 解题代理提示词
│       ├── physics_verifier.txt # 物理验证器提示词
│       ├── general_verifier.txt # 通用验证器提示词
│       └── reviewer.txt         # 审阅代理提示词
├── agents/                       # Agent 组件模块
│   ├── __init__.py
│   ├── base_agent.py            # 工作流基础 Agent 类
│   ├── describer/               # 问题描述代理
│   │   ├── __init__.py
│   │   └── agent.py             # Describer Agent 实现
│   ├── planner/                 # 规划代理
│   │   ├── __init__.py
│   │   └── agent.py             # Planner Agent 实现
│   ├── solver/                  # 解题代理
│   │   ├── __init__.py
│   │   └── agent.py             # Solver Agent 实现
│   ├── verifier/                # 验证器模块
│   │   ├── __init__.py
│   │   ├── physics_verifier.py  # 物理验证器实现
│   │   └── general_verifier.py  # 通用验证器实现
│   └── reviewer/                # 审阅代理
│       ├── __init__.py
│       └── agent.py             # Reviewer Agent 实现
├── tools/                        # 工具模块
│   ├── __init__.py
│   └── wolfram_tools.py         # Wolfram Script 工具
└── utils/                        # 工具函数模块
    ├── __init__.py
    └── logger.py                # 工作流日志记录器
```

## 模块说明

### 核心模块

#### 1. `main.py` - 主程序入口
- **功能**：整合所有子模块，提供命令行接口
- **职责**：
  - 加载配置和环境变量
  - 创建和初始化各个 Agent
  - 启动工作流
  - 处理用户输入和输出

#### 2. `config/` - 配置管理
- **settings.py**：
  - 从环境变量加载配置
  - 提供配置验证
  - 管理默认值和常量

#### 3. `agents/` - Agent 组件
- **base_agent.py**：
  - 定义 `PhysicsFlowAgent` 工作流
  - 编排子 agent 执行顺序
  - 处理循环和决策逻辑
  
- **describer/**：
  - 生成规范化的题目描述
  - 结构化输出：物理领域、已知条件、未知量、约束条件

- **planner/**：
  - 生成多个带优先级的解题思路
  - JSON 格式输出思路和步骤

- **solver/**：
  - 按照选定思路逐步解答
  - 支持 LaTeX 格式输出
  - 集成 Wolfram 计算工具

- **verifier/**：
  - `physics_verifier.py`：验证物理正确性（公式、原理、量纲）
  - `general_verifier.py`：验证数学和逻辑正确性

- **reviewer/**：
  - 综合审阅结果
  - 决策：SUCCESS/REVISE/SWITCH_PLAN/FAIL

### 工具模块

#### 4. `tools/` - 外部工具
- **wolfram_tools.py**：
  - `wolfram_calculate()`：数学计算
  - `wolfram_verify_formula()`：公式验证
  - `wolfram_check_dimensions()`：量纲分析

#### 5. `utils/` - 工具函数
- **logger.py**：
  - `WorkflowLogger`：工作流日志记录
  - 文本和 JSON 双格式输出
  - 自动保存所有中间步骤

### 配置文件

#### 6. `config/prompts/` - 提示词
每个 agent 的提示词独立存储为文本文件：
- 易于修改和优化
- 支持版本控制
- 代码与提示词分离

## 工作流程

```
用户问题 (question.md)
    ↓
Describer (问题描述)
    ↓
Planner (解题规划)
    ↓
Solver (问题解答) ←→ Wolfram Tools
    ↓
Physics Verifier (物理验证)
    ↓
General Verifier (通用验证) ←→ Wolfram Tools
    ↓
Reviewer (审阅决策)
    ↓
决策结果：
- SUCCESS → 输出答案
- REVISE → 返回 Solver 修订
- SWITCH_PLAN → 切换解题思路
- FAIL → 结束流程
```

## 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云 API 密钥 | 必需 |
| `DEFAULT_MODEL` | 使用的模型 | `openai/qwen3.5-plus` |
| `API_BASE_URL` | API 基础 URL | 阿里云 DashScope |
| `QUESTION_FILE` | 问题文件路径 | `d:/ADK/question.md` |
| `LOG_DIR` | 日志输出目录 | `d:/ADK/phyagent/logs` |
| `MAX_PLAN_ATTEMPTS` | 最大 Plan 尝试次数 | `2` |
| `MAX_REVISION_ATTEMPTS` | 最大修订次数 | `3` |
| `HIGH_TEMPERATURE` | 高 temperature 值 | `0.8` |
| `WOLFRAM_TIMEOUT` | Wolfram 计算超时（秒） | `30` |

## 日志输出

系统会自动在 `LOG_DIR` 目录下生成日志文件：

- `workflow_YYYYMMDD_HHMMSS.txt`：人类可读的文本日志
- `workflow_YYYYMMDD_HHMMSS.json`：机器可读的 JSON 数据

包含内容：
- 初始问题
- 规范化题目描述
- 解题思路规划
- 每次尝试的解答
- 物理验证结果
- 通用验证结果
- 审阅决策
- 最终状态

## 扩展开发

### 添加新的 Agent

1. 在 `agents/` 下创建新文件夹
2. 实现 `agent.py` 和 `__init__.py`
3. 在 `config/prompts/` 创建对应的提示词文件
4. 在 `agents/__init__.py` 中注册

### 添加新的工具

1. 在 `tools/` 下创建新的工具文件
2. 实现工具函数（返回 `Dict[str, Any]`）
3. 在 `tools/__init__.py` 中导出
4. 在需要的 Agent 中引入并使用

### 修改提示词

直接编辑 `config/prompts/` 下对应的 `.txt` 文件，无需修改代码。

## 依赖项

- `google-adk`：Agent Development Kit
- `python-dotenv`：环境变量管理
- `wolframscript`：可选，用于数学计算（需单独安装）
