"""Vertex AI mock fixtures"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_chat_session():
    """Mock Vertex AI ChatSession 对象"""
    chat = MagicMock()
    chat.history = []

    # Mock streaming response
    mock_response = MagicMock()
    mock_response.text = "Hello! How can I help you?"

    # Mock send_message to return streaming iterator
    async def mock_send_generator():
        chunks = ["Hello! ", "How ", "can ", "I ", "help ", "you?"]
        for chunk in chunks:
            c = MagicMock()
            c.text = chunk
            yield c

    chat.send_message = MagicMock(return_value=mock_send_generator())

    return chat


@pytest.fixture
def mock_generative_model(mock_chat_session):
    """Mock GenerativeModel"""
    model = MagicMock()
    model._model_name = "gemini-2.5-flash"
    model.start_chat = MagicMock(return_value=mock_chat_session)
    return model


@pytest.fixture
def mock_vertexai_init(mocker):
    """Mock vertexai.init"""
    return mocker.patch('vertexai.init')


@pytest.fixture
def mock_generative_model_class(mocker, mock_generative_model):
    """Mock GenerativeModel class"""
    return mocker.patch('vertexai.generative_models.GenerativeModel', return_value=mock_generative_model)


@pytest.fixture
def mock_stream_response():
    """Mock streaming response from Vertex AI"""
    async def generate_chunks():
        chunks = ["This ", "is ", "a ", "test ", "response."]
        for chunk in chunks:
            c = MagicMock()
            c.text = chunk
            yield c

    return generate_chunks()
