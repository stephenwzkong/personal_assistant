"""Unit tests for tools.shared.memory_tools — ADK tool wrappers."""
from unittest.mock import MagicMock, patch

import pytest


class TestResolveUserId:
    def test_returns_user_id_from_context(self):
        from tools.shared.memory_tools import _resolve_user_id

        ctx = MagicMock()
        ctx._invocation_context.user_id = "real_user"

        assert _resolve_user_id(ctx) == "real_user"

    def test_returns_default_when_no_context(self):
        from tools.shared.memory_tools import _resolve_user_id

        assert _resolve_user_id(None) == "default_user"

    def test_returns_default_when_user_id_missing(self):
        from tools.shared.memory_tools import _resolve_user_id

        ctx = MagicMock()
        ctx._invocation_context = MagicMock(spec=[])  # no user_id attribute

        assert _resolve_user_id(ctx) == "default_user"


class TestSaveMemoryTool:
    def test_delegates_to_service(self):
        from tools.shared.memory_tools import save_memory

        ctx = MagicMock()
        ctx._invocation_context.user_id = "tool_user"
        ctx._invocation_context.session = MagicMock(id="sess-123")

        with patch("memory.service.save_memory", return_value={"status": "success", "subject": "k", "value": "v"}) as mock_svc:
            result = save_memory("preference", "k", "v", 0.9, ctx)

        mock_svc.assert_called_once_with(
            user_id="tool_user",
            category="preference",
            subject="k",
            value="v",
            confidence=0.9,
            source_session="sess-123",
        )
        assert result["status"] == "success"


class TestRecallMemoryTool:
    def test_passes_filters_to_service(self):
        from tools.shared.memory_tools import recall_memory

        ctx = MagicMock()
        ctx._invocation_context.user_id = "tool_user"

        with patch("memory.service.recall_memory", return_value={"status": "success", "facts": [], "count": 0}) as mock_svc:
            result = recall_memory("workout", "preference", 5, ctx)

        mock_svc.assert_called_once_with(
            user_id="tool_user",
            query="workout",
            category="preference",
            limit=5,
        )

    def test_empty_strings_become_none(self):
        from tools.shared.memory_tools import recall_memory

        ctx = MagicMock()
        ctx._invocation_context.user_id = "u"

        with patch("memory.service.recall_memory", return_value={"status": "success", "facts": [], "count": 0}) as mock_svc:
            recall_memory("", "", 10, ctx)

        mock_svc.assert_called_once_with(user_id="u", query=None, category=None, limit=10)


class TestForgetMemoryTool:
    def test_delegates_to_service(self):
        from tools.shared.memory_tools import forget_memory

        ctx = MagicMock()
        ctx._invocation_context.user_id = "tool_user"

        with patch("memory.service.forget_memory", return_value={"status": "success", "subject": "k"}) as mock_svc:
            result = forget_memory("k", ctx)

        mock_svc.assert_called_once_with(user_id="tool_user", subject="k")
        assert result["status"] == "success"
