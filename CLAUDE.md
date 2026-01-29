# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述

集成 Google Cloud Vertex AI (Gemini) 的 Telegram 机器人，提供 AI 聊天和可自定义的睡眠提醒功能。使用 `python-telegram-bot` 及其任务队列支持定时任务。

## 开发命令

### 运行机器人
```bash
# 运行主 AI 聊天机器人
python chat.py

# 运行简单模板机器人
python main.py
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

### 入口文件
- **`chat.py`** - 生产环境主机器人，包含 AI 聊天和睡眠提醒功能
- **`main.py`** - 简单模板机器人，用于基础命令处理（参考/示例）

### 核心组件 (chat.py)

**AI 聊天系统：**
- 使用 Vertex AI `GenerativeModel` 模型 `gemini-2.5-flash`
- 在 `user_chats` 字典中维护每个用户的聊天历史：`{user_id: ChatSession}`
- 通过 `chat.send_message(user_text, stream=True)` 实现流式响应

**睡眠提醒系统：**
- 每个用户可独立配置提醒时间，存储在 `sleep_reminder_users` 字典：`{chat_id: {"time": time对象}}`
- 每个用户有独立的每日任务：`sleep_reminder_{chat_id}`
- 使用 `context.job_queue.run_daily()` 进行调度
- 通过命令动态创建/更新/删除任务

**命令处理器：**
| 命令 | 处理函数 | 用途 |
|------|----------|------|
| `/start` | `start()` | 重置聊天历史，显示帮助 |
| `/sleep_on [HH:MM]` | `sleep_on()` | 开启/配置提醒（默认 23:30）|
| `/sleep_off` | `sleep_off()` | 关闭提醒，删除任务 |
| `/sleep_status` | `sleep_status()` | 显示当前提醒设置 |
| (文本消息) | `chat_logic()` | AI 聊天处理 |

**关键设计模式：**
- 时区感知：使用 `pytz.timezone('Asia/Shanghai')` 处理北京时间
- 任务命名：`f"sleep_reminder_{chat_id}"` 用于按用户管理任务
- 上下文数据：任务存储 `{"chat_id": ..., "time_str": ...}` 供回调访问
- 无持久化：所有数据存储在内存中（重启后丢失）

### 配置项

硬编码在 `chat.py` 中：
- `TELEGRAM_TOKEN` - BotFather 提供的机器人令牌
- `PROJECT_ID` - Google Cloud 项目 ID
- `LOCATION` - Vertex AI 区域（如 `us-central1`）
- `DEFAULT_REMINDER_TIME` - 默认睡眠提醒时间（`23:30`）

## 重要说明

- **无数据持久化**：重启后所有聊天历史和提醒设置都会丢失
- **chat_id 与 user_id**：提醒系统使用 `chat_id`（非 `user_id`），意味着不同场景（私聊 vs 群组）有独立的提醒设置
- **任务管理**：更新提醒时间时，必须先删除旧任务再创建新任务
