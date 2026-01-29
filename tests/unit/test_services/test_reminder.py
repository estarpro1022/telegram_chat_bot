"""睡眠提醒服务单元测试"""
import pytest
from datetime import time
from unittest.mock import AsyncMock

from bot.services.reminder import parse_time, send_sleep_reminder, sleep_reminder_users


class TestParseTime:
    """测试 parse_time 函数"""

    def test_parse_valid_time_with_colon(self):
        """测试解析有效时间格式 HH:MM"""
        result = parse_time("23:30")
        assert result.hour == 23
        assert result.minute == 30

    def test_parse_valid_time_single_digit_hour(self):
        """测试解析单位数小时 (9:00)"""
        result = parse_time("9:00")
        assert result.hour == 9
        assert result.minute == 0

    def test_parse_valid_time_with_leading_zero(self):
        """测试解析带前导零的时间 (09:00)"""
        result = parse_time("09:00")
        assert result.hour == 9
        assert result.minute == 0

    def test_parse_valid_time_midnight(self):
        """测试解析午夜时间 (00:00)"""
        result = parse_time("00:00")
        assert result.hour == 0
        assert result.minute == 0

    def test_parse_valid_time_last_minute(self):
        """测试解析最后分钟 (23:59)"""
        result = parse_time("23:59")
        assert result.hour == 23
        assert result.minute == 59

    def test_parse_time_with_whitespace(self):
        """测试解析带空格的时间"""
        result = parse_time("  23:30  ")
        assert result.hour == 23
        assert result.minute == 30

    def test_parse_time_missing_colon(self):
        """测试缺少冒号时抛出 ValueError"""
        with pytest.raises(ValueError, match="时间格式应为 HH:MM"):
            parse_time("2330")

    def test_parse_time_wrong_parts(self):
        """测试部分数量错误时抛出 ValueError"""
        with pytest.raises(ValueError, match="时间格式应为 HH:MM"):
            parse_time("23:30:00")

    def test_parse_time_invalid_hour_negative(self):
        """测试无效小时（负数）时抛出 ValueError"""
        with pytest.raises(ValueError, match="时间超出有效范围"):
            parse_time("-1:00")

    def test_parse_time_invalid_hour_too_large(self):
        """测试无效小时（超过23）时抛出 ValueError"""
        with pytest.raises(ValueError, match="时间超出有效范围"):
            parse_time("24:00")

    def test_parse_time_invalid_minute_negative(self):
        """测试无效分钟（负数）时抛出 ValueError"""
        with pytest.raises(ValueError, match="时间超出有效范围"):
            parse_time("23:-1")

    def test_parse_time_invalid_minute_too_large(self):
        """测试无效分钟（超过59）时抛出 ValueError"""
        with pytest.raises(ValueError, match="时间超出有效范围"):
            parse_time("23:60")

    def test_parse_time_non_numeric(self):
        """测试非数字输入时抛出 ValueError"""
        with pytest.raises(ValueError):
            parse_time("ab:cd")

    def test_parse_time_has_timezone_info(self):
        """测试解析的时间包含正确的时区信息"""
        result = parse_time("23:30")
        assert result.tzinfo is not None
        # 检查时区是北京时间
        assert "Shanghai" in str(result.tzinfo) or "CST" in str(result.tzinfo)


class TestSendSleepReminder:
    """测试 send_sleep_reminder 函数"""

    @pytest.mark.asyncio
    async def test_send_reminder_success(self, mock_context):
        """测试成功发送睡眠提醒"""
        mock_context.job.data = {"chat_id": 12345, "time_str": "23:30"}
        mock_context.bot.send_message = AsyncMock()

        await send_sleep_reminder(mock_context)

        mock_context.bot.send_message.assert_called_once_with(
            chat_id=12345,
            text="🌙 晚安！现在是北京时间 23:30，该睡觉啦！\n\n早睡早起身体好，明天又是元气满满的一天！💤"
        )

    @pytest.mark.asyncio
    async def test_send_reminder_with_different_time(self, mock_context):
        """测试发送不同时间的提醒"""
        mock_context.job.data = {"chat_id": 99999, "time_str": "22:00"}
        mock_context.bot.send_message = AsyncMock()

        await send_sleep_reminder(mock_context)

        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert call_args[1]["chat_id"] == 99999
        assert "22:00" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_send_reminder_failure_logs_error(self, mock_context, mocker):
        """测试发送失败时记录错误日志"""
        mock_context.job.data = {"chat_id": 12345, "time_str": "23:30"}
        mock_context.bot.send_message = AsyncMock(side_effect=Exception("Network error"))

        mock_logger = mocker.patch('bot.services.reminder.logging.error')

        await send_sleep_reminder(mock_context)

        mock_logger.assert_called_once()
        assert "发送睡眠提醒给 12345 失败" in mock_logger.call_args[0][0]

    @pytest.mark.asyncio
    async def test_send_reminder_failure_removes_job(self, mock_context, mocker):
        """测试发送失败时移除任务"""
        mock_context.job.data = {"chat_id": 12345, "time_str": "23:30"}
        mock_context.bot.send_message = AsyncMock(side_effect=Exception("Network error"))
        mock_context.job.schedule_removal = mocker.MagicMock()

        await send_sleep_reminder(mock_context)

        mock_context.job.schedule_removal.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_reminder_failure_removes_user_from_dict(self, mock_context):
        """测试发送失败时从字典中移除用户"""
        chat_id = 12345
        mock_context.job.data = {"chat_id": chat_id, "time_str": "23:30"}
        mock_context.bot.send_message = AsyncMock(side_effect=Exception("Network error"))

        # 先添加用户到字典
        sleep_reminder_users[chat_id] = {"time": time(23, 30)}

        await send_sleep_reminder(mock_context)

        assert chat_id not in sleep_reminder_users


class TestSleepReminderUsers:
    """测试 sleep_reminder_users 全局字典"""

    def test_sleep_reminder_users_is_dict(self):
        """测试 sleep_reminder_users 是字典"""
        assert isinstance(sleep_reminder_users, dict)

    def test_can_add_user_to_reminder_list(self):
        """测试可以添加用户到提醒列表"""
        from bot.config import Config

        chat_id = 12345
        reminder_time = time(23, 30, tzinfo=Config.BEIJING_TZ)
        sleep_reminder_users[chat_id] = {"time": reminder_time}

        assert chat_id in sleep_reminder_users
        assert sleep_reminder_users[chat_id]["time"] == reminder_time

        # 清理
        del sleep_reminder_users[chat_id]

    def test_can_remove_user_from_reminder_list(self):
        """测试可以从提醒列表移除用户"""
        from bot.config import Config

        chat_id = 12345
        reminder_time = time(23, 30, tzinfo=Config.BEIJING_TZ)
        sleep_reminder_users[chat_id] = {"time": reminder_time}

        del sleep_reminder_users[chat_id]

        assert chat_id not in sleep_reminder_users
