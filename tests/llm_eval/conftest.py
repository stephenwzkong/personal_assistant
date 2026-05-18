"""Shared fixtures for LLM evaluation tests.

These tests call live Gemini API — run manually with:
  pytest tests/llm_eval/ -m llm -v
"""
import os
import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        if "llm_eval" in str(item.fspath):
            item.add_marker(pytest.mark.llm)


@pytest.fixture(scope="session")
def require_api_key():
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        pytest.skip("GOOGLE_API_KEY not set — skipping LLM eval tests")
    return key
