# 快速启动指南

## 5 分钟快速开始

### 步骤 1：配置环境变量

```bash
# 进入项目目录
cd d:\ADK\phyagent

# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
# 使用记事本或任何文本编辑器打开 .env
```

在 `.env` 文件中填写：
```env
DASHSCOPE_API_KEY=sk-your-actual-api-key-here
```

### 步骤 2：准备问题

编辑 `d:\ADK\question.md` 文件，写入物理问题：
```
一个质量为 2kg 的物体以 10m/s 的初速度水平抛出，求 2 秒后的速度和位置。
```

### 步骤 3：安装依赖（如果需要）

```bash
pip install google-adk python-dotenv
```

### 步骤 4：运行

```bash
cd d:\ADK\phyagent
python main.py
```

## 查看结果

### 控制台输出
- 工作流程进度
- 各阶段状态
- 最终答案

### 日志文件
位置：`d:\ADK\phyagent\logs\`
- `workflow_YYYYMMDD_HHMMSS.txt` - 详细过程
- `workflow_YYYYMMDD_HHMMSS.json` - 结构化数据

## 自定义配置

### 修改问题文件位置

编辑 `.env`：
```env
QUESTION_FILE=d:/my_problems/question1.md
```

### 修改日志目录

编辑 `.env`：
```env
LOG_DIR=d:/my_logs
```

### 调整尝试次数

编辑 `.env`：
```env
MAX_PLAN_ATTEMPTS=3
MAX_REVISION_ATTEMPTS=5
```

## 常见问题

### Q: 找不到 Wolfram Script？
A: Wolfram Script 是可选的。如果未安装，工具会返回错误信息，但系统仍可正常运行。

### Q: 如何更换模型？
A: 编辑 `.env` 文件：
```env
DEFAULT_MODEL=openai/qwen3.5-plus
```

### Q: 提示词如何修改？
A: 直接编辑 `config/prompts/` 下对应的 `.txt` 文件

### Q: 如何添加新的解题思路？
A: 修改 `config/prompts/planner.txt`，调整生成思路的数量和要求

## 下一步

- 阅读完整的 [README.md](README.md) 了解更多功能
- 查看 [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md) 了解重构详情
- 运行 `python test_refactor.py` 验证安装

## 获取帮助

遇到问题？检查以下事项：
1. ✅ `.env` 文件已创建并填写 API 密钥
2. ✅ `question.md` 文件存在且包含有效问题
3. ✅ 依赖项已安装（google-adk, python-dotenv）
4. ✅ 网络连接正常（需要访问 API）

祝使用愉快！
