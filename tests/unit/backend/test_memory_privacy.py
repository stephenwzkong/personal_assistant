"""Privacy tests — user isolation, fact deletion, error message safety."""
from unittest.mock import MagicMock

import pytest

from fixtures.users import TEST_USER_ID, TEST_USER_ID_2


class TestUserIsolation:
    def test_recall_scoped_to_user_id(self, mock_bq_client):
        from memory.service import recall_memory

        mock_bq_client.query.return_value.result.return_value = []

        recall_memory(user_id=TEST_USER_ID, query="secrets")

        sql = mock_bq_client.query.call_args[0][0]
        assert "user_id = @user_id" in sql
        params = {p.name: p.value for p in mock_bq_client.query.call_args[1]["job_config"].query_parameters}
        assert params["user_id"] == TEST_USER_ID

    def test_forget_scoped_to_user_id(self, mock_bq_client):
        from memory.service import forget_memory

        forget_memory(user_id=TEST_USER_ID, subject="secret_fact")

        sql = mock_bq_client.query.call_args[0][0]
        assert "user_id = @user_id" in sql
        params = {p.name: p.value for p in mock_bq_client.query.call_args[1]["job_config"].query_parameters}
        assert params["user_id"] == TEST_USER_ID


class TestForgetActuallyDeletes:
    def test_issues_delete_not_soft_delete(self, mock_bq_client):
        from memory.service import forget_memory

        forget_memory(user_id=TEST_USER_ID, subject="old_fact")

        sql = mock_bq_client.query.call_args[0][0]
        assert sql.strip().startswith("DELETE")
        assert "status" not in sql.lower() or "cancelled" not in sql.lower()


class TestNoPiiInErrors:
    def test_bq_error_doesnt_leak_user_data(self, mock_bq_client):
        from memory.service import save_memory

        mock_bq_client.query.return_value.result.side_effect = Exception("connection reset")

        result = save_memory(
            user_id=TEST_USER_ID,
            category="preference",
            subject="secret.data",
            value="my_ssn_12345",
        )
        assert result["status"] == "error"
        assert "my_ssn_12345" not in result["error_message"]
        assert TEST_USER_ID not in result["error_message"]
