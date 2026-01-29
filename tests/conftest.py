"""Pytest 配置和共享 fixtures"""
import os
import sys
import pytest

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所有 fixtures 使它们可用
from tests.fixtures.telegram import *
from tests.fixtures.vertex import *


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """
    设置测试所需的环境变量
    autouse=True 表示自动应用于所有测试
    """
    monkeypatch.setenv("TELEGRAM_TOKEN", "test_token_12345")
    monkeypatch.setenv("PROJECT_ID", "test-project-id")
    monkeypatch.setenv("LOCATION", "us-central1")
    monkeypatch.setenv("DEFAULT_REMINDER_TIME", "23:30")
    monkeypatch.setenv("TIMEZONE", "Asia/Shanghai")


@pytest.fixture(autouse=True)
def reset_global_state():
    """
    重置全局状态（如模块级别的字典）
    在每个测试后执行
    """
    yield

    # 重置 AI 服务的用户聊天存储
    from bot.services import ai
    ai.user_chats.clear()

    # 重置睡眠提醒用户存储
    from bot.services import reminder
    reminder.sleep_reminder_users.clear()


# 配置 pytest 标记
def pytest_configure(config):
    """配置 pytest 自定义标记"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "external: Tests requiring external services")
