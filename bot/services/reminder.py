"""睡眠提醒服务"""
import logging
from datetime import time

from telegram.ext import ContextTypes

from bot.config import Config

# 存储需要接收睡眠提醒的用户配置
# 结构：{chat_id: {"time": time对象}}
sleep_reminder_users = {}


def parse_time(time_str: str) -> time:
    """
    解析用户输入的时间字符串
    支持格式：HH:MM (24小时制)
    """
    time_str = time_str.strip()
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("时间格式应为 HH:MM")
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("时间超出有效范围")
        return time(hour=hour, minute=minute, tzinfo=Config.BEIJING_TZ)
    except ValueError as e:
        raise ValueError(f"时间格式错误: {e}")


async def send_sleep_reminder(context: ContextTypes.DEFAULT_TYPE):
    """定时任务：发送睡眠提醒给特定用户"""
    chat_id = context.job.data.get("chat_id")
    time_str = context.job.data.get("time_str")

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🌙 晚安！现在是北京时间 {time_str}，该睡觉啦！\n\n早睡早起身体好，明天又是元气满满的一天！💤"
        )
    except Exception as e:
        logging.error(f"发送睡眠提醒给 {chat_id} 失败: {e}")
        # 发送失败，移除任务和数据
        context.job.schedule_removal()
        if chat_id in sleep_reminder_users:
            del sleep_reminder_users[chat_id]
