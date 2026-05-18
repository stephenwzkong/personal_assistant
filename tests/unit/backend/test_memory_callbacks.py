"""Unit tests for memory.callbacks — inject_memory_bundle and caching."""
import time
from unittest.mock import MagicMock, patch

import pytest


class TestInjectMemoryBundle:
    def test_inject_sets_state(self):
        from memory.callbacks import inject_memory_bundle

        ctx = MagicMock()
        ctx._invocation_context.user_id = "test_user"
        ctx.state = {}

        with patch("memory.callbacks._get_bundle", return_value="<user_memory>\n  [preference]\n    - time: morning\n</user_memory>"):
            result = inject_memory_bundle(ctx)

        assert result is None
        assert "user_memory" in ctx.state["user_memory_block"]

    def test_inject_fallback_user(self):
        from memory.callbacks import inject_memory_bundle

        ctx = MagicMock()
        ctx._invocation_context = None
        ctx.state = {}

        with patch("memory.callbacks._get_bundle", return_value="") as mock_get:
            inject_memory_bundle(ctx)

        mock_get.assert_called_once_with("default_user")


class TestBundleCache:
    def test_cache_hit_within_ttl(self):
        from memory.callbacks import _get_bundle, _BUNDLE_CACHE, _CACHE_TTL_SECONDS

        _BUNDLE_CACHE.clear()
        _BUNDLE_CACHE["cached_user"] = ("cached_bundle", time.time())

        with patch("memory.service.build_bundle") as mock_build:
            result = _get_bundle("cached_user")

        assert result == "cached_bundle"
        mock_build.assert_not_called()

    def test_cache_miss_after_ttl(self):
        from memory.callbacks import _get_bundle, _BUNDLE_CACHE, _CACHE_TTL_SECONDS

        _BUNDLE_CACHE.clear()
        _BUNDLE_CACHE["stale_user"] = ("old_bundle", time.time() - _CACHE_TTL_SECONDS - 1)

        with patch("memory.service.build_bundle", return_value="fresh_bundle") as mock_build:
            result = _get_bundle("stale_user")

        assert result == "fresh_bundle"
        mock_build.assert_called_once_with(user_id="stale_user")

    def test_invalidate_clears_cache(self):
        from memory.callbacks import invalidate_bundle, _BUNDLE_CACHE

        _BUNDLE_CACHE["to_clear"] = ("data", time.time())
        invalidate_bundle("to_clear")
        assert "to_clear" not in _BUNDLE_CACHE

    def teardown_method(self):
        from memory.callbacks import _BUNDLE_CACHE
        _BUNDLE_CACHE.clear()
