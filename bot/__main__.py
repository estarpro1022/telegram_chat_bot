"""程序入口"""
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

from bot.config import Config
from bot.handlers import start, help_cmd, chat_logic, sleep_on, sleep_off, sleep_status

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()

    # 指令处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("sleepon", sleep_on))
    app.add_handler(CommandHandler("sleepoff", sleep_off))
    app.add_handler(CommandHandler("sleepstatus", sleep_status))

    # 消息处理器：过滤掉指令，只处理纯文本
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_logic))

    print("AI 机器人已启动...")
    print(f"睡眠提醒功能：用户可自定义提醒时间（默认 {Config.DEFAULT_REMINDER_TIME}）")
    app.run_polling()


if __name__ == '__main__':
    main()
