"""Vertex AI 服务"""
import logging
import vertexai
from vertexai.generative_models import GenerativeModel

from bot.config import Config

# 初始化 Vertex AI
vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)
model = GenerativeModel("gemini-2.5-flash")

# 用户聊天会话存储: {user_id: ChatSession}
user_chats = {}


def get_user_chat(user_id):
    """获取或创建用户聊天会话"""
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]


def reset_user_chat(user_id):
    """重置用户聊天会话"""
    user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]
