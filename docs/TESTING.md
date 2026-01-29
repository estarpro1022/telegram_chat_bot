# 测试文档

本文档介绍 Telegram AI Bot 项目的测试策略、运行方法和编写指南。

## 目录

- [测试概览](#测试概览)
- [快速开始](#快速开始)
- [测试框架](#测试框架)
- [测试结构](#测试结构)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [Mock 策略](#mock-策略)
- [覆盖率报告](#覆盖率报告)
- [CI/CD 集成](#cicd-集成)

---

## 测试概览

### 当前状态

- **总测试数**: 75
- **通过率**: 100%
- **代码覆盖率**: 88.96%
- **目标覆盖率**: 80%

### 覆盖率详情

| 模块 | 语句数 | 覆盖率 |
|------|--------|--------|
| bot/__init__.py | 3 | 100% |
| bot/handlers/__init__.py | 4 | 100% |
| bot/handlers/base.py | 11 | 100% |
| bot/handlers/chat.py | 18 | 100% |
| bot/handlers/sleep.py | 47 | 100% |
| bot/services/__init__.py | 3 | 100% |
| bot/services/ai.py | 14 | 100% |
| bot/services/reminder.py | 28 | 100% |
| bot/config.py | 19 | 89.47% |
| bot/__main__.py | 16 | 0% |
| **总计** | **163** | **88.96%** |

---

## 快速开始

### 安装依赖

```bash
# 安装开发依赖
uv sync --all-extras
```

### 运行所有测试

```bash
uv run pytest
```

### 查看覆盖率

```bash
uv run pytest --cov=bot --cov-report=html
# 在浏览器中打开 htmlcov/index.html
```

---

## 测试框架

项目使用 **pytest** 作为主要测试框架，配合以下插件：

| 插件 | 版本 | 用途 |
|------|------|------|
| pytest | >=8.0.0 | 测试运行器 |
| pytest-asyncio | >=0.23.0 | 异步测试支持 |
| pytest-cov | >=4.1.0 | 覆盖率报告 |
| pytest-mock | >=3.12.0 | Mock 对象 |

### 为什么选择 pytest？

1. **异步支持**: pytest-asyncio 提供优秀的 async/await 测试能力
2. **Fixture 系统**: 强大且灵活的 fixture 机制
3. **简洁语法**: 比 unittest 更少的样板代码
4. **插件生态**: 丰富的插件支持
5. **社区标准**: 现代 Python 测试的最佳实践

---

## 测试结构

```
tests/
├── __init__.py
├── conftest.py                   # 共享 fixtures 和全局配置
├── fixtures/                     # 可重用的 mock fixtures
│   ├── __init__.py
│   ├── telegram.py               # Telegram Bot API mocks
│   └── vertex.py                 # Vertex AI mocks
├── unit/                         # 单元测试
│   ├── __init__.py
│   ├── test_config.py            # 配置模块测试 (10 tests)
│   ├── test_handlers/            # 处理器测试
│   │   ├── __init__.py
│   │   ├── test_base.py          # start/help 命令 (7 tests)
│   │   ├── test_chat.py          # AI 聊天处理 (7 tests)
│   │   └── test_sleep.py         # 睡眠提醒命令 (15 tests)
│   └── test_services/            # 服务层测试
│       ├── __init__.py
│       ├── test_ai.py            # AI 服务 (9 tests)
│       └── test_reminder.py      # 提醒服务 (22 tests)
└── integration/                  # 集成测试
    ├── __init__.py
    └── test_bot_integration.py   # Bot 集成测试 (5 tests)
```

### 测试类型说明

- **单元测试**: 测试单个函数或类的行为
- **集成测试**: 测试多个模块协同工作
- **异步测试**: 使用 `@pytest.mark.asyncio` 装饰器

---

## 运行测试

### 基本命令

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/unit/test_config.py

# 运行特定测试类
uv run pytest tests/unit/test_handlers/test_base.py::TestStartCommand

# 运行特定测试函数
uv run pytest tests/unit/test_config.py::TestConfig::test_telegram_token_from_env
```

### 使用标记

```bash
# 只运行单元测试
uv run pytest -m unit

# 只运行集成测试
uv run pytest -m integration

# 排除慢速测试
uv run pytest -m "not slow"
```

### 详细输出

```bash
# 显示详细输出
uv run pytest -v

# 显示更详细的输出（包括 print 内容）
uv run pytest -vv -s

# 只显示失败的测试详情
uv run pytest --tb=short
```

### 并行运行（需要安装 pytest-xdist）

```bash
# 使用多个 CPU 核心并行运行
uv run pytest -n auto
```

---

## 编写测试

### 测试命名规范

- **文件名**: `test_*.py` (例如 `test_config.py`)
- **类名**: `Test*` (例如 `TestConfig`)
- **函数名**: `test_*` (例如 `test_validate_with_all_required_config`)

### 基本测试结构

```python
"""模块说明"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from bot.module import function_to_test


class TestFunctionToTest:
    """测试 function_to_test 函数"""

    def test_success_case(self, mock_update, mock_context):
        """测试成功情况"""
        # Arrange（准备）
        input_data = "test input"

        # Act（执行）
        result = function_to_test(input_data)

        # Assert（断言）
        assert result == "expected output"

    @pytest.mark.asyncio
    async def test_async_function(self, mock_update, mock_context):
        """测试异步函数"""
        result = await async_function_to_test()
        assert result is not None
```

### 异步测试

所有异步测试函数必须使用 `@pytest.mark.asyncio` 装饰器：

```python
@pytest.mark.asyncio
async def test_async_handler(self, mock_update, mock_context):
    """测试异步处理器"""
    await some_async_function(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
```

### 使用 Fixtures

从共享 fixtures 导入：

```python
def test_with_fixtures(self, mock_update, mock_context):
    """使用预定义的 fixtures"""
    # mock_update 和 mock_context 自动注入
    mock_update.effective_user.id = 12345
    mock_update.message.text = "Hello"

    await some_handler(mock_update, mock_context)
```

可用的 fixtures（定义在 `tests/fixtures/` 目录）：

**Telegram Fixtures** (`tests/fixtures/telegram.py`):
- `mock_user` - Mock User 对象
- `mock_chat` - Mock Chat 对象
- `mock_message` - Mock Message 对象
- `mock_update` - Mock Update 对象
- `mock_context` - Mock Context 对象
- `mock_job` - Mock Job 对象

**Vertex AI Fixtures** (`tests/fixtures/vertex.py`):
- `mock_vertexai_init` - Mock Vertex AI 初始化
- `mock_generative_model` - Mock GenerativeModel
- `mock_chat_session` - Mock 聊天会话
- `mock_stream_response` - Mock 流式响应

### 创建自定义 Fixture

```python
@pytest.fixture
def custom_data():
    """自定义 fixture"""
    return {"key": "value"}

def test_with_custom_fixture(self, custom_data):
    """使用自定义 fixture"""
    assert custom_data["key"] == "value"
```

---

## Mock 策略

### 原则

1. **外部 API 必须 mock**：Vertex AI、Telegram Bot API
2. **使用共享 fixtures**：避免重复创建 mock 对象
3. **不要连接真实服务**：测试不应调用实际的外部 API

### Mocking Telegram 对象

```python
from unittest.mock import AsyncMock

# 创建 mock 对象
mock_update = MagicMock()
mock_update.effective_user.id = 12345
mock_update.message.reply_text = AsyncMock()

# 验证调用
mock_update.message.reply_text.assert_called_with("Expected message")
```

### Mocking Vertex AI

```python
import pytest
from unittest.mock import MagicMock

def test_ai_service(self, mocker):
    """测试 AI 服务"""
    # Mock Vertex AI 初始化
    mock_vertex = mocker.patch('vertexai.init')

    # Mock GenerativeModel
    mock_model = mocker.patch('vertexai.generative_models.GenerativeModel')

    # 验证 mock 被调用
    mock_vertex.assert_called_once()
```

### Mocking 异步函数

```python
@pytest.mark.asyncio
async def test_async_function(self, mocker):
    """测试异步函数"""
    # Mock 异步函数
    mock_async_func = mocker.patch('bot.module.async_function', new_callable=AsyncMock)

    # 调用异步函数
    await async_function()

    # 验证
    mock_async_func.assert_called_once()
```

---

## 覆盖率报告

### 生成报告

```bash
# 终端输出（简洁）
uv run pytest --cov=bot --cov-report=term

# 终端输出（显示未覆盖行）
uv run pytest --cov=bot --cov-report=term-missing

# HTML 报告
uv run pytest --cov=bot --cov-report=html
# 打开 htmlcov/index.html

# XML 报告（用于 CI）
uv run pytest --cov=bot --cov-report=xml
```

### 覆盖率配置

覆盖率配置在 [pyproject.toml](../pyproject.toml) 中：

```toml
[tool.coverage.run]
source = ["bot"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.venv/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### 排除代码

使用注释排除特定行：

```python
def some_function():  # pragma: no cover
    # 这行代码不会被计入覆盖率
    pass
```

---

## CI/CD 集成

### GitHub Actions

测试在 GitHub Actions CI 中自动运行。查看配置文件：

[`.github/workflows/ci.yml`](.github/workflows/ci.yml)

### 本地预览 CI

```bash
# 运行与 CI 相同的测试命令
uv run pytest --cov=bot --cov-report=xml --cov-report=term-missing
```

---

## 常见问题

### Q: 测试失败怎么办？

```bash
# 只运行失败的测试
uv run pytest --lf

# 先运行失败的，再运行其他的
uv run pytest --ff

# 在调试模式下运行（进入 pdb）
uv run pytest --pdb
```

### Q: 如何调试单个测试？

```bash
# 打印输出
uv run pytest -s tests/unit/test_config.py::TestConfig::test_validate

# 使用 pdb 调试
uv run pytest --pdb tests/unit/test_config.py::TestConfig::test_validate
```

### Q: 异步测试报错怎么办？

确保：
1. 使用 `@pytest.mark.asyncio` 装饰器
2. `asyncio_mode = "auto"` 在 conftest.py 中配置
3. 异步函数使用 `async def` 定义

### Q: Mock 不生效？

检查：
1. Mock 的路径是否正确（使用实际的导入路径）
2. 是否在正确的位置进行 patch
3. 是否有其他代码重新导入模块

---

## 最佳实践

1. **AAA 模式**: Arrange（准备）→ Act（执行）→ Assert（断言）
2. **独立性**: 每个测试应该独立运行，不依赖其他测试
3. **描述性名称**: 测试名称应该清楚描述测试内容
4. **一个断言**: 每个测试只验证一个行为
5. **Mock 边界**: Mock 外部依赖，不要 mock 内部逻辑
6. **测试异常**: 测试错误处理路径
7. **清理状态**: 使用 fixtures 清理测试状态

---

## 参考资料

- [Pytest 官方文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [python-telegram-bot 测试指南](https://docs.python-telegram-bot.org/en/stable/tests.html)
- [项目测试覆盖率报告](../htmlcov/index.html)
