"""Unit tests for memory.service — save, recall, forget, bundle."""
import pytest
from unittest.mock import MagicMock

from fixtures.users import TEST_USER_ID
from fixtures.memory import make_fact


class TestSaveMemory:
    def test_save_success(self, mock_bq_client):
        from memory.service import save_memory

        result = save_memory(
            user_id=TEST_USER_ID,
            category="preference",
            subject="workout.time",
            value="morning",
        )
        assert result["status"] == "success"
        assert result["subject"] == "workout.time"
        assert result["value"] == "morning"
        mock_bq_client.query.assert_called_once()
        sql = mock_bq_client.query.call_args[0][0]
        assert "MERGE" in sql

    def test_save_invalid_category_defaults_to_preference(self, mock_bq_client):
        from memory.service import save_memory

        result = save_memory(
            user_id=TEST_USER_ID,
            category="nonexistent_category",
            subject="test",
            value="val",
        )
        assert result["status"] == "success"
        job_config = mock_bq_client.query.call_args[1]["job_config"]
        params = {p.name: p.value for p in job_config.query_parameters}
        assert params["category"] == "preference"

    def test_save_bq_error_returns_error_dict(self, mock_bq_client):
        from memory.service import save_memory

        mock_bq_client.query.return_value.result.side_effect = Exception("BQ timeout")

        result = save_memory(
            user_id=TEST_USER_ID,
            category="preference",
            subject="test",
            value="val",
        )
        assert result["status"] == "error"
        assert "BQ timeout" in result["error_message"]


class TestRecallMemory:
    def test_recall_with_category_filter(self, mock_bq_client):
        from memory.service import recall_memory

        fact_data = make_fact()
        row = MagicMock()
        row.__getitem__ = lambda self, k: fact_data[k]
        mock_bq_client.query.return_value.result.return_value = [row]

        result = recall_memory(user_id=TEST_USER_ID, category="preference")
        assert result["status"] == "success"
        assert result["count"] == 1
        sql = mock_bq_client.query.call_args[0][0]
        assert "category = @category" in sql

    def test_recall_with_query_keyword(self, mock_bq_client):
        from memory.service import recall_memory

        mock_bq_client.query.return_value.result.return_value = []

        result = recall_memory(user_id=TEST_USER_ID, query="workout")
        assert result["status"] == "success"
        assert result["count"] == 0
        sql = mock_bq_client.query.call_args[0][0]
        assert "LOWER(subject) LIKE @q" in sql

    def test_recall_empty_returns_zero_count(self, mock_bq_client):
        from memory.service import recall_memory

        mock_bq_client.query.return_value.result.return_value = []

        result = recall_memory(user_id=TEST_USER_ID)
        assert result == {"status": "success", "facts": [], "count": 0}


class TestForgetMemory:
    def test_forget_success(self, mock_bq_client):
        from memory.service import forget_memory

        result = forget_memory(user_id=TEST_USER_ID, subject="workout.time")
        assert result["status"] == "success"
        assert result["subject"] == "workout.time"
        sql = mock_bq_client.query.call_args[0][0]
        assert "DELETE" in sql


class TestBuildBundle:
    def test_bundle_groups_by_category(self, mock_bq_client):
        from memory.service import build_bundle

        facts = [
            {"category": "preference", "subject": "time", "predicate": "prefers", "value": "morning", "confidence": 0.9},
            {"category": "goal", "subject": "reading", "predicate": "wants", "value": "24 books", "confidence": 0.8},
        ]
        rows = []
        for f in facts:
            row = MagicMock()
            row.__getitem__ = lambda self, k, f=f: f[k]
            rows.append(row)
        mock_bq_client.query.return_value.result.return_value = rows

        bundle = build_bundle(user_id=TEST_USER_ID)
        assert "<user_memory>" in bundle
        assert "[preference]" in bundle
        assert "[goal]" in bundle
        assert "time: morning" in bundle

    def test_bundle_truncates_at_max_chars(self, mock_bq_client):
        from memory.service import build_bundle, MAX_BUNDLE_CHARS

        long_facts = [
            {"category": "preference", "subject": f"key_{i}", "predicate": "is", "value": "x" * 200, "confidence": 0.9}
            for i in range(20)
        ]
        rows = []
        for f in long_facts:
            row = MagicMock()
            row.__getitem__ = lambda self, k, f=f: f[k]
            rows.append(row)
        mock_bq_client.query.return_value.result.return_value = rows

        bundle = build_bundle(user_id=TEST_USER_ID)
        assert len(bundle) <= MAX_BUNDLE_CHARS + 30

    def test_bundle_empty_when_no_facts(self, mock_bq_client):
        from memory.service import build_bundle

        mock_bq_client.query.return_value.result.return_value = []

        bundle = build_bundle(user_id=TEST_USER_ID)
        assert bundle == ""
