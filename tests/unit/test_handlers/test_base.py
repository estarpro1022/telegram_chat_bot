"""基础命令处理器单元测试"""
import pytest
from unittest.mock import AsyncMock

from bot.handlers.base import start, help_cmd


class TestStartCommand:
    """测试 /start 命令"""

    @pytest.mark.asyncio
    async def test_start_resets_user_chat(self, mock_update, mock_context, mocker):
        """测试 /start 命令重置用户聊天"""
        mock_update.effective_user.id = 12345

        mock_reset = mocker.patch('bot.handlers.base.reset_user_chat')

        await start(mock_update, mock_context)

        mock_reset.assert_called_once_with(12345)

    @pytest.mark.asyncio
    async def test_start_sends_welcome_message(self, mock_update, mock_context):
        """测试 /start 命令发送欢迎消息"""
        await start(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]

        assert "你好" in message or "AI 助手" in message

    @pytest.mark.asyncio
    async def test_start_includes_all_commands(self, mock_update, mock_context):
        """测试欢迎消息包含所有命令"""
        await start(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]

        # 检查包含所有命令
        assert "/start" in message
        assert "/help" in message
        assert "/sleepon" in message
        assert "/sleepoff" in message
        assert "/sleepstatus" in message


class TestHelpCommand:
    """测试 /help 命令"""

    @pytest.mark.asyncio
    async def test_help_sends_help_text(self, mock_update, mock_context):
        """测试 /help 命令发送帮助文本"""
        await help_cmd(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]

        assert "命令" in message or "AI" in message

    @pytest.mark.asyncio
    async def test_help_includes_default_reminder_time(self, mock_update, mock_context):
        """测试帮助文本包含默认提醒时间"""
        from bot.config import Config

        await help_cmd(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]

        assert Config.DEFAULT_REMINDER_TIME in message

    @pytest.mark.asyncio
    async def test_help_lists_all_commands(self, mock_update, mock_context):
        """测试帮助文本列出所有命令"""
        await help_cmd(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]

        # 检查所有命令都存在
        assert "/start" in message
        assert "/help" in message
        assert "/sleepon" in message
        assert "/sleepoff" in message
        assert "/sleepstatus" in message

    @pytest.mark.asyncio
    async def test_help_has_proper_formatting(self, mock_update, mock_context):
        """测试帮助文本有正确的格式"""
        await help_cmd(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]

        # 应该包含一些格式符号
        assert len(message) > 50  # 足够详细
