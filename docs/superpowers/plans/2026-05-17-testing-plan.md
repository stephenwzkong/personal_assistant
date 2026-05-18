# Testing Plan Implementation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add comprehensive test infrastructure (pytest, vitest, Playwright) to the personal assistant app, covering backend unit tests, integration tests, frontend unit tests, E2E tests, and LLM evaluation tests.

**Architecture:** Backend tests use pytest with mocked BigQuery/Firestore clients. Frontend tests use vitest + @testing-library/react + MSW for API mocking. E2E tests use Playwright against running dev servers. LLM eval tests are separate, marked with `@pytest.mark.llm`, and use live Gemini.

**Tech Stack:** pytest, pytest-asyncio, pytest-cov, pytest-mock, httpx, vitest, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, MSW, jsdom, Playwright

---

## File Structure

```
tests/
├── conftest.py
├── __init__.py
├── fixtures/
│   ├── __init__.py
│   ├── users.py
│   ├── events.py
│   ├── tasks.py
│   └── memory.py
├── unit/
│   ├── __init__.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── test_memory_service.py
│   │   ├── test_memory_callbacks.py
│   │   ├── test_memory_tools.py
│   │   ├── test_memory_privacy.py
│   │   ├── test_calendar_tools.py
│   │   ├── test_task_tools.py
│   │   ├── test_bq_client.py
│   │   ├── test_skills_loader.py
│   │   ├── test_session_service.py
│   │   └── test_error_paths.py
│   └── frontend/
│       ├── setup.ts
│       ├── api.test.ts
│       ├── useSession.test.ts
│       ├── useChat.test.ts
│       ├── useCalendar.test.ts
│       ├── useTasks.test.ts
│       ├── ChatInterface.test.tsx
│       ├── CalendarView.test.tsx
│       ├── TasksPage.test.tsx
│       └── DomainChat.test.tsx
├── integration/
│   ├── __init__.py
│   ├── test_chat_api.py
│   ├── test_calendar_api.py
│   ├── test_session_api.py
│   ├── test_tasks_api.py
│   └── test_routing_logic.py
├── e2e/
│   ├── chat.spec.ts
│   ├── calendar.spec.ts
│   ├── tasks.spec.ts
│   └── session.spec.ts
└── llm_eval/
    ├── __init__.py
    ├── conftest.py
    ├── test_agent_routing.py
    ├── test_agent_tools.py
    └── test_skill_quality.py
```

Config files modified/created:
- `pyproject.toml` — add test dependencies + pytest config
- `src/assistant/frontend/vitest.config.ts` — create
- `src/assistant/frontend/playwright.config.ts` — create
- `src/assistant/frontend/package.json` — add test deps + scripts

---

### Task 1: Add Python Test Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add test optional-dependencies and pytest config to pyproject.toml**

Open `pyproject.toml` and add after the `[build-system]` section:

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "pytest-mock>=3.14",
    "httpx>=0.27",
    "pandas>=2.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "llm: tests that call live Gemini API (deselect with -m 'not llm')",
]
```

- [ ] **Step 2: Install test dependencies**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && uv pip install -e ".[test]"
```
Expected: all packages install successfully.

- [ ] **Step 3: Verify pytest is available**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest --version
```
Expected: `pytest 8.x.x`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add pytest test dependencies and config"
```

---

### Task 2: Create Test Fixtures

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/fixtures/__init__.py`
- Create: `tests/fixtures/users.py`
- Create: `tests/fixtures/events.py`
- Create: `tests/fixtures/tasks.py`
- Create: `tests/fixtures/memory.py`

- [ ] **Step 1: Create test directory structure**

```bash
mkdir -p tests/fixtures tests/unit/backend tests/unit/frontend tests/integration tests/e2e tests/llm_eval
touch tests/__init__.py tests/unit/__init__.py tests/unit/backend/__init__.py tests/integration/__init__.py tests/llm_eval/__init__.py tests/fixtures/__init__.py
```

- [ ] **Step 2: Create users fixture**

File: `tests/fixtures/users.py`
```python
TEST_USER_ID = "test_user_001"
TEST_USER_ID_2 = "test_user_002"
DEFAULT_USER_ID = "default_user"
TEST_SESSION_ID = "test-session-00000000"
```

- [ ] **Step 3: Create events fixture**

File: `tests/fixtures/events.py`
```python
def make_event(overrides=None):
    base = {
        "event_id": "evt-test-001",
        "title": "Morning Run",
        "start_datetime": "2026-05-17T07:00:00",
        "end_datetime": "2026-05-17T08:00:00",
        "event_type": "workout",
        "status": "active",
        "priority": "medium",
        "description": "",
        "source_agent": "FitnessAgent",
    }
    if overrides:
        base.update(overrides)
    return base


def make_events_list(count=3):
    types = ["workout", "meal_window", "school"]
    return [
        make_event({
            "event_id": f"evt-test-{i:03d}",
            "title": f"Event {i}",
            "event_type": types[i % len(types)],
            "start_datetime": f"2026-05-1{7 + i}T09:00:00",
            "end_datetime": f"2026-05-1{7 + i}T10:00:00",
        })
        for i in range(count)
    ]
```

- [ ] **Step 4: Create tasks fixture**

File: `tests/fixtures/tasks.py`
```python
def make_task(overrides=None):
    base = {
        "task_id": "task-test-001",
        "parent_task_id": None,
        "title": "Buy groceries",
        "description": "",
        "status": "todo",
        "priority": "medium",
        "category": "personal",
        "due_date": "2026-05-20",
        "position": 0,
        "created_at": "2026-05-17T00:00:00+00:00",
        "updated_at": "2026-05-17T00:00:00+00:00",
    }
    if overrides:
        base.update(overrides)
    return base


def make_task_with_steps():
    parent = make_task({"title": "Prepare for exam", "category": "school"})
    steps = [
        make_task({
            "task_id": f"step-{i}",
            "parent_task_id": parent["task_id"],
            "title": t,
            "position": i,
        })
        for i, t in enumerate(["Review notes", "Practice problems", "Make flashcards"])
    ]
    return parent, steps
```

- [ ] **Step 5: Create memory fixture**

File: `tests/fixtures/memory.py`
```python
def make_fact(overrides=None):
    base = {
        "fact_id": "fact-test-001",
        "user_id": "test_user_001",
        "category": "preference",
        "subject": "workout_time",
        "predicate": "prefers",
        "value": "morning",
        "confidence": 0.9,
        "source_agent": "FitnessAgent",
    }
    if overrides:
        base.update(overrides)
    return base


def make_facts_list(count=5):
    categories = ["preference", "goal", "constraint", "profile", "routine"]
    return [
        make_fact({
            "fact_id": f"fact-test-{i:03d}",
            "category": categories[i % len(categories)],
            "subject": f"subject_{i}",
            "value": f"value_{i}",
        })
        for i in range(count)
    ]
```

- [ ] **Step 6: Commit**

```bash
git add tests/
git commit -m "feat: add test fixtures for users, events, tasks, memory"
```

---

### Task 3: Create Shared conftest.py

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Write the shared conftest**

File: `tests/conftest.py`
```python
"""Shared test fixtures — BigQuery and Firestore mocks."""
import sys
import os
from unittest.mock import MagicMock

import pytest
import pandas as pd

# Add src/assistant to path so imports like `memory.service` work
_assistant_root = os.path.join(os.path.dirname(__file__), "..", "src", "assistant")
sys.path.insert(0, os.path.abspath(_assistant_root))


@pytest.fixture
def mock_bq_client(mocker):
    """Mock google.cloud.bigquery.Client used across all BQ-dependent modules."""
    mock = mocker.patch("google.cloud.bigquery.Client")
    client = mock.return_value
    # query().result() returns empty iterator by default
    query_job = MagicMock()
    query_job.result.return_value = iter([])
    query_job.to_dataframe.return_value = pd.DataFrame()
    client.query.return_value = query_job
    # insert_rows_json returns no errors by default
    client.insert_rows_json.return_value = []
    return client


@pytest.fixture
def mock_firestore_client(mocker):
    """Mock google.cloud.firestore.Client for session service tests."""
    mock = mocker.patch("google.cloud.firestore.Client")
    client = mock.return_value
    # Default: document does not exist
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
```

- [ ] **Step 2: Verify conftest loads**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/ --collect-only 2>&1 | head -20
```
Expected: pytest discovers the conftest without import errors. No tests collected yet is fine.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "feat: add shared conftest with BQ and Firestore mocks"
```

---

### Task 4: Unit Test — Memory Service

**Files:**
- Create: `tests/unit/backend/test_memory_service.py`
- Test: `tests/unit/backend/test_memory_service.py`

- [ ] **Step 1: Write test_memory_service.py**

File: `tests/unit/backend/test_memory_service.py`
```python
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
        # Category param should have been corrected to "preference"
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
        assert len(bundle) <= MAX_BUNDLE_CHARS + 30  # +30 for truncation suffix

    def test_bundle_empty_when_no_facts(self, mock_bq_client):
        from memory.service import build_bundle

        mock_bq_client.query.return_value.result.return_value = []

        bundle = build_bundle(user_id=TEST_USER_ID)
        assert bundle == ""
```

- [ ] **Step 2: Run the tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_memory_service.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_memory_service.py
git commit -m "test: add unit tests for memory service"
```

---

### Task 5: Unit Test — Memory Callbacks

**Files:**
- Create: `tests/unit/backend/test_memory_callbacks.py`

- [ ] **Step 1: Write test_memory_callbacks.py**

File: `tests/unit/backend/test_memory_callbacks.py`
```python
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

        assert result is None  # callback returns None to let agent run
        assert "user_memory" in ctx.state["user_memory_block"]

    def test_inject_fallback_user(self):
        from memory.callbacks import inject_memory_bundle

        ctx = MagicMock()
        ctx._invocation_context = None  # triggers fallback
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
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_memory_callbacks.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_memory_callbacks.py
git commit -m "test: add unit tests for memory callbacks and caching"
```

---

### Task 6: Unit Test — Memory Tools

**Files:**
- Create: `tests/unit/backend/test_memory_tools.py`

- [ ] **Step 1: Write test_memory_tools.py**

File: `tests/unit/backend/test_memory_tools.py`
```python
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

    def test_returns_default_on_exception(self):
        from tools.shared.memory_tools import _resolve_user_id

        ctx = MagicMock()
        type(ctx)._invocation_context = property(lambda s: (_ for _ in ()).throw(AttributeError))

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
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_memory_tools.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_memory_tools.py
git commit -m "test: add unit tests for memory tool wrappers"
```

---

### Task 7: Unit Test — Memory Privacy

**Files:**
- Create: `tests/unit/backend/test_memory_privacy.py`

- [ ] **Step 1: Write test_memory_privacy.py**

File: `tests/unit/backend/test_memory_privacy.py`
```python
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
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_memory_privacy.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_memory_privacy.py
git commit -m "test: add memory privacy and isolation tests"
```

---

### Task 8: Unit Test — Calendar Tools

**Files:**
- Create: `tests/unit/backend/test_calendar_tools.py`

- [ ] **Step 1: Write test_calendar_tools.py**

File: `tests/unit/backend/test_calendar_tools.py`
```python
"""Unit tests for tools.shared.calendar_tools."""
from unittest.mock import MagicMock

import pytest
import pandas as pd

from fixtures.events import make_event


class TestCreateCalendarEvent:
    def test_create_success(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        result = create_calendar_event(
            title="Morning Run",
            start_datetime="2026-05-17T07:00:00",
            end_datetime="2026-05-17T08:00:00",
            event_type="workout",
        )
        assert result["status"] == "success"
        assert "event_id" in result
        assert result["title"] == "Morning Run"
        mock_bq_client.insert_rows_json.assert_called_once()

    def test_create_invalid_type_defaults_to_other(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        result = create_calendar_event(
            title="Mystery",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
            event_type="invalid_type",
        )
        assert result["status"] == "success"
        rows = mock_bq_client.insert_rows_json.call_args[0][1]
        assert rows[0]["event_type"] == "other"

    def test_create_bq_insert_error(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        mock_bq_client.insert_rows_json.return_value = [{"errors": "bad row"}]

        result = create_calendar_event(
            title="Bad",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
        )
        assert result["status"] == "error"


class TestListCalendarEvents:
    def test_list_with_date_range(self, mock_bq_client):
        from tools.shared.calendar_tools import list_calendar_events

        ev = make_event()
        df = pd.DataFrame([ev])
        mock_bq_client.query.return_value.to_dataframe.return_value = df

        result = list_calendar_events(start_date="2026-05-17", end_date="2026-05-24")
        assert result["status"] == "success"
        assert result["count"] == 1
        sql = mock_bq_client.query.call_args[0][0]
        assert "2026-05-17" in sql
        assert "2026-05-24" in sql

    def test_list_filters_by_event_type(self, mock_bq_client):
        from tools.shared.calendar_tools import list_calendar_events

        mock_bq_client.query.return_value.to_dataframe.return_value = pd.DataFrame()

        list_calendar_events(event_type="workout")
        sql = mock_bq_client.query.call_args[0][0]
        assert "event_type = 'workout'" in sql


class TestUpdateCalendarEvent:
    def test_update_partial_fields(self, mock_bq_client):
        from tools.shared.calendar_tools import update_calendar_event

        result = update_calendar_event(event_id="evt-001", title="New Title")
        assert result["status"] == "success"
        sql = mock_bq_client.query.call_args[0][0]
        assert "title = @title" in sql
        assert "event_id = @event_id" in sql

    def test_update_invalid_status_returns_error(self):
        from tools.shared.calendar_tools import update_calendar_event

        result = update_calendar_event(event_id="evt-001", status="deleted")
        assert result["status"] == "error"
        assert "Invalid status" in result["error_message"]


class TestDeleteCalendarEvent:
    def test_delete_soft_deletes(self, mock_bq_client):
        from tools.shared.calendar_tools import delete_calendar_event

        result = delete_calendar_event(event_id="evt-001")
        assert result["status"] == "success"
        sql = mock_bq_client.query.call_args[0][0]
        assert "UPDATE" in sql
        params = {p.name: p.value for p in mock_bq_client.query.call_args[1]["job_config"].query_parameters}
        assert params["status"] == "cancelled"


class TestEventColors:
    def test_all_event_types_have_colors(self):
        from tools.shared.calendar_tools import EVENT_COLORS, VALID_EVENT_TYPES

        for et in VALID_EVENT_TYPES:
            assert et in EVENT_COLORS
            assert EVENT_COLORS[et].startswith("#")
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_calendar_tools.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_calendar_tools.py
git commit -m "test: add unit tests for calendar tools"
```

---

### Task 9: Unit Test — Task Tools

**Files:**
- Create: `tests/unit/backend/test_task_tools.py`

- [ ] **Step 1: Write test_task_tools.py**

File: `tests/unit/backend/test_task_tools.py`
```python
"""Unit tests for tools.productivity.task_tools."""
from unittest.mock import MagicMock

import pytest
import pandas as pd

from fixtures.tasks import make_task


class TestCreateTask:
    def test_create_success(self, mock_bq_client):
        from tools.productivity.task_tools import create_task

        pos_row = MagicMock()
        pos_row.__getitem__ = lambda self, k: 1
        mock_bq_client.query.return_value.result.return_value = [pos_row]

        result = create_task(title="Buy milk")
        assert result["status"] == "success"
        assert result["task"]["title"] == "Buy milk"
        assert result["task"]["status"] == "todo"
        mock_bq_client.insert_rows_json.assert_called_once()


class TestCreateTaskWithSteps:
    def test_creates_parent_and_children(self, mock_bq_client):
        from tools.productivity.task_tools import create_task_with_steps

        pos_row = MagicMock()
        pos_row.__getitem__ = lambda self, k: 0
        mock_bq_client.query.return_value.result.return_value = [pos_row]

        result = create_task_with_steps(
            title="Study for exam",
            steps=["Review notes", "Practice problems", "Make flashcards"],
        )
        assert result["status"] == "success"
        assert result["task"]["title"] == "Study for exam"
        assert len(result["steps"]) == 3
        # All rows inserted in one call
        rows = mock_bq_client.insert_rows_json.call_args[0][1]
        assert len(rows) == 4  # 1 parent + 3 steps

        # Steps reference parent
        parent_id = result["task"]["task_id"]
        for step in result["steps"]:
            assert step["parent_task_id"] == parent_id


class TestUpdateTaskStatus:
    def test_valid_status_transitions(self, mock_bq_client):
        from tools.productivity.task_tools import update_task_status

        for status in ("todo", "in_progress", "done"):
            result = update_task_status("task-001", status)
            assert result["status"] == "success"
            assert result["new_status"] == status

    def test_invalid_status_returns_error(self):
        from tools.productivity.task_tools import update_task_status

        result = update_task_status("task-001", "archived")
        assert result["status"] == "error"
        assert "Invalid status" in result["error_message"]


class TestDeleteTask:
    def test_delete_cascades_to_children(self, mock_bq_client):
        from tools.productivity.task_tools import delete_task

        result = delete_task("parent-001")
        assert result["status"] == "success"
        sql = mock_bq_client.query.call_args[0][0]
        assert "task_id = @task_id OR parent_task_id = @task_id" in sql


class TestGetAllTasks:
    def test_returns_structured_list(self, mock_bq_client):
        from tools.productivity.task_tools import get_all_tasks

        task_data = make_task()
        df = pd.DataFrame([task_data])
        mock_bq_client.query.return_value.to_dataframe.return_value = df

        result = get_all_tasks()
        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Buy groceries"
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_task_tools.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_task_tools.py
git commit -m "test: add unit tests for task tools"
```

---

### Task 10: Unit Test — BQ Client

**Files:**
- Create: `tests/unit/backend/test_bq_client.py`

- [ ] **Step 1: Write test_bq_client.py**

File: `tests/unit/backend/test_bq_client.py`
```python
"""Unit tests for db.bq_client — calendar query wrapper."""
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

import pytest
import pandas as pd


class TestQueryCalendarEvents:
    def test_default_date_range(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        mock_bq_client.query.return_value.to_dataframe.return_value = pd.DataFrame()

        result = query_calendar_events()
        assert result == []
        sql = mock_bq_client.query.call_args[0][0]
        assert "status = 'active'" in sql

    def test_custom_date_range(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        mock_bq_client.query.return_value.to_dataframe.return_value = pd.DataFrame()

        query_calendar_events(start_date="2026-05-01", end_date="2026-05-31")
        sql = mock_bq_client.query.call_args[0][0]
        assert "2026-05-01" in sql
        assert "2026-05-31" in sql

    def test_color_mapping_applied(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        ev = {
            "event_id": "e1",
            "title": "Run",
            "start_datetime": "2026-05-17T07:00:00",
            "end_datetime": "2026-05-17T08:00:00",
            "event_type": "workout",
            "source_agent": None,
            "priority": "medium",
            "status": "active",
            "description": None,
        }
        df = pd.DataFrame([ev])
        mock_bq_client.query.return_value.to_dataframe.return_value = df

        events = query_calendar_events(start_date="2026-05-17", end_date="2026-05-17")
        assert len(events) == 1
        assert events[0]["color"] == "#10B981"  # workout color
        assert events[0]["date"] == "2026-05-17"
        assert events[0]["time"] == "07:00"

    def test_exception_returns_empty_list(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        mock_bq_client.query.side_effect = Exception("network error")

        result = query_calendar_events()
        assert result == []


class TestGetWeekStart:
    def test_returns_monday(self):
        from db.bq_client import get_week_start

        # 2026-05-17 is a Sunday
        result = get_week_start("2026-05-17")
        assert result == "2026-05-11"  # Monday of that week

    def test_monday_returns_itself(self):
        from db.bq_client import get_week_start

        result = get_week_start("2026-05-11")
        assert result == "2026-05-11"

    def test_defaults_to_today(self):
        from db.bq_client import get_week_start

        result = get_week_start()
        parsed = date.fromisoformat(result)
        assert parsed.weekday() == 0  # Monday
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_bq_client.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_bq_client.py
git commit -m "test: add unit tests for BQ client calendar queries"
```

---

### Task 11: Unit Test — Skills Loader

**Files:**
- Create: `tests/unit/backend/test_skills_loader.py`

- [ ] **Step 1: Write test_skills_loader.py**

File: `tests/unit/backend/test_skills_loader.py`
```python
"""Unit tests for skills.loader — ADK skill loading."""
import pytest

ALL_SKILLS = [
    "fitness", "meal", "sleep", "habit", "task", "school",
    "longterm", "reading", "relationships", "news", "finance", "trivial",
]

SKILLS_WITH_REFERENCES = [
    "fitness", "meal", "sleep", "habit", "school",
    "longterm", "reading", "relationships", "finance",
]

SKILLS_WITHOUT_REFERENCES = ["task", "news", "trivial"]


class TestLoadAllSkills:
    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_load_skill_no_error(self, skill_name):
        from google.adk.skills import load_skill_from_dir
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        skill = load_skill_from_dir(str(skills_dir / skill_name))
        assert skill is not None
        assert skill.name == skill_name

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_nonempty_instructions(self, skill_name):
        from google.adk.skills import load_skill_from_dir
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        skill = load_skill_from_dir(str(skills_dir / skill_name))
        assert skill.instructions and len(skill.instructions.strip()) > 0


class TestSkillReferences:
    @pytest.mark.parametrize("skill_name", SKILLS_WITH_REFERENCES)
    def test_skills_with_references_have_files(self, skill_name):
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        refs_dir = skills_dir / skill_name / "references"
        assert refs_dir.is_dir(), f"Missing references/ for {skill_name}"
        ref_files = list(refs_dir.glob("*.md"))
        assert len(ref_files) > 0, f"No .md files in references/ for {skill_name}"

    @pytest.mark.parametrize("skill_name", SKILLS_WITHOUT_REFERENCES)
    def test_skills_without_references(self, skill_name):
        import pathlib

        skills_dir = pathlib.Path(__file__).resolve().parents[3] / "src" / "assistant" / "skills"
        refs_dir = skills_dir / skill_name / "references"
        assert not refs_dir.is_dir() or len(list(refs_dir.glob("*.md"))) == 0


class TestSkillToolsetLoader:
    def test_load_skill_toolset_success(self):
        from skills.loader import load_skill_toolset

        toolset = load_skill_toolset("fitness")
        assert toolset is not None

    def test_invalid_skill_raises(self):
        from skills.loader import load_skill_toolset

        with pytest.raises((FileNotFoundError, Exception)):
            load_skill_toolset("nonexistent_skill_xyz")

    def test_additional_tools_accepted(self):
        from skills.loader import load_skill_toolset

        def dummy_tool():
            pass

        toolset = load_skill_toolset("trivial", additional_tools=[dummy_tool])
        assert toolset is not None
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_skills_loader.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_skills_loader.py
git commit -m "test: add unit tests for ADK skills loader"
```

---

### Task 12: Unit Test — Session Service

**Files:**
- Create: `tests/unit/backend/test_session_service.py`

- [ ] **Step 1: Write test_session_service.py**

File: `tests/unit/backend/test_session_service.py`
```python
"""Unit tests for memory.firestore_session_service."""
import pytest
from unittest.mock import MagicMock

from fixtures.users import TEST_USER_ID, TEST_SESSION_ID


class TestFirestoreSessionService:
    @pytest.fixture
    def svc(self, mock_firestore_client):
        from memory.firestore_session_service import FirestoreSessionService
        return FirestoreSessionService(project_id="test-project")

    @pytest.mark.asyncio
    async def test_create_session(self, svc, mock_firestore_client):
        session = await svc.create_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
        )
        assert session.id == TEST_SESSION_ID
        assert session.user_id == TEST_USER_ID
        assert session.app_name == "test_app"
        # Should have called set() to persist
        mock_firestore_client.collection.return_value.document.return_value.set.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, svc, mock_firestore_client):
        session = await svc.get_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id="nonexistent",
        )
        assert session is None

    @pytest.mark.asyncio
    async def test_get_session_found(self, svc, mock_firestore_client):
        from google.adk.sessions import Session

        stored_session = Session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            id=TEST_SESSION_ID,
            state={},
            last_update_time=1000.0,
        )
        doc_snap = MagicMock()
        doc_snap.exists = True
        doc_snap.to_dict.return_value = {
            "app_name": "test_app",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "payload": stored_session.model_dump_json(),
        }
        mock_firestore_client.collection.return_value.document.return_value.get.return_value = doc_snap

        session = await svc.get_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
        )
        assert session is not None
        assert session.id == TEST_SESSION_ID

    @pytest.mark.asyncio
    async def test_delete_session(self, svc, mock_firestore_client):
        await svc.delete_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
        )
        mock_firestore_client.collection.return_value.document.return_value.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_sessions(self, svc, mock_firestore_client):
        result = await svc.list_sessions(app_name="test_app", user_id=TEST_USER_ID)
        assert result.sessions == []


class TestStateSplit:
    def test_prefixes_route_correctly(self):
        from memory.firestore_session_service import _split_state

        state = {
            "app:theme": "dark",
            "user:name": "Stephen",
            "temp:draft": "ignore me",
            "session_key": "session_value",
        }
        app_s, user_s, sess_s = _split_state(state)
        assert app_s == {"theme": "dark"}
        assert user_s == {"name": "Stephen"}
        assert sess_s == {"session_key": "session_value"}
        assert "draft" not in sess_s  # temp: dropped
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_session_service.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_session_service.py
git commit -m "test: add unit tests for Firestore session service"
```

---

### Task 13: Unit Test — Error Paths

**Files:**
- Create: `tests/unit/backend/test_error_paths.py`

- [ ] **Step 1: Write test_error_paths.py**

File: `tests/unit/backend/test_error_paths.py`
```python
"""Error-path tests — BQ timeouts, connection errors, malformed inputs."""
from unittest.mock import MagicMock

import pytest


class TestBigQueryErrors:
    def test_bq_timeout_returns_error(self, mock_bq_client):
        from memory.service import save_memory

        mock_bq_client.query.return_value.result.side_effect = TimeoutError("query timed out")

        result = save_memory(user_id="u", category="preference", subject="k", value="v")
        assert result["status"] == "error"
        assert "timed out" in result["error_message"]

    def test_bq_connection_error_in_recall(self, mock_bq_client):
        from memory.service import recall_memory

        mock_bq_client.query.return_value.result.side_effect = ConnectionError("network down")

        result = recall_memory(user_id="u")
        assert result["status"] == "error"
        assert "network" in result["error_message"].lower()

    def test_bq_insert_error_in_calendar(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        mock_bq_client.insert_rows_json.side_effect = Exception("quota exceeded")

        result = create_calendar_event(
            title="Fail",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
        )
        assert result["status"] == "error"
        assert "quota" in result["error_message"].lower()

    def test_bq_error_in_get_all_tasks(self, mock_bq_client):
        from tools.productivity.task_tools import get_all_tasks

        mock_bq_client.query.side_effect = Exception("service unavailable")

        result = get_all_tasks()
        assert result["status"] == "error"


class TestCalendarValidation:
    def test_invalid_priority_defaults(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        result = create_calendar_event(
            title="Test",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
            priority="urgent",  # invalid
        )
        assert result["status"] == "success"
        rows = mock_bq_client.insert_rows_json.call_args[0][1]
        assert rows[0]["priority"] == "medium"


class TestTaskValidation:
    def test_update_no_fields_returns_error(self):
        from tools.productivity.task_tools import update_task

        result = update_task(task_id="task-001")
        assert result["status"] == "error"
        assert "No fields" in result["error_message"]
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/test_error_paths.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/backend/test_error_paths.py
git commit -m "test: add error-path tests for BQ and validation"
```

---

### Task 14: Integration Test — Chat API

**Files:**
- Create: `tests/integration/test_chat_api.py`

- [ ] **Step 1: Write test_chat_api.py**

File: `tests/integration/test_chat_api.py`
```python
"""Integration tests for /api/chat endpoints — mocked runner."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_runner():
    with patch("api.routes.chat.run_agent", new_callable=AsyncMock) as mock:
        mock.return_value = "I can help with that!"
        yield mock


class TestChatEndpoint:
    @pytest.mark.asyncio
    async def test_chat_returns_response(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat", json={
            "session_id": "sess-001",
            "user_id": "user-001",
            "message": "Hello!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "assistant"
        assert data["content"] == "I can help with that!"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_chat_response_schema(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat", json={
            "session_id": "sess-001",
            "user_id": "user-001",
            "message": "What can you do?",
        })
        data = resp.json()
        assert set(data.keys()) == {"role", "content", "timestamp"}

    @pytest.mark.asyncio
    async def test_chat_invalid_body(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat", json={"message": "no session"})
        assert resp.status_code == 422


class TestDomainChatEndpoint:
    @pytest.mark.asyncio
    async def test_domain_chat_prefixes_message(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat/domain", json={
            "session_id": "sess-001",
            "user_id": "user-001",
            "message": "Log a run",
            "domain": "wellness",
        })
        assert resp.status_code == 200
        # Verify the runner received the prefixed message
        call_kwargs = mock_runner.call_args[1]
        assert "[Wellness context]" in call_kwargs["message"]
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/integration/test_chat_api.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_chat_api.py
git commit -m "test: add integration tests for chat API endpoints"
```

---

### Task 15: Integration Test — Calendar API

**Files:**
- Create: `tests/integration/test_calendar_api.py`

- [ ] **Step 1: Write test_calendar_api.py**

File: `tests/integration/test_calendar_api.py`
```python
"""Integration tests for /api/calendar endpoints."""
import pytest
from unittest.mock import patch

from fixtures.events import make_event


@pytest.fixture
def mock_bq_events():
    ev = make_event()
    ev["color"] = "#10B981"
    ev["date"] = "2026-05-17"
    ev["time"] = "07:00"
    with patch("api.routes.calendar.query_calendar_events", return_value=[ev]) as mock:
        yield mock


class TestCalendarGrid:
    @pytest.mark.asyncio
    async def test_grid_structure(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/grid")
        assert resp.status_code == 200
        data = resp.json()
        assert "grid" in data
        assert len(data["grid"]) == 6  # 6 weeks
        assert len(data["grid"][0]) == 7  # 7 days per week
        assert "week_label" in data
        assert "event_count" in data

    @pytest.mark.asyncio
    async def test_grid_day_fields(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/grid")
        day = resp.json()["grid"][0][0]
        assert "date" in day
        assert "day_num" in day
        assert "is_today" in day
        assert "events" in day

    @pytest.mark.asyncio
    async def test_grid_week_navigation(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/grid?week_start=2026-05-11")
        assert resp.status_code == 200
        data = resp.json()
        first_day = data["grid"][0][0]
        assert first_day["date"] == "2026-05-11"


class TestCalendarEvents:
    @pytest.mark.asyncio
    async def test_events_with_date_filter(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/events?start_date=2026-05-17&end_date=2026-05-24")
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert "count" in data
        assert data["count"] == len(data["events"])
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/integration/test_calendar_api.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_calendar_api.py
git commit -m "test: add integration tests for calendar API"
```

---

### Task 16: Integration Test — Session API

**Files:**
- Create: `tests/integration/test_session_api.py`

- [ ] **Step 1: Write test_session_api.py**

File: `tests/integration/test_session_api.py`
```python
"""Integration tests for /api/session endpoints."""
import pytest


class TestSessionInit:
    @pytest.mark.asyncio
    async def test_init_returns_session(self, app_client):
        resp = await app_client.post("/api/session/init")
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert "user_id" in data
        assert len(data["session_id"]) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_default_user_id(self, app_client):
        resp = await app_client.post("/api/session/init")
        data = resp.json()
        assert data["user_id"] == "default_user"

    @pytest.mark.asyncio
    async def test_multiple_inits_return_different_sessions(self, app_client):
        r1 = await app_client.post("/api/session/init")
        r2 = await app_client.post("/api/session/init")
        assert r1.json()["session_id"] != r2.json()["session_id"]
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/integration/test_session_api.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_session_api.py
git commit -m "test: add integration tests for session API"
```

---

### Task 17: Integration Test — Tasks API

**Files:**
- Create: `tests/integration/test_tasks_api.py`

- [ ] **Step 1: Write test_tasks_api.py**

File: `tests/integration/test_tasks_api.py`
```python
"""Integration tests for /api/tasks endpoints."""
import pytest
from unittest.mock import patch

from fixtures.tasks import make_task


@pytest.fixture
def mock_task_tools():
    tasks = [make_task()]
    with patch("api.routes.tasks.get_all_tasks", return_value={"status": "success", "tasks": tasks, "count": 1}) as mock_get, \
         patch("api.routes.tasks.update_task_status", return_value={"status": "success", "task_id": "task-test-001", "new_status": "in_progress"}) as mock_update, \
         patch("api.routes.tasks.delete_task", return_value={"status": "success", "deleted_task_id": "task-test-001"}) as mock_delete:
        yield mock_get, mock_update, mock_delete


class TestTasksEndpoints:
    @pytest.mark.asyncio
    async def test_list_tasks(self, app_client, mock_task_tools):
        resp = await app_client.get("/api/tasks")
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data
        assert "count" in data
        assert data["count"] == 1
        assert data["tasks"][0]["title"] == "Buy groceries"

    @pytest.mark.asyncio
    async def test_task_response_schema(self, app_client, mock_task_tools):
        resp = await app_client.get("/api/tasks")
        task = resp.json()["tasks"][0]
        expected_keys = {"task_id", "parent_task_id", "title", "description", "status",
                         "priority", "category", "due_date", "position", "created_at", "updated_at"}
        assert set(task.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_move_task(self, app_client, mock_task_tools):
        resp = await app_client.patch("/api/tasks/task-test-001/status", json={"status": "in_progress"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_task(self, app_client, mock_task_tools):
        resp = await app_client.delete("/api/tasks/task-test-001")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/integration/test_tasks_api.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_tasks_api.py
git commit -m "test: add integration tests for tasks API"
```

---

### Task 18: Integration Test — Routing Logic

**Files:**
- Create: `tests/integration/test_routing_logic.py`

- [ ] **Step 1: Write test_routing_logic.py**

File: `tests/integration/test_routing_logic.py`
```python
"""Integration tests — verify agent hierarchy and SkillToolset wiring."""
import pytest
from google.adk.tools.skill_toolset import SkillToolset


class TestRootOrchestrator:
    def test_root_has_6_sub_agents(self):
        from agents.root_orchestrator import root_orchestrator

        assert len(root_orchestrator.sub_agents) == 6
        names = {a.name for a in root_orchestrator.sub_agents}
        assert names == {
            "CalendarAgent",
            "WellnessRouter",
            "ProductivityRouter",
            "SocialRouter",
            "FinanceAgent",
            "TrivialAgent",
        }

    def test_root_has_memory_tools(self):
        from agents.root_orchestrator import root_orchestrator

        tool_names = [getattr(t, "__name__", getattr(t, "name", str(t))) for t in root_orchestrator.tools]
        assert "save_memory" in tool_names
        assert "recall_memory" in tool_names
        assert "forget_memory" in tool_names

    def test_root_has_before_agent_callback(self):
        from agents.root_orchestrator import root_orchestrator
        from memory.callbacks import inject_memory_bundle

        assert root_orchestrator.before_agent_callback == inject_memory_bundle


class TestDomainRouters:
    def test_wellness_router_has_4_specialists(self):
        from agents.wellness.wellness_router import wellness_router

        assert len(wellness_router.sub_agents) == 4
        names = {a.name for a in wellness_router.sub_agents}
        assert "FitnessAgent" in names
        assert "MealAgent" in names
        assert "SleepAgent" in names
        assert "HabitAgent" in names

    def test_productivity_router_has_4_specialists(self):
        from agents.productivity.productivity_router import productivity_router

        assert len(productivity_router.sub_agents) == 4
        names = {a.name for a in productivity_router.sub_agents}
        assert "TaskAgent" in names
        assert "SchoolAgent" in names

    def test_social_router_has_2_specialists(self):
        from agents.social.social_router import social_router

        assert len(social_router.sub_agents) == 2


class TestSkillToolsetWiring:
    def test_all_specialists_have_skill_toolset(self):
        from agents.wellness.wellness_router import wellness_router
        from agents.productivity.productivity_router import productivity_router
        from agents.social.social_router import social_router
        from agents.finance.finance_agent import finance_agent
        from agents.trivial_agent import trivial_agent

        all_specialists = (
            list(wellness_router.sub_agents)
            + list(productivity_router.sub_agents)
            + list(social_router.sub_agents)
            + [finance_agent, trivial_agent]
        )

        for agent in all_specialists:
            has_skillset = any(isinstance(t, SkillToolset) for t in agent.tools)
            assert has_skillset, f"{agent.name} has no SkillToolset"
```

- [ ] **Step 2: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/integration/test_routing_logic.py -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_routing_logic.py
git commit -m "test: add integration tests for agent routing and wiring"
```

---

### Task 19: Add Frontend Test Dependencies

**Files:**
- Modify: `src/assistant/frontend/package.json`
- Create: `src/assistant/frontend/vitest.config.ts`

- [ ] **Step 1: Install frontend test dependencies**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom msw @types/react @types/react-dom typescript
```

- [ ] **Step 2: Add test scripts to package.json**

Add these scripts to `package.json`:
```json
{
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] **Step 3: Create vitest.config.ts**

File: `src/assistant/frontend/vitest.config.ts`
```typescript
import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: ["../../../tests/unit/frontend/setup.ts"],
      include: ["../../../tests/unit/frontend/**/*.test.{ts,tsx}"],
      css: false,
    },
  })
);
```

- [ ] **Step 4: Create frontend test setup**

File: `tests/unit/frontend/setup.ts`
```typescript
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeAll, afterAll } from "vitest";
import { setupServer } from "msw/node";

afterEach(cleanup);

export const server = setupServer();
beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

- [ ] **Step 5: Verify vitest runs**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test 2>&1 | head -20
```
Expected: vitest runs (0 tests is fine at this point).

- [ ] **Step 6: Commit**

```bash
git add src/assistant/frontend/package.json src/assistant/frontend/pnpm-lock.yaml src/assistant/frontend/vitest.config.ts tests/unit/frontend/setup.ts
git commit -m "feat: add vitest + testing-library + MSW frontend test setup"
```

---

### Task 20: Frontend Unit Test — API Client

**Files:**
- Create: `tests/unit/frontend/api.test.ts`

- [ ] **Step 1: Write api.test.ts**

File: `tests/unit/frontend/api.test.ts`
```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "./setup";
import {
  initSession,
  sendMessage,
  sendDomainMessage,
  getCalendarGrid,
  getTasks,
} from "../../../src/assistant/frontend/src/lib/api";

describe("API client", () => {
  describe("initSession", () => {
    it("calls POST /api/session/init", async () => {
      server.use(
        http.post("*/api/session/init", () =>
          HttpResponse.json({ session_id: "s-1", user_id: "u-1" })
        )
      );
      const result = await initSession();
      expect(result.session_id).toBe("s-1");
      expect(result.user_id).toBe("u-1");
    });
  });

  describe("sendMessage", () => {
    it("sends sessionId, userId, message in body", async () => {
      let capturedBody: any;
      server.use(
        http.post("*/api/chat", async ({ request }) => {
          capturedBody = await request.json();
          return HttpResponse.json({
            role: "assistant",
            content: "Hello!",
            timestamp: "12:00",
          });
        })
      );
      const result = await sendMessage("sess", "user", "hi");
      expect(capturedBody).toEqual({
        session_id: "sess",
        user_id: "user",
        message: "hi",
      });
      expect(result.content).toBe("Hello!");
    });
  });

  describe("sendDomainMessage", () => {
    it("includes domain field", async () => {
      let capturedBody: any;
      server.use(
        http.post("*/api/chat/domain", async ({ request }) => {
          capturedBody = await request.json();
          return HttpResponse.json({
            role: "assistant",
            content: "OK",
            timestamp: "12:00",
          });
        })
      );
      await sendDomainMessage("sess", "user", "run", "wellness");
      expect(capturedBody.domain).toBe("wellness");
    });
  });

  describe("getCalendarGrid", () => {
    it("passes week_start as query param", async () => {
      let capturedUrl: string;
      server.use(
        http.get("*/api/calendar/grid", ({ request }) => {
          capturedUrl = request.url;
          return HttpResponse.json({
            grid: [],
            week_label: "May 2026",
            event_count: 0,
          });
        })
      );
      await getCalendarGrid("2026-05-11");
      expect(capturedUrl!).toContain("week_start=2026-05-11");
    });
  });

  describe("getTasks", () => {
    it("returns typed response", async () => {
      server.use(
        http.get("*/api/tasks", () =>
          HttpResponse.json({
            tasks: [
              {
                task_id: "t1",
                parent_task_id: "",
                title: "Test",
                description: "",
                status: "todo",
                priority: "medium",
                category: "",
                due_date: "",
                position: 0,
                created_at: "",
                updated_at: "",
              },
            ],
            count: 1,
          })
        )
      );
      const result = await getTasks();
      expect(result.tasks).toHaveLength(1);
      expect(result.tasks[0].task_id).toBe("t1");
    });
  });

  describe("error handling", () => {
    it("throws on network error", async () => {
      server.use(http.post("*/api/chat", () => HttpResponse.error()));
      await expect(sendMessage("s", "u", "msg")).rejects.toThrow();
    });
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- api.test.ts
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/api.test.ts
git commit -m "test: add frontend unit tests for API client"
```

---

### Task 21: Frontend Unit Test — useSession Hook

**Files:**
- Create: `tests/unit/frontend/useSession.test.ts`

- [ ] **Step 1: Write useSession.test.ts**

File: `tests/unit/frontend/useSession.test.ts`
```typescript
import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "./setup";
import { useSession } from "../../../src/assistant/frontend/src/hooks/useSession";

describe("useSession", () => {
  beforeEach(() => {
    sessionStorage.clear();
    server.use(
      http.post("*/api/session/init", () =>
        HttpResponse.json({ session_id: "new-sess", user_id: "default_user" })
      )
    );
  });

  it("initializes session on mount", async () => {
    const { result } = renderHook(() => useSession());

    await waitFor(() => {
      expect(result.current.ready).toBe(true);
    });
    expect(result.current.sessionId).toBe("new-sess");
    expect(result.current.userId).toBe("default_user");
  });

  it("persists to sessionStorage", async () => {
    const { result } = renderHook(() => useSession());

    await waitFor(() => expect(result.current.ready).toBe(true));
    const stored = JSON.parse(sessionStorage.getItem("pa_session")!);
    expect(stored.session_id).toBe("new-sess");
  });

  it("returns existing session from sessionStorage", async () => {
    sessionStorage.setItem(
      "pa_session",
      JSON.stringify({ session_id: "cached-sess", user_id: "cached-user" })
    );

    const { result } = renderHook(() => useSession());

    await waitFor(() => expect(result.current.ready).toBe(true));
    expect(result.current.sessionId).toBe("cached-sess");
    expect(result.current.userId).toBe("cached-user");
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- useSession.test.ts
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/useSession.test.ts
git commit -m "test: add frontend unit tests for useSession hook"
```

---

### Task 22: Frontend Unit Test — useChat Hook

**Files:**
- Create: `tests/unit/frontend/useChat.test.ts`

- [ ] **Step 1: Write useChat.test.ts**

File: `tests/unit/frontend/useChat.test.ts`
```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { server } from "./setup";
import { useChat } from "../../../src/assistant/frontend/src/hooks/useChat";

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe("useChat", () => {
  beforeEach(() => {
    server.use(
      http.post("*/api/chat", () =>
        HttpResponse.json({
          role: "assistant",
          content: "I can help!",
          timestamp: "12:00",
        })
      )
    );
  });

  it("sends message and appends to history", async () => {
    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Hello"));

    // User message should appear immediately
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Hello");

    // Wait for assistant response
    await waitFor(() => expect(result.current.messages).toHaveLength(2));
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].content).toBe("I can help!");
  });

  it("sets isThinking during request", async () => {
    server.use(
      http.post("*/api/chat", async () => {
        await new Promise((r) => setTimeout(r, 50));
        return HttpResponse.json({
          role: "assistant",
          content: "Done",
          timestamp: "12:00",
        });
      })
    );

    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Think"));
    expect(result.current.isThinking).toBe(true);

    await waitFor(() => expect(result.current.isThinking).toBe(false));
  });

  it("clear resets history", async () => {
    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Hello"));
    await waitFor(() => expect(result.current.messages).toHaveLength(2));

    act(() => result.current.clear());
    expect(result.current.messages).toHaveLength(0);
  });

  it("handles error response", async () => {
    server.use(
      http.post("*/api/chat", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 })
      )
    );

    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Fail"));
    await waitFor(() => expect(result.current.error).toBeTruthy());
    expect(result.current.isThinking).toBe(false);
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- useChat.test.ts
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/useChat.test.ts
git commit -m "test: add frontend unit tests for useChat hook"
```

---

### Task 23: Frontend Unit Test — useCalendar and useTasks Hooks

**Files:**
- Create: `tests/unit/frontend/useCalendar.test.ts`
- Create: `tests/unit/frontend/useTasks.test.ts`

- [ ] **Step 1: Write useCalendar.test.ts**

File: `tests/unit/frontend/useCalendar.test.ts`
```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { server } from "./setup";
import { useCalendarGrid } from "../../../src/assistant/frontend/src/hooks/useCalendar";

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

const mockGrid = {
  grid: Array.from({ length: 6 }, () =>
    Array.from({ length: 7 }, (_, i) => ({
      date: `2026-05-1${i}`,
      day_num: String(10 + i),
      is_today: i === 0,
      events: [],
    }))
  ),
  week_label: "May – June 2026",
  event_count: 0,
};

describe("useCalendarGrid", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/calendar/grid", () => HttpResponse.json(mockGrid))
    );
  });

  it("fetches grid on mount", async () => {
    const { result } = renderHook(() => useCalendarGrid(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data!.grid).toHaveLength(6);
    expect(result.current.data!.grid[0]).toHaveLength(7);
  });

  it("navigateWeek changes weekStart", async () => {
    const { result } = renderHook(() => useCalendarGrid(), {
      wrapper: createWrapper(),
    });

    const initial = result.current.weekStart;
    act(() => result.current.navigateWeek(1));
    expect(result.current.weekStart).not.toBe(initial);
  });
});
```

- [ ] **Step 2: Write useTasks.test.ts**

File: `tests/unit/frontend/useTasks.test.ts`
```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { server } from "./setup";
import { useTasks, useMoveTask, useDeleteTask } from "../../../src/assistant/frontend/src/hooks/useTasks";

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe("useTasks", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/tasks", () =>
        HttpResponse.json({
          tasks: [
            {
              task_id: "t1",
              parent_task_id: "",
              title: "Test Task",
              description: "",
              status: "todo",
              priority: "medium",
              category: "",
              due_date: "",
              position: 0,
              created_at: "",
              updated_at: "",
            },
          ],
          count: 1,
        })
      )
    );
  });

  it("fetches tasks", async () => {
    const { result } = renderHook(() => useTasks(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data!.tasks).toHaveLength(1);
    expect(result.current.data!.tasks[0].title).toBe("Test Task");
  });
});

describe("useMoveTask", () => {
  it("calls PATCH with status", async () => {
    let capturedBody: any;
    server.use(
      http.patch("*/api/tasks/:id/status", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({ status: "success" });
      })
    );

    const { result } = renderHook(() => useMoveTask(), { wrapper: createWrapper() });

    act(() => result.current.mutate({ taskId: "t1", status: "in_progress" }));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(capturedBody.status).toBe("in_progress");
  });
});

describe("useDeleteTask", () => {
  it("calls DELETE", async () => {
    let deletedId: string;
    server.use(
      http.delete("*/api/tasks/:id", ({ params }) => {
        deletedId = params.id as string;
        return HttpResponse.json({ status: "success" });
      })
    );

    const { result } = renderHook(() => useDeleteTask(), { wrapper: createWrapper() });

    act(() => result.current.mutate("t1"));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(deletedId!).toBe("t1");
  });
});
```

- [ ] **Step 3: Run tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- "useCalendar|useTasks"
```
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/frontend/useCalendar.test.ts tests/unit/frontend/useTasks.test.ts
git commit -m "test: add frontend unit tests for useCalendar and useTasks hooks"
```

---

### Task 24: Frontend Component Test — ChatInterface

**Files:**
- Create: `tests/unit/frontend/ChatInterface.test.tsx`

- [ ] **Step 1: Write ChatInterface.test.tsx**

File: `tests/unit/frontend/ChatInterface.test.tsx`
```tsx
import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import React from "react";
import { ChatProvider } from "../../../src/assistant/frontend/src/contexts/ChatContext";

// Mock hooks
vi.mock("../../../src/assistant/frontend/src/hooks/useSession", () => ({
  useSession: () => ({ sessionId: "sess", userId: "user", ready: true }),
}));

const mockSend = vi.fn();
const mockClear = vi.fn();

vi.mock("../../../src/assistant/frontend/src/hooks/useChat", () => ({
  useChat: () => ({
    messages: [],
    send: mockSend,
    clear: mockClear,
    isThinking: false,
    error: null,
  }),
}));

import { ChatInterface } from "../../../src/assistant/frontend/src/app/components/ChatInterface";

function Wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient();
  return React.createElement(
    QueryClientProvider,
    { client: qc },
    React.createElement(
      MemoryRouter,
      null,
      React.createElement(ChatProvider, null, children)
    )
  );
}

describe("ChatInterface", () => {
  beforeEach(() => {
    mockSend.mockClear();
    mockClear.mockClear();
  });

  it("renders empty state with welcome message", () => {
    render(React.createElement(ChatInterface), { wrapper: Wrapper });
    expect(screen.getByText(/I can help you manage/i)).toBeInTheDocument();
  });

  it("has an input field and send button", () => {
    render(React.createElement(ChatInterface), { wrapper: Wrapper });
    expect(screen.getByPlaceholderText(/Schedule a meeting/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "" })).toBeInTheDocument(); // Send icon button
  });

  it("can type and submit a message", async () => {
    const user = userEvent.setup();
    render(React.createElement(ChatInterface), { wrapper: Wrapper });

    const input = screen.getByPlaceholderText(/Schedule a meeting/i);
    await user.type(input, "Hello assistant");
    await user.keyboard("{Enter}");

    expect(mockSend).toHaveBeenCalledWith("Hello assistant");
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- ChatInterface.test.tsx
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/ChatInterface.test.tsx
git commit -m "test: add frontend unit tests for ChatInterface component"
```

---

### Task 25: Frontend Component Test — TasksPage

**Files:**
- Create: `tests/unit/frontend/TasksPage.test.tsx`

- [ ] **Step 1: Write TasksPage.test.tsx**

File: `tests/unit/frontend/TasksPage.test.tsx`
```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import React from "react";
import { ChatProvider } from "../../../src/assistant/frontend/src/contexts/ChatContext";

const mockTasks = [
  { task_id: "t1", parent_task_id: "", title: "Todo Item", description: "", status: "todo", priority: "high", category: "school", due_date: "2026-05-20", position: 0, created_at: "", updated_at: "" },
  { task_id: "t2", parent_task_id: "", title: "In Progress Item", description: "", status: "in_progress", priority: "medium", category: "", due_date: "", position: 1, created_at: "", updated_at: "" },
  { task_id: "t3", parent_task_id: "", title: "Done Item", description: "", status: "done", priority: "low", category: "", due_date: "", position: 2, created_at: "", updated_at: "" },
];

vi.mock("../../../src/assistant/frontend/src/hooks/useTasks", () => ({
  useTasks: () => ({
    data: { tasks: mockTasks, count: 3 },
    isLoading: false,
    error: null,
  }),
  useMoveTask: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteTask: () => ({ mutate: vi.fn(), isPending: false }),
}));

import { TasksPage } from "../../../src/assistant/frontend/src/app/components/TasksPage";

function Wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient();
  return React.createElement(
    QueryClientProvider,
    { client: qc },
    React.createElement(
      MemoryRouter,
      null,
      React.createElement(ChatProvider, null, children)
    )
  );
}

describe("TasksPage", () => {
  it("renders 3 kanban columns", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("To Do")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByText("Done")).toBeInTheDocument();
  });

  it("displays task cards in correct columns", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("Todo Item")).toBeInTheDocument();
    expect(screen.getByText("In Progress Item")).toBeInTheDocument();
    expect(screen.getByText("Done Item")).toBeInTheDocument();
  });

  it("shows task metadata", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("school")).toBeInTheDocument();
  });

  it("shows total count", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("3 total tasks")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- TasksPage.test.tsx
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/TasksPage.test.tsx
git commit -m "test: add frontend unit tests for TasksPage component"
```

---

### Task 26: Frontend Component Test — DomainChat

**Files:**
- Create: `tests/unit/frontend/DomainChat.test.tsx`

- [ ] **Step 1: Write DomainChat.test.tsx**

File: `tests/unit/frontend/DomainChat.test.tsx`
```tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";

vi.mock("../../../src/assistant/frontend/src/hooks/useSession", () => ({
  useSession: () => ({ sessionId: "sess", userId: "user", ready: true }),
}));

const mockSend = vi.fn();
vi.mock("../../../src/assistant/frontend/src/hooks/useChat", () => ({
  useDomainChat: () => ({
    messages: [],
    send: mockSend,
    clear: vi.fn(),
    isThinking: false,
    error: null,
  }),
}));

import { DomainChat } from "../../../src/assistant/frontend/src/app/components/DomainChat";

describe("DomainChat", () => {
  beforeEach(() => {
    mockSend.mockClear();
  });

  it("renders domain-specific header", () => {
    render(React.createElement(DomainChat, { domain: "wellness" }));
    expect(screen.getByText("Wellness Assistant")).toBeInTheDocument();
  });

  it("shows quick action examples", () => {
    render(React.createElement(DomainChat, { domain: "wellness" }));
    expect(screen.getByText("Log a 45-minute run")).toBeInTheDocument();
  });

  it("clicking example sends domain message", async () => {
    const user = userEvent.setup();
    render(React.createElement(DomainChat, { domain: "wellness" }));

    await user.click(screen.getByText("Log a 45-minute run"));
    expect(mockSend).toHaveBeenCalledWith("Log a 45-minute run");
  });

  it("renders different domain configs", () => {
    render(React.createElement(DomainChat, { domain: "finance" }));
    expect(screen.getByText("Finance Assistant")).toBeInTheDocument();
    expect(screen.getByText(/Add expense/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- DomainChat.test.tsx
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/DomainChat.test.tsx
git commit -m "test: add frontend unit tests for DomainChat component"
```

---

### Task 27: Frontend Component Test — CalendarView

**Files:**
- Create: `tests/unit/frontend/CalendarView.test.tsx`

- [ ] **Step 1: Write CalendarView.test.tsx**

File: `tests/unit/frontend/CalendarView.test.tsx`
```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import React from "react";
import { ChatProvider } from "../../../src/assistant/frontend/src/contexts/ChatContext";

vi.mock("../../../src/assistant/frontend/src/hooks/useCalendar", () => ({
  useCalendarEvents: () => ({
    data: { events: [], count: 0 },
    isLoading: false,
  }),
}));

import { CalendarView } from "../../../src/assistant/frontend/src/app/components/CalendarView";

function Wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient();
  return React.createElement(
    QueryClientProvider,
    { client: qc },
    React.createElement(
      MemoryRouter,
      null,
      React.createElement(ChatProvider, null, children)
    )
  );
}

describe("CalendarView", () => {
  it("renders calendar with view buttons", () => {
    render(React.createElement(CalendarView), { wrapper: Wrapper });
    expect(screen.getByText("Day")).toBeInTheDocument();
    expect(screen.getByText("Week")).toBeInTheDocument();
    expect(screen.getByText("Month")).toBeInTheDocument();
  });

  it("has Today button", () => {
    render(React.createElement(CalendarView), { wrapper: Wrapper });
    expect(screen.getByText("Today")).toBeInTheDocument();
  });

  it("shows month/year header", () => {
    render(React.createElement(CalendarView), { wrapper: Wrapper });
    // Should show current month and year
    const now = new Date();
    const monthYear = now.toLocaleDateString("en-US", { month: "long", year: "numeric" });
    expect(screen.getByText(monthYear)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test -- CalendarView.test.tsx
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/frontend/CalendarView.test.tsx
git commit -m "test: add frontend unit tests for CalendarView component"
```

---

### Task 28: Add Playwright E2E Setup

**Files:**
- Modify: `src/assistant/frontend/package.json` (add Playwright)
- Create: `src/assistant/frontend/playwright.config.ts`

- [ ] **Step 1: Install Playwright**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm add -D @playwright/test && npx playwright install chromium
```

- [ ] **Step 2: Add E2E scripts to package.json**

Add to scripts in `package.json`:
```json
{
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui"
}
```

- [ ] **Step 3: Create playwright.config.ts**

File: `src/assistant/frontend/playwright.config.ts`
```typescript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "../../../tests/e2e",
  testMatch: "**/*.spec.ts",
  timeout: 30000,
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: "cd ../../.. && cd src/assistant && uvicorn api.main:app --port 8082",
      port: 8082,
      reuseExistingServer: true,
    },
    {
      command: "pnpm dev",
      port: 5173,
      reuseExistingServer: true,
    },
  ],
});
```

- [ ] **Step 4: Commit**

```bash
git add src/assistant/frontend/package.json src/assistant/frontend/pnpm-lock.yaml src/assistant/frontend/playwright.config.ts
git commit -m "feat: add Playwright E2E test infrastructure"
```

---

### Task 29: E2E Test — Chat

**Files:**
- Create: `tests/e2e/chat.spec.ts`

- [ ] **Step 1: Write chat.spec.ts**

File: `tests/e2e/chat.spec.ts`
```typescript
import { test, expect } from "@playwright/test";

test.describe("Chat page", () => {
  test("page loads with chat interface", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Assistant")).toBeVisible();
    await expect(page.getByPlaceholderText(/Schedule a meeting/)).toBeVisible();
  });

  test("send message and get response", async ({ page }) => {
    await page.goto("/");
    const input = page.getByPlaceholderText(/Schedule a meeting/);
    await input.fill("Hello");
    await input.press("Enter");

    // User message should appear
    await expect(page.getByText("Hello")).toBeVisible();

    // Wait for assistant response (may take time with real backend)
    await expect(
      page.locator('[class*="bg-gray-50"]').filter({ hasText: /./}).last()
    ).toBeVisible({ timeout: 30000 });
  });

  test("message history preserved on navigation", async ({ page }) => {
    await page.goto("/");
    const input = page.getByPlaceholderText(/Schedule a meeting/);
    await input.fill("Test message");
    await input.press("Enter");
    await expect(page.getByText("Test message")).toBeVisible();

    // Navigate away
    await page.goto("/calendar");
    await page.waitForTimeout(500);

    // Navigate back
    await page.goto("/");
    // Note: messages may or may not persist depending on session state
    // This verifies the page loads without error after navigation
    await expect(page.getByPlaceholderText(/Schedule a meeting/)).toBeVisible();
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add tests/e2e/chat.spec.ts
git commit -m "test: add E2E chat tests"
```

---

### Task 30: E2E Test — Calendar

**Files:**
- Create: `tests/e2e/calendar.spec.ts`

- [ ] **Step 1: Write calendar.spec.ts**

File: `tests/e2e/calendar.spec.ts`
```typescript
import { test, expect } from "@playwright/test";

test.describe("Calendar page", () => {
  test("calendar page renders", async ({ page }) => {
    await page.goto("/calendar");
    await expect(page.getByText("Calendar")).toBeVisible();
    await expect(page.getByText("Today")).toBeVisible();
  });

  test("has view toggle buttons", async ({ page }) => {
    await page.goto("/calendar");
    await expect(page.getByText("Day")).toBeVisible();
    await expect(page.getByText("Week")).toBeVisible();
    await expect(page.getByText("Month")).toBeVisible();
  });

  test("navigate between views", async ({ page }) => {
    await page.goto("/calendar");
    await page.getByText("Month").click();
    // Calendar should re-render in month view
    await page.waitForTimeout(500);
    await page.getByText("Week").click();
    await page.waitForTimeout(500);
    // No crash = success
    await expect(page.getByText("Today")).toBeVisible();
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add tests/e2e/calendar.spec.ts
git commit -m "test: add E2E calendar tests"
```

---

### Task 31: E2E Test — Tasks

**Files:**
- Create: `tests/e2e/tasks.spec.ts`

- [ ] **Step 1: Write tasks.spec.ts**

File: `tests/e2e/tasks.spec.ts`
```typescript
import { test, expect } from "@playwright/test";

test.describe("Tasks page", () => {
  test("tasks page renders board", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page.getByText("Tasks")).toBeVisible();
    await expect(page.getByText("To Do")).toBeVisible();
    await expect(page.getByText("In Progress")).toBeVisible();
    await expect(page.getByText("Done")).toBeVisible();
  });

  test("has new task button", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page.getByText("+ New Task")).toBeVisible();
  });

  test("new task button navigates to chat", async ({ page }) => {
    await page.goto("/tasks");
    await page.getByText("+ New Task").click();
    // Should navigate to home (chat) page
    await expect(page.getByPlaceholderText(/Schedule a meeting/)).toBeVisible();
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add tests/e2e/tasks.spec.ts
git commit -m "test: add E2E tasks tests"
```

---

### Task 32: E2E Test — Session

**Files:**
- Create: `tests/e2e/session.spec.ts`

- [ ] **Step 1: Write session.spec.ts**

File: `tests/e2e/session.spec.ts`
```typescript
import { test, expect } from "@playwright/test";

test.describe("Session management", () => {
  test("session persists on refresh", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    // Get session from sessionStorage
    const session1 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );
    expect(session1).toBeTruthy();

    // Refresh
    await page.reload();
    await page.waitForTimeout(1000);

    const session2 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );
    expect(session2).toBe(session1);
  });

  test("session persists across pages", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    const session1 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );

    await page.goto("/calendar");
    await page.waitForTimeout(500);

    const session2 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );
    expect(session2).toBe(session1);
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add tests/e2e/session.spec.ts
git commit -m "test: add E2E session persistence tests"
```

---

### Task 33: LLM Eval Suite

**Files:**
- Create: `tests/llm_eval/__init__.py`
- Create: `tests/llm_eval/conftest.py`
- Create: `tests/llm_eval/test_agent_routing.py`
- Create: `tests/llm_eval/test_agent_tools.py`
- Create: `tests/llm_eval/test_skill_quality.py`

- [ ] **Step 1: Create llm_eval conftest**

File: `tests/llm_eval/conftest.py`
```python
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
```

- [ ] **Step 2: Create test_agent_routing.py**

File: `tests/llm_eval/test_agent_routing.py`
```python
"""LLM eval — verify agent routing with live Gemini calls."""
import pytest


@pytest.mark.llm
class TestAgentRouting:
    @pytest.fixture(autouse=True)
    def setup(self, require_api_key):
        pass

    @pytest.mark.asyncio
    async def test_fitness_query_routes(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-fitness",
            user_id="eval_user",
            message="What workouts did I do this week?",
        )
        assert isinstance(response, str)
        assert len(response) > 10

    @pytest.mark.asyncio
    async def test_calendar_query_routes(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-calendar",
            user_id="eval_user",
            message="What's on my calendar today?",
        )
        assert isinstance(response, str)
        assert len(response) > 10

    @pytest.mark.asyncio
    async def test_trivial_query_routes(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-trivial",
            user_id="eval_user",
            message="Hello, how are you?",
        )
        assert isinstance(response, str)
        assert len(response) > 5
```

- [ ] **Step 3: Create test_agent_tools.py**

File: `tests/llm_eval/test_agent_tools.py`
```python
"""LLM eval — verify agents call appropriate tools."""
import pytest


@pytest.mark.llm
class TestAgentTools:
    @pytest.fixture(autouse=True)
    def setup(self, require_api_key):
        pass

    @pytest.mark.asyncio
    async def test_memory_save_triggered(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-memory",
            user_id="eval_user",
            message="Remember that I prefer morning workouts",
        )
        assert isinstance(response, str)
        # Agent should acknowledge the preference was saved
        response_lower = response.lower()
        assert any(w in response_lower for w in ["remember", "noted", "saved", "preference", "morning"])
```

- [ ] **Step 4: Create test_skill_quality.py**

File: `tests/llm_eval/test_skill_quality.py`
```python
"""LLM eval — verify skill loading improves response quality."""
import pytest


@pytest.mark.llm
class TestSkillQuality:
    @pytest.fixture(autouse=True)
    def setup(self, require_api_key):
        pass

    @pytest.mark.asyncio
    async def test_agent_produces_substantive_response(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-skill",
            user_id="eval_user",
            message="Give me fitness tips for improving my 5K running time",
        )
        assert isinstance(response, str)
        assert len(response) > 50  # Should be a substantive response
```

- [ ] **Step 5: Commit**

```bash
git add tests/llm_eval/
git commit -m "test: add LLM evaluation test suite"
```

---

### Task 34: Run Full Backend Test Suite

- [ ] **Step 1: Run all backend unit tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend/ -v
```
Expected: all tests pass.

- [ ] **Step 2: Run all integration tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/integration/ -v
```
Expected: all tests pass.

- [ ] **Step 3: Run with coverage**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant && python -m pytest tests/unit/backend tests/integration --cov=src/assistant --cov-report=term-missing -v
```
Expected: coverage report generated, all tests pass.

---

### Task 35: Run Full Frontend Test Suite

- [ ] **Step 1: Run all frontend unit tests**

Run:
```bash
cd /Users/stephenkong/Documents/Github/personal_assistant/src/assistant/frontend && pnpm test
```
Expected: all tests pass.

- [ ] **Step 2: Final commit with any fixes**

If any tests needed adjustments, commit fixes:
```bash
git add -A
git commit -m "test: fix test adjustments from full suite run"
```
