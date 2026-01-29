# Telegram AI 助手机器人

集成 Google Cloud Vertex AI (Gemini) 的 Telegram 机器人，提供 AI 聊天和可自定义的睡眠提醒功能。

## 功能特性

- 🤖 **AI 聊天** - 使用 Gemini 2.5 Flash 模型进行智能对话
- 💤 **睡眠提醒** - 可自定义时间的每日睡眠提醒
- 🧠 **对话记忆** - 每个用户独立的聊天历史
- ⏰ **灵活调度** - 每个用户可设置不同的提醒时间

## 快速开始

### 前置要求

- Python 3.12+
- Telegram Bot Token（从 [BotFather](https://t.me/botfather) 获取）
- Google Cloud 项目 ID（启用 Vertex AI API）

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd telegram

# 使用 uv 安装依赖
uv sync
```

### 配置

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
TELEGRAM_TOKEN=你的_Bot_Token
PROJECT_ID=你的_Google_Cloud_项目_ID
LOCATION=us-central1
```

### 运行

```bash
# 方式1：运行模块（推荐）
uv run python -m bot

# 方式2：使用命令行入口
uv run bot
```

## 命令列表

| 命令 | 说明 |
|------|------|
| `/start` | 清空对话记忆，重新开始 |
| `/help` | 显示所有命令帮助 |
| `/sleepon [HH:MM]` | 开启睡眠提醒，可指定时间（默认 23:30）|
| `/sleepoff` | 关闭睡眠提醒 |
| `/sleepstatus` | 查看当前提醒设置 |

### 使用示例

```
/sleepon          # 使用默认时间 23:30
/sleepon 22:10    # 自定义时间 22:10
/sleepstatus      # 查看提醒状态
/sleepoff         # 关闭提醒
```

## 测试

### 运行测试

```bash
# 安装开发依赖
uv sync --all-extras

# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/unit/test_config.py

# 查看覆盖率报告
uv run pytest --cov=bot --cov-report=html
# 打开 htmlcov/index.html
```

### 测试文档

完整的测试文档请参阅：[TESTING.md](TESTING.md)

- 测试概览与覆盖率
- 编写测试指南
- Mock 策略
- 常见问题解答

### 测试覆盖率

项目目标测试覆盖率：**80%**

## 技术栈

- **python-telegram-bot** - Telegram Bot API 封装
- **google-cloud-aiplatform** - Vertex AI SDK
- **pytz** - 时区处理
- **pytest** - 测试框架

## 项目结构

```
telegram/
├── bot/                      # 核心代码包
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # 程序入口
│   ├── config.py            # 配置管理
│   ├── handlers/            # Telegram 命令处理器
│   │   ├── base.py          # 基础命令 (start, help)
│   │   ├── chat.py          # AI 聊天处理
│   │   └── sleep.py         # 睡眠提醒命令
│   └── services/            # 业务服务层
│       ├── ai.py            # AI 服务（Vertex AI）
│       └── reminder.py      # 睡眠提醒服务
├── examples/                # 示例代码
│   └── simple_bot.py        # 简单模板示例
├── .env                     # 环境变量配置
├── .env.example             # 环境变量示例
├── pyproject.toml           # 项目配置
├── CLAUDE.md                # 开发者指南
└── README.md                # 项目说明
```

## 注意事项

- ⚠️ **无数据持久化**：重启后聊天历史和提醒设置会丢失
- ⏰ **时区**：所有时间均为北京时间（Asia/Shanghai）
- 👥 **多场景**：提醒按 chat_id 存储，私聊和群组独立设置

## 许可证

MIT License
