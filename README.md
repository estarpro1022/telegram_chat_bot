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

编辑 `chat.py` 中的配置项：

```python
TELEGRAM_TOKEN = "你的_Bot_Token"
PROJECT_ID = "你的_Google_Cloud_项目_ID"
LOCATION = "us-central1"  # 或 asia-east1 等
```

### 运行

```bash
uv run chat.py
```

## 命令列表

| 命令 | 说明 |
|------|------|
| `/start` | 清空对话记忆，重新开始 |
| `/help` | 显示所有命令帮助 |
| `/sleep_on [HH:MM]` | 开启睡眠提醒，可指定时间（默认 23:30）|
| `/sleep_off` | 关闭睡眠提醒 |
| `/sleep_status` | 查看当前提醒设置 |

### 使用示例

```
/sleep_on          # 使用默认时间 23:30
/sleep_on 22:10    # 自定义时间 22:10
/sleep_status      # 查看提醒状态
/sleep_off         # 关闭提醒
```

## 技术栈

- **python-telegram-bot** - Telegram Bot API 封装
- **google-cloud-aiplatform** - Vertex AI SDK
- **pytz** - 时区处理

## 项目结构

```
telegram/
├── chat.py          # 主程序：AI 聊天 + 睡眠提醒
├── main.py          # 简单模板示例
├── pyproject.toml   # 项目配置
└── CLAUDE.md        # 开发者指南
```

## 注意事项

- ⚠️ **无数据持久化**：重启后聊天历史和提醒设置会丢失
- ⏰ **时区**：所有时间均为北京时间（Asia/Shanghai）
- 👥 **多场景**：提醒按 chat_id 存储，私聊和群组独立设置

## 许可证

MIT License
