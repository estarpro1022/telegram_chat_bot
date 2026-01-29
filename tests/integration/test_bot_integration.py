"""Bot 集成测试"""
import pytest


@pytest.mark.integration
class TestBotIntegration:
    """测试 Bot 应用集成"""

    def test_imports_work_correctly(self):
        """测试所有模块可以正确导入"""
        # 基础模块
        from bot import config
        from bot.services import ai, reminder
        from bot.handlers import base, chat, sleep

        # 验证关键函数存在
        assert hasattr(config, 'Config')
        assert hasattr(ai, 'get_user_chat')
        assert hasattr(ai, 'reset_user_chat')
        assert hasattr(reminder, 'parse_time')
        assert hasattr(reminder, 'send_sleep_reminder')
        assert hasattr(base, 'start')
        assert hasattr(base, 'help_cmd')
        assert hasattr(chat, 'chat_logic')
        assert hasattr(sleep, 'sleep_on')
        assert hasattr(sleep, 'sleep_off')
        assert hasattr(sleep, 'sleep_status')

    def test_config_validation(self):
        """测试配置验证在导入时执行"""
        # 重新导入配置模块
        import importlib
        from bot.config import Config

        # 验证必需的配置存在
        assert Config.TELEGRAM_TOKEN is not None
        assert Config.PROJECT_ID is not None
        assert Config.LOCATION is not None
        assert Config.DEFAULT_REMINDER_TIME is not None
        assert Config.TIMEZONE is not None
        assert Config.BEIJING_TZ is not None

    def test_user_chats_dict_exists(self):
        """测试用户聊天字典存在"""
        from bot.services.ai import user_chats
        assert isinstance(user_chats, dict)

    def test_sleep_reminder_users_dict_exists(self):
        """测试睡眠提醒用户字典存在"""
        from bot.services.reminder import sleep_reminder_users
        assert isinstance(sleep_reminder_users, dict)

    @pytest.mark.asyncio
    async def test_parse_time_function_works(self):
        """测试时间解析函数正常工作"""
        from bot.services.reminder import parse_time

        result = parse_time("23:30")
        assert result.hour == 23
        assert result.minute == 30

        # 测试无效时间
        with pytest.raises(ValueError):
            parse_time("invalid")
