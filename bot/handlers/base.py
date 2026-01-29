"""基础命令处理器"""
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.ai import reset_user_chat
from bot.config import Config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """重置聊天历史"""
    user_id = update.effective_user.id
    reset_user_chat(user_id)
    await update.message.reply_text(
        "你好！我是你的 AI 助手。我们开始聊天吧！\n\n"
        "可用命令：\n"
        "/start - 清空记忆重新开始\n"
        "/help - 查看所有命令\n"
        "/sleepon [HH:MM] - 开启睡眠提醒（可自定义时间）\n"
        "/sleepoff - 关闭睡眠提醒\n"
        "/sleepstatus - 查看睡眠提醒状态"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示帮助信息"""
    help_text = f"""🤖 AI 助手命令列表：

📝 聊天命令：
/start - 清空对话记忆，重新开始
/help - 显示此帮助信息

💤 睡眠提醒命令：
/sleepon [HH:MM] - 开启提醒，可指定时间（默认 {Config.DEFAULT_REMINDER_TIME}）
/sleepoff - 关闭睡眠提醒
/sleepstatus - 查看当前提醒设置

💡 直接发送文字即可与 AI 聊天！"""
    await update.message.reply_text(help_text)
