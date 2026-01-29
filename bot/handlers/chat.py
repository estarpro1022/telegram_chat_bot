"""AI 聊天处理器"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.ai import get_user_chat


async def chat_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI 聊天处理逻辑"""
    user_id = update.effective_user.id
    user_text = update.message.text

    # 1. 显示 "typing..." 状态
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # 2. 获取或创建该用户的聊天会话
    chat = get_user_chat(user_id)

    try:
        # 3. 发送给 Vertex AI 并获取流式响应
        response_stream = chat.send_message(user_text, stream=True)

        # 4. 拼接流式回复
        full_response = ""
        for chunk in response_stream:
            full_response += chunk.text

        # 5. 回复用户
        await update.message.reply_text(full_response)

    except Exception as e:
        logging.error(f"AI 聊天出错: {e}")
        await update.message.reply_text("抱歉，我的大脑短路了，请稍后再试。")
