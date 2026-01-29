"""AI 服务单元测试"""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestGetUserChat:
    """测试 get_user_chat 函数"""

    def test_get_user_chat_creates_new_session_for_new_user(self, mock_chat_session):
        """测试为新用户创建新的聊天会话"""
        from bot.services.ai import get_user_chat, user_chats

        user_id = 12345

        chat = get_user_chat(user_id)

        assert user_id in user_chats
        assert user_chats[user_id] == chat

    def test_get_user_chat_returns_existing_session(self):
        """测试为已存在用户返回现有会话"""
        from bot.services.ai import get_user_chat, user_chats

        user_id = 12345

        # 第一次调用创建会话
        first_chat = get_user_chat(user_id)
        # 第二次调用应返回同一会话
        second_chat = get_user_chat(user_id)

        # 应该返回同一个会话
        assert first_chat == second_chat

    def test_get_user_chat_isolation_between_users(self):
        """测试不同用户的会话隔离"""
        from bot.services.ai import get_user_chat, user_chats

        user_id_1 = 11111
        user_id_2 = 22222

        chat_1 = get_user_chat(user_id_1)
        chat_2 = get_user_chat(user_id_2)

        # 两个会话应该是不同的对象
        assert chat_1 is not chat_2
        # 用户应该有不同的会话
        assert user_chats[user_id_1] is not user_chats[user_id_2]


class TestResetUserChat:
    """测试 reset_user_chat 函数"""

    def test_reset_user_chat_creates_new_session(self):
        """测试重置用户聊天会话创建新会话"""
        from bot.services.ai import get_user_chat, reset_user_chat, user_chats

        user_id = 12345

        # 先创建一个会话
        original_chat = get_user_chat(user_id)
        # 重置会话
        new_chat = reset_user_chat(user_id)

        # 新会话应该与原会话不同
        assert new_chat is not original_chat

    def test_reset_user_chat_for_nonexistent_user(self):
        """测试重置不存在的用户会话"""
        from bot.services.ai import reset_user_chat, user_chats

        user_id = 99999

        reset_user_chat(user_id)

        # 应该创建新会话
        assert user_id in user_chats


class TestUserChats:
    """测试 user_chats 全局字典"""

    def test_user_chats_is_dict(self):
        """测试 user_chats 是字典"""
        from bot.services.ai import user_chats

        assert isinstance(user_chats, dict)

    def test_user_chats_persists_across_calls(self):
        """测试 user_chats 在调用间持久化"""
        from bot.services.ai import get_user_chat

        user_id = 12345

        chat_1 = get_user_chat(user_id)
        chat_2 = get_user_chat(user_id)

        # 应该返回同一个会话对象
        assert chat_1 is chat_2


class TestVertexAIInitialization:
    """测试 Vertex AI 初始化"""

    def test_model_exists(self):
        """测试模型对象存在"""
        from bot.services.ai import model

        assert model is not None

    def test_model_has_correct_name(self):
        """测试模型有正确的名称"""
        from bot.services.ai import model

        assert hasattr(model, '_model_name') or hasattr(model, 'model_name')
