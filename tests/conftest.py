"""Shared test fixtures — BigQuery and Firestore mocks."""
import sys
import os
from unittest.mock import MagicMock

import pytest
import pandas as pd

_assistant_root = os.path.join(os.path.dirname(__file__), "..", "src", "assistant")
sys.path.insert(0, os.path.abspath(_assistant_root))


@pytest.fixture
def mock_bq_client(mocker):
    """Mock google.cloud.bigquery.Client used across all BQ-dependent modules."""
    mock = mocker.patch("google.cloud.bigquery.Client")
    client = mock.return_value
    query_job = MagicMock()
    query_job.result.return_value = iter([])
    query_job.to_dataframe.return_value = pd.DataFrame()
    client.query.return_value = query_job
    client.insert_rows_json.return_value = []
    return client


@pytest.fixture
def mock_firestore_client(mocker):
    """Mock google.cloud.firestore.Client for session service tests."""
    mock = mocker.patch("google.cloud.firestore.Client")
    client = mock.return_value
    doc_snap = MagicMock()
    doc_snap.exists = False
    doc_snap.to_dict.return_value = None
    collection_ref = MagicMock()
    collection_ref.document.return_value.get.return_value = doc_snap
    collection_ref.document.return_value.set.return_value = None
    collection_ref.where.return_value.stream.return_value = iter([])
    client.collection.return_value = collection_ref
    return client


@pytest.fixture
def app_client():
    """FastAPI TestClient using httpx for async support."""
    from api.main import app
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
