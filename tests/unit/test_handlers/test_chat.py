"""AI 聊天处理器单元测试"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from bot.handlers.chat import chat_logic


class MockAsyncIterator:
    """模拟可被同步迭代的异步生成器"""

    def __init__(self, chunks):
        self.chunks = chunks

    def __iter__(self):
        """支持同步迭代"""
        for chunk in self.chunks:
            c = MagicMock()
            c.text = chunk
            yield c


class TestChatLogic:
    """测试 chat_logic 函数"""

    @pytest.mark.asyncio
    async def test_chat_logic_sends_typing_action(self, mock_update, mock_context, mocker):
        """测试发送 typing 动作"""
        mock_update.effective_user.id = 12345
        mock_update.effective_chat.id = 12345
        mock_update.message.text = "Hello"

        # Mock AI chat with working stream
        mock_chat = mocker.MagicMock()
        mock_stream = MockAsyncIterator(["Hello!"])
        mock_chat.send_message = MagicMock(return_value=mock_stream)
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)

        await chat_logic(mock_update, mock_context)

        mock_context.bot.send_chat_action.assert_called_once_with(
            chat_id=12345,
            action="typing"
        )

    @pytest.mark.asyncio
    async def test_chat_logic_sends_message_to_ai(self, mock_update, mock_context, mocker):
        """测试向 AI 发送消息"""
        user_text = "Hello, how are you?"
        mock_update.effective_user.id = 12345
        mock_update.message.text = user_text

        mock_chat = mocker.MagicMock()
        mock_stream = MockAsyncIterator(["I'm fine!"])
        mock_chat.send_message = MagicMock(return_value=mock_stream)
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)

        await chat_logic(mock_update, mock_context)

        mock_chat.send_message.assert_called_once_with(user_text, stream=True)

    @pytest.mark.asyncio
    async def test_chat_logic_replies_to_user(self, mock_update, mock_context, mocker):
        """测试回复用户"""
        mock_update.effective_user.id = 12345
        mock_update.message.text = "Hello"

        mock_chat = mocker.MagicMock()
        mock_stream = MockAsyncIterator(["Hello! How can I help?"])
        mock_chat.send_message = MagicMock(return_value=mock_stream)
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)

        await chat_logic(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]
        assert "Hello! How can I help?" in message

    @pytest.mark.asyncio
    async def test_chat_logic_handles_ai_exception(self, mock_update, mock_context, mocker):
        """测试处理 AI 异常"""
        mock_update.effective_user.id = 12345
        mock_update.message.text = "Hello"

        mock_chat = mocker.MagicMock()
        mock_chat.send_message = MagicMock(side_effect=Exception("AI error"))
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)
        mocker.patch('bot.handlers.chat.logging.error')

        await chat_logic(mock_update, mock_context)

        # 应该发送错误消息给用户
        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]
        assert "抱歉" in message or "大脑短路" in message

    @pytest.mark.asyncio
    async def test_chat_logic_logs_error_on_failure(self, mock_update, mock_context, mocker):
        """测试失败时记录错误日志"""
        mock_update.effective_user.id = 12345
        mock_update.message.text = "Hello"

        mock_chat = mocker.MagicMock()
        mock_chat.send_message = MagicMock(side_effect=Exception("Network error"))
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)

        mock_logger = mocker.patch('bot.handlers.chat.logging.error')

        await chat_logic(mock_update, mock_context)

        mock_logger.assert_called_once()
        assert "AI 聊天出错" in mock_logger.call_args[0][0]

    @pytest.mark.asyncio
    async def test_chat_logic_accumulates_streaming_response(self, mock_update, mock_context, mocker):
        """测试拼接流式响应"""
        mock_update.effective_user.id = 12345
        mock_update.message.text = "Tell me a joke"

        mock_chat = mocker.MagicMock()
        chunks = ["Why ", "did ", "the ", "chicken ", "cross ", "the ", "road?"]
        mock_stream = MockAsyncIterator(chunks)
        mock_chat.send_message = MagicMock(return_value=mock_stream)
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)

        await chat_logic(mock_update, mock_context)

        expected_response = "Why did the chicken cross the road?"
        mock_update.message.reply_text.assert_called_once_with(expected_response)

    @pytest.mark.asyncio
    async def test_chat_logic_with_empty_response(self, mock_update, mock_context, mocker):
        """测试处理空响应"""
        mock_update.effective_user.id = 12345
        mock_update.message.text = "Hello"

        mock_chat = mocker.MagicMock()
        mock_stream = MockAsyncIterator([""])
        mock_chat.send_message = MagicMock(return_value=mock_stream)
        mocker.patch('bot.handlers.chat.get_user_chat', return_value=mock_chat)

        await chat_logic(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once_with("")
