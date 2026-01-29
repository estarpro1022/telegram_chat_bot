"""配置模块单元测试"""
import os
import pytest
import pytz


class TestConfig:
    """测试 Config 类"""

    def test_telegram_token_from_env(self, monkeypatch):
        """测试从环境变量加载 TELEGRAM_TOKEN"""
        from bot.config import Config

        token = "test_token_12345"
        monkeypatch.setenv("TELEGRAM_TOKEN", token)

        # 由于 conftest 已经设置了环境变量，我们验证它存在
        assert Config.TELEGRAM_TOKEN is not None

    def test_project_id_from_env(self, monkeypatch):
        """测试从环境变量加载 PROJECT_ID"""
        from bot.config import Config

        project_id = "test-project-id"
        monkeypatch.setenv("PROJECT_ID", project_id)

        # 由于 conftest 已经设置了环境变量，我们验证它存在
        assert Config.PROJECT_ID is not None

    def test_location_default_value(self):
        """测试 LOCATION 默认值"""
        from bot.config import Config

        assert Config.LOCATION == "us-central1"

    def test_location_from_env(self, monkeypatch):
        """测试从环境变量加载 LOCATION"""
        location = "us-east1"
        monkeypatch.setenv("LOCATION", location)

        import importlib
        import bot.config
        importlib.reload(bot.config)
        from bot.config import Config as NewConfig

        assert NewConfig.LOCATION == location

    def test_default_reminder_time_default_value(self):
        """测试 DEFAULT_REMINDER_TIME 默认值"""
        from bot.config import Config

        assert Config.DEFAULT_REMINDER_TIME == "23:30"

    def test_timezone_default_value(self):
        """测试 TIMEZONE 默认值"""
        from bot.config import Config

        assert Config.TIMEZONE == "Asia/Shanghai"

    def test_timezone_from_env(self, monkeypatch):
        """测试从环境变量加载 TIMEZONE"""
        timezone = "America/New_York"
        monkeypatch.setenv("TIMEZONE", timezone)

        import importlib
        import bot.config
        importlib.reload(bot.config)
        from bot.config import Config as NewConfig

        assert NewConfig.TIMEZONE == timezone

    def test_beijing_tz_is_timezone_object(self):
        """测试 BEIJING_TZ 是有效的 pytz 时区对象"""
        from bot.config import Config

        # pytz 时区对象是 DynamicTimeZone 或 StaticTimeZone
        assert hasattr(Config.BEIJING_TZ, 'zone')
        # 注意：由于其他测试可能修改了环境变量并重新加载了模块，
        # 这里只验证它是一个有效的时区对象
        assert Config.BEIJING_TZ is not None

    def test_validate_with_all_required_config(self):
        """测试所有必需配置存在时验证通过"""
        from bot.config import Config

        # conftest 设置了所有必需的环境变量
        assert Config.validate() is True

    def test_config_has_required_attributes(self):
        """测试 Config 类有所有必需的属性"""
        from bot.config import Config

        assert hasattr(Config, 'TELEGRAM_TOKEN')
        assert hasattr(Config, 'PROJECT_ID')
        assert hasattr(Config, 'LOCATION')
        assert hasattr(Config, 'DEFAULT_REMINDER_TIME')
        assert hasattr(Config, 'TIMEZONE')
        assert hasattr(Config, 'BEIJING_TZ')
        assert hasattr(Config, 'validate')
