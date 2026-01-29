"""Telegram Bot API mock fixtures"""
import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_user():
    """Mock Telegram User 对象"""
    user = MagicMock()
    user.id = 12345
    user.username = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    return user


@pytest.fixture
def mock_chat():
    """Mock Telegram Chat 对象"""
    chat = MagicMock()
    chat.id = 12345
    chat.type = "private"
    return chat


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Mock Telegram Message 对象"""
    message = MagicMock()
    message.message_id = 1
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "Hello"
    message.reply_text = AsyncMock()
    return message


@pytest.fixture
def mock_update(mock_user, mock_chat, mock_message):
    """Mock Telegram Update 对象"""
    update = MagicMock()
    update.update_id = 1
    update.effective_user = mock_user
    update.effective_chat = mock_chat
    update.message = mock_message
    return update


@pytest.fixture
def mock_context():
    """Mock Telegram Context 对象"""
    context = MagicMock()
    context.args = []
    context.bot_data = {}

    # Mock bot methods
    context.bot.send_chat_action = AsyncMock()
    context.bot.send_message = AsyncMock()

    # Mock job queue
    context.job_queue = MagicMock()
    context.job_queue.get_jobs_by_name = MagicMock(return_value=[])
    context.job_queue.run_daily = MagicMock()

    # Mock job (for callbacks)
    context.job = MagicMock()
    context.job.data = {}
    context.job.schedule_removal = MagicMock()

    return context


@pytest.fixture
def mock_job():
    """Mock Job 对象"""
    job = MagicMock()
    job.name = "test_job"
    job.data = {}
    job.schedule_removal = MagicMock()
    job.next_t = None
    return job
