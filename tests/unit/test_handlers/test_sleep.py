"""睡眠提醒命令处理器单元测试"""
import pytest
from datetime import time, datetime
from unittest.mock import MagicMock, AsyncMock

from bot.handlers.sleep import sleep_on, sleep_off, sleep_status
from bot.services.reminder import sleep_reminder_users
from bot.config import Config


class TestSleepOnCommand:
    """测试 /sleepon 命令"""

    @pytest.mark.asyncio
    async def test_sleep_on_with_default_time(self, mock_update, mock_context):
        """测试 /sleepon 使用默认时间"""
        mock_update.effective_chat.id = 12345
        mock_context.args = []  # 无参数

        await sleep_on(mock_update, mock_context)

        # 验证创建了任务
        mock_context.job_queue.run_daily.assert_called_once()
        call_args = mock_context.job_queue.run_daily.call_args
        assert call_args[1]["name"] == "sleep_reminder_12345"
        assert call_args[1]["data"]["chat_id"] == 12345

    @pytest.mark.asyncio
    async def test_sleep_on_with_custom_time(self, mock_update, mock_context):
        """测试 /sleepon 使用自定义时间"""
        mock_update.effective_chat.id = 12345
        mock_context.args = ["22:00"]

        await sleep_on(mock_update, mock_context)

        # 验证创建了任务
        mock_context.job_queue.run_daily.assert_called_once()
        call_args = mock_context.job_queue.run_daily.call_args
        assert call_args[1]["data"]["time_str"] == "22:00"

    @pytest.mark.asyncio
    async def test_sleep_on_with_invalid_time(self, mock_update, mock_context):
        """测试 /sleepon 使用无效时间"""
        mock_update.effective_chat.id = 12345
        mock_context.args = ["invalid"]

        await sleep_on(mock_update, mock_context)

        # 验证发送了错误消息
        mock_update.message.reply_text.assert_called_once()
        message = mock_update.message.reply_text.call_args[0][0]
        assert "时间格式错误" in message or "格式示例" in message

    @pytest.mark.asyncio
    async def test_sleep_on_removes_existing_job(self, mock_update, mock_context):
        """测试 /sleepon 删除已存在的任务"""
        mock_update.effective_chat.id = 12345
        mock_context.args = ["23:00"]

        # 模拟已存在的任务
        existing_job = MagicMock()
        existing_job.schedule_removal = MagicMock()
        mock_context.job_queue.get_jobs_by_name.return_value = [existing_job]

        await sleep_on(mock_update, mock_context)

        # 验证删除了旧任务
        existing_job.schedule_removal.assert_called_once()

    @pytest.mark.asyncio
    async def test_sleep_on_stores_reminder_in_dict(self, mock_update, mock_context):
        """测试 /sleepon 在字典中存储提醒"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id
        mock_context.args = ["22:30"]

        await sleep_on(mock_update, mock_context)

        # 验证存储在字典中
        assert chat_id in sleep_reminder_users
        assert "time" in sleep_reminder_users[chat_id]

    @pytest.mark.asyncio
    async def test_sleep_on_sends_confirmation(self, mock_update, mock_context):
        """测试 /sleepon 发送确认消息"""
        mock_update.effective_chat.id = 12345
        mock_context.args = ["22:00"]

        await sleep_on(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "已开启" in message or "✅" in message
        assert "22:00" in message

    @pytest.mark.asyncio
    async def test_sleep_on_shows_help_tips(self, mock_update, mock_context):
        """测试确认消息包含帮助提示"""
        mock_update.effective_chat.id = 12345
        mock_context.args = []

        await sleep_on(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "/sleepoff" in message
        assert "/sleepon" in message
        assert "/sleepstatus" in message


class TestSleepOffCommand:
    """测试 /sleepoff 命令"""

    @pytest.mark.asyncio
    async def test_sleep_off_when_enabled(self, mock_update, mock_context):
        """测试 /sleepoff 当提醒已开启时"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id

        # 先添加用户到字典
        sleep_reminder_users[chat_id] = {"time": time(23, 30)}

        # 模拟任务存在
        mock_job = MagicMock()
        mock_job.schedule_removal = MagicMock()
        mock_context.job_queue.get_jobs_by_name.return_value = [mock_job]

        await sleep_off(mock_update, mock_context)

        # 验证删除了任务
        mock_job.schedule_removal.assert_called_once()
        # 验证从字典中移除
        assert chat_id not in sleep_reminder_users

    @pytest.mark.asyncio
    async def test_sleep_off_when_not_enabled(self, mock_update, mock_context):
        """测试 /sleepoff 当提醒未开启时"""
        mock_update.effective_chat.id = 12345

        await sleep_off(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "还没有开启" in message or "⚠️" in message

    @pytest.mark.asyncio
    async def test_sleep_off_sends_confirmation(self, mock_update, mock_context):
        """测试 /sleepoff 发送确认消息"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id
        sleep_reminder_users[chat_id] = {"time": time(23, 30)}

        mock_job = MagicMock()
        mock_job.schedule_removal = MagicMock()
        mock_context.job_queue.get_jobs_by_name.return_value = [mock_job]

        await sleep_off(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "已关闭" in message or "❌" in message


class TestSleepStatusCommand:
    """测试 /sleepstatus 命令"""

    @pytest.mark.asyncio
    async def test_sleep_status_when_not_enabled(self, mock_update, mock_context):
        """测试 /sleepstatus 当提醒未开启时"""
        mock_update.effective_chat.id = 12345

        await sleep_status(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "未开启" in message or "💤" in message

    @pytest.mark.asyncio
    async def test_sleep_status_when_enabled(self, mock_update, mock_context):
        """测试 /sleepstatus 当提醒已开启时"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id

        # 添加用户到字典
        reminder_time = time(22, 30)
        sleep_reminder_users[chat_id] = {"time": reminder_time}

        await sleep_status(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "已开启" in message
        assert "22:30" in message

    @pytest.mark.asyncio
    async def test_sleep_status_shows_next_run_time(self, mock_update, mock_context):
        """测试 /sleepstatus 显示下次执行时间"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id
        sleep_reminder_users[chat_id] = {"time": time(22, 30)}

        # 模拟任务存在并设置下次运行时间
        mock_job = MagicMock()
        next_time = datetime(2024, 1, 1, 22, 30, 0)
        mock_job.next_t = next_time
        mock_context.job_queue.get_jobs_by_name.return_value = [mock_job]

        await sleep_status(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "下次提醒" in message

    @pytest.mark.asyncio
    async def test_sleep_status_includes_management_commands(self, mock_update, mock_context):
        """测试 /sleepstatus 包含管理命令"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id
        sleep_reminder_users[chat_id] = {"time": time(22, 30)}

        await sleep_status(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "/sleepon" in message
        assert "/sleepoff" in message

    @pytest.mark.asyncio
    async def test_sleep_status_formats_time_correctly(self, mock_update, mock_context):
        """测试时间格式化正确 (HH:MM)"""
        chat_id = 12345
        mock_update.effective_chat.id = chat_id
        sleep_reminder_users[chat_id] = {"time": time(9, 5)}  # 9:05

        await sleep_status(mock_update, mock_context)

        message = mock_update.message.reply_text.call_args[0][0]
        assert "09:05" in message
