# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述

集成 Google Cloud Vertex AI (Gemini) 的 Telegram 机器人，提供 AI 聊天和可自定义的睡眠提醒功能。使用 `python-telegram-bot` 及其任务队列支持定时任务。

## 开发命令

### 运行机器人
```bash
# 运行主 AI 聊天机器人
uv run chat.py

# 运行简单模板机器人
uv run main.py
```

### 依赖管理
项目使用 `uv` 作为包管理器：
```bash
# 安装依赖
uv sync

# 添加依赖
uv add <package>
```

## 架构

### 项目结构
```
telegram/
├── .env                 # 环境变量配置（不提交到 git）
├── config.py            # 配置管理模块
├── sleep_reminder.py    # 睡眠提醒功能模块
├── chat.py              # 主程序：AI 聊天 + 命令路由
├── main.py              # 简单模板机器人（参考）
├── pyproject.toml       # 项目配置
└── CLAUDE.md            # 开发者指南（本文件）
```

### 模块说明

**`config.py` - 配置管理**
- 使用 `python-dotenv` 从 `.env` 文件加载配置
- 提供 `Config` 类集中管理所有配置项
- 启动时验证必需的配置项

**`sleep_reminder.py` - 睡眠提醒**
- 独立的睡眠提醒功能模块
- 导出函数：`sleep_on`, `sleep_off`, `sleep_status`
- 管理用户提醒配置和定时任务

**`chat.py` - 主程序**
- AI 聊天逻辑
- Telegram 命令路由
- 整合各模块功能

### 核心组件

**AI 聊天系统：**
- 使用 Vertex AI `GenerativeModel` 模型 `gemini-2.5-flash`
- 在 `user_chats` 字典中维护每个用户的聊天历史：`{user_id: ChatSession}`
- 通过 `chat.send_message(user_text, stream=True)` 实现流式响应

**睡眠提醒系统：**
- 每个用户可独立配置提醒时间，存储在 `sleep_reminder.sleep_reminder_users` 字典
- 每个用户有独立的每日任务：`sleep_reminder_{chat_id}`
- 使用 `context.job_queue.run_daily()` 进行调度
- 通过命令动态创建/更新/删除任务

**命令处理器：**
| 命令 | 处理函数 | 模块 | 用途 |
|------|----------|------|------|
| `/start` | `start()` | chat.py | 重置聊天历史，显示帮助 |
| `/help` | `help_cmd()` | chat.py | 显示所有命令帮助 |
| `/sleepon [HH:MM]` | `sleep_on()` | bot/handlers/sleep.py | 开启/配置提醒 |
| `/sleepoff` | `sleep_off()` | bot/handlers/sleep.py | 关闭提醒，删除任务 |
| `/sleepstatus` | `sleep_status()` | bot/handlers/sleep.py | 显示当前提醒设置 |
| (文本消息) | `chat_logic()` | chat.py | AI 聊天处理 |

**关键设计模式：**
- 时区感知：使用 `Config.BEIJING_TZ` 处理北京时间
- 任务命名：`f"sleep_reminder_{chat_id}"` 用于按用户管理任务
- 上下文数据：任务存储 `{"chat_id": ..., "time_str": ...}` 供回调访问
- 无持久化：所有数据存储在内存中（重启后丢失）

### 配置项

**环境变量 (.env)：**
```bash
TELEGRAM_TOKEN=         # BotFather 提供的机器人令牌
PROJECT_ID=             # Google Cloud 项目 ID
LOCATION=               # Vertex AI 区域（默认 us-central1）
DEFAULT_REMINDER_TIME=  # 默认睡眠提醒时间（默认 23:30）
TIMEZONE=               # 时区（默认 Asia/Shanghai）
```

**配置访问：**
```python
from config import Config

Config.TELEGRAM_TOKEN
Config.PROJECT_ID
Config.LOCATION
Config.DEFAULT_REMINDER_TIME
Config.BEIJING_TZ
```

## 重要说明

- **无数据持久化**：重启后所有聊天历史和提醒设置都会丢失
- **chat_id 与 user_id**：提醒系统使用 `chat_id`（非 `user_id`），意味着不同场景（私聊 vs 群组）有独立的提醒设置
- **任务管理**：更新提醒时间时，必须先删除旧任务再创建新任务
- **环境变量**：`.env` 文件包含敏感信息，不应提交到 git
- **文档同步**：修改代码后，请及时更新 [README.md](README.md) 以保持文档与代码一致
