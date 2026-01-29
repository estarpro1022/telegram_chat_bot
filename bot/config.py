"""配置管理模块"""
from dotenv import load_dotenv
import os
import pytz

# 加载 .env 文件
load_dotenv()


class Config:
    """应用配置类"""

    # Telegram 配置
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Google Cloud Vertex AI 配置
    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("LOCATION", "us-central1")

    # 睡眠提醒配置
    DEFAULT_REMINDER_TIME = os.getenv("DEFAULT_REMINDER_TIME", "23:30")

    # 时区配置
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")
    BEIJING_TZ = pytz.timezone(TIMEZONE)

    @classmethod
    def validate(cls):
        """验证必需的配置项"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN 未设置")
        if not cls.PROJECT_ID:
            raise ValueError("PROJECT_ID 未设置")
        return True


# 验证配置
Config.validate()
