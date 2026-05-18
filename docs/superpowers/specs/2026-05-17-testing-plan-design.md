# Testing Plan — Personal Assistant

## Context

The personal assistant app has zero test infrastructure. No pytest, no vitest, no test files, no CI. This spec establishes a comprehensive testing suite covering backend (Python/FastAPI/ADK), frontend (React/Vite), and E2E (Playwright), plus a separate LLM evaluation suite.

## Test Pyramid

- **Unit tests** (~20 files): fast, fully mocked, run on every save
- **Integration tests** (~5 files): FastAPI TestClient, mocked LLM, mocked BigQuery
- **E2E tests** (~4 files): Playwright browser tests against running app
- **LLM eval** (~3 files): live Gemini calls, run manually or nightly

## Dependencies

### Backend (Python)

Add to `pyproject.toml` under `[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "pytest-mock>=3.14",
    "httpx>=0.27",
]
```

### Frontend (TypeScript)

Add to `frontend/package.json` devDependencies:

```json
{
  "vitest": "^3.2",
  "@testing-library/react": "^16.3",
  "@testing-library/jest-dom": "^6.6",
  "@testing-library/user-event": "^14.6",
  "jsdom": "^26.1",
  "msw": "^2.10",
  "@playwright/test": "^1.52"
}
```

### Frontend scripts

Add to `frontend/package.json` scripts:

```json
{
  "test": "vitest run",
  "test:watch": "vitest",
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui"
}
```

## Directory Structure

```
tests/
├── conftest.py                  # Shared mocks (BigQuery, Firestore, ADK)
├── fixtures/
│   ├── __init__.py
│   ├── users.py                 # Test user IDs, default user
│   ├── events.py                # Calendar event dicts
│   ├── tasks.py                 # Task dicts with parent/children
│   └── memory.py                # Memory facts by category
├── unit/
│   ├── backend/
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
    ├── conftest.py
    ├── test_agent_routing.py
    ├── test_agent_tools.py
    └── test_skill_quality.py
```

## Configuration Files

### `pyproject.toml` — pytest config

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "llm: tests that call live Gemini API (deselect with -m 'not llm')",
]
```

### `frontend/vitest.config.ts`

```typescript
import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: ["../../tests/unit/frontend/setup.ts"],
      include: ["../../tests/unit/frontend/**/*.test.{ts,tsx}"],
      css: false,
    },
  })
);
```

### `frontend/playwright.config.ts`

```typescript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "../../tests/e2e",
  testMatch: "**/*.spec.ts",
  timeout: 30000,
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: "cd ../.. && uvicorn api.main:app --port 8082",
      port: 8082,
      reuseExistingServer: true,
      cwd: ".",
    },
    {
      command: "pnpm dev",
      port: 5173,
      reuseExistingServer: true,
    },
  ],
});
```

## Shared Fixtures (`tests/fixtures/`)

### `users.py`

```python
TEST_USER_ID = "test_user_001"
TEST_USER_ID_2 = "test_user_002"  # For isolation tests
DEFAULT_USER_ID = "default_user"
TEST_SESSION_ID = "test-session-00000000"
```

### `events.py`

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
```

### `tasks.py`

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
    }
    if overrides:
        base.update(overrides)
    return base

def make_task_with_steps():
    parent = make_task({"title": "Prepare for exam", "category": "school"})
    steps = [
        make_task({"task_id": f"step-{i}", "parent_task_id": parent["task_id"], "title": t, "position": i})
        for i, t in enumerate(["Review notes", "Practice problems", "Make flashcards"])
    ]
    return parent, steps
```

### `memory.py`

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
```

## Shared conftest.py (`tests/conftest.py`)

Key fixtures:

```python
@pytest.fixture
def mock_bq_client(mocker):
    """Mock google.cloud.bigquery.Client used across all BQ-dependent modules."""
    mock = mocker.patch("google.cloud.bigquery.Client")
    client = mock.return_value
    client.query.return_value.result.return_value = []
    client.query.return_value.to_dataframe.return_value = pd.DataFrame()
    return client

@pytest.fixture
def mock_firestore_client(mocker):
    """Mock google.cloud.firestore.Client for session service tests."""
    mock = mocker.patch("google.cloud.firestore.Client")
    return mock.return_value

@pytest.fixture
def app_client():
    """FastAPI TestClient using httpx for async support."""
    from api.main import app
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
```

## Unit Test Details

### test_memory_service.py

| Test | What it verifies |
|------|-----------------|
| `test_save_memory_success` | MERGE upsert returns `{status: success, subject, value}` |
| `test_save_memory_invalid_category` | Defaults to "preference" for unknown categories |
| `test_save_memory_bq_error` | BigQuery exception returns `{status: error}` |
| `test_recall_memory_with_filters` | Category + query keyword filters applied to SQL |
| `test_recall_memory_empty` | Returns `{facts: [], count: 0}` |
| `test_forget_memory_success` | DELETE by user_id + subject |
| `test_build_bundle_groups_by_category` | Facts grouped under `[category]` headers |
| `test_build_bundle_truncates` | Respects MAX_BUNDLE_CHARS |
| `test_build_bundle_empty` | Returns empty string when no facts |

### test_memory_privacy.py

| Test | What it verifies |
|------|-----------------|
| `test_user_isolation_recall` | User A's query never returns User B's facts |
| `test_user_isolation_forget` | User A cannot delete User B's facts |
| `test_forget_actually_deletes` | DELETE query issued (not soft-delete) |
| `test_no_pii_in_error_messages` | BigQuery errors don't leak user data or fact content |
| `test_session_isolation` | Different session_ids don't cross-contaminate state |

### test_memory_callbacks.py

| Test | What it verifies |
|------|-----------------|
| `test_inject_sets_state` | `state["user_memory_block"]` set with bundle content |
| `test_inject_fallback_user` | Falls back to "default_user" on missing context |
| `test_cache_hit_within_ttl` | Second call within 5 min doesn't query BQ |
| `test_cache_miss_after_ttl` | Call after 5 min re-queries BQ |
| `test_invalidate_clears_cache` | `invalidate_bundle()` removes cache entry |

### test_skills_loader.py

| Test | What it verifies |
|------|-----------------|
| `test_load_all_12_skills` | Parametrized: each skill name loads without error |
| `test_skill_name_matches_directory` | `skill.name == directory_name` for all skills |
| `test_skills_with_references` | 9 skills have non-empty `resources.references` |
| `test_skills_without_references` | task, news, trivial have empty references |
| `test_invalid_skill_raises` | `load_skill_toolset("nonexistent")` raises `FileNotFoundError` |
| `test_additional_tools_registered` | Tools passed to SkillToolset are accessible |
| `test_skill_instructions_nonempty` | Every skill has non-empty instructions |

### test_calendar_tools.py

| Test | What it verifies |
|------|-----------------|
| `test_create_event_success` | INSERT with valid fields returns `{status: success}` |
| `test_create_event_invalid_type` | Rejects event_type not in VALID_EVENT_TYPES |
| `test_list_events_date_range` | SQL WHERE clause includes start/end dates |
| `test_update_event_partial` | Only supplied fields updated |
| `test_delete_event_soft` | Sets `status='cancelled'`, not DELETE |
| `test_event_colors_mapped` | Each event_type gets correct hex color |

### test_task_tools.py

| Test | What it verifies |
|------|-----------------|
| `test_create_task_success` | INSERT returns `{status: success, task_id}` |
| `test_create_task_with_steps` | Parent + N children inserted |
| `test_update_status_valid` | todo → in_progress → done transitions |
| `test_delete_cascades` | Parent delete also deletes children |
| `test_get_all_tasks` | Returns structured list with count |

### test_error_paths.py

| Test | What it verifies |
|------|-----------------|
| `test_bq_timeout_returns_error` | BigQuery timeout → graceful error dict, not crash |
| `test_bq_connection_error` | Network failure → `{status: error}` |
| `test_invalid_datetime_format` | Malformed dates → error, not 500 |
| `test_missing_required_fields` | Missing title/event_type → validation error |
| `test_empty_message_chat` | Empty string message handled gracefully |

### test_bq_client.py

| Test | What it verifies |
|------|-----------------|
| `test_query_events_default_range` | Defaults to today-7 through today+42 |
| `test_query_events_custom_range` | Custom start/end dates passed to SQL |
| `test_color_mapping` | event_type → hex color applied to each event |
| `test_timestamp_to_iso` | BigQuery timestamps converted to ISO strings |
| `test_empty_result_on_error` | Exception returns `[]`, not crash |
| `test_get_week_start` | Returns Monday of the week |

### test_session_service.py

| Test | What it verifies |
|------|-----------------|
| `test_create_session` | Generates ID, persists to Firestore collections |
| `test_get_session` | Loads and merges state from 3 collections |
| `test_list_sessions` | Filters by app_name and optional user_id |
| `test_delete_session` | Removes from all collections |
| `test_state_split_by_prefix` | user:/app:/temp: prefixes route to correct collections |

## Integration Test Details

### test_chat_api.py

| Test | What it verifies |
|------|-----------------|
| `test_chat_returns_response` | POST `/api/chat` → 200 with `{role, content, timestamp}` |
| `test_chat_response_schema` | Response matches `ChatResponse` Pydantic model exactly |
| `test_domain_chat_prefixes` | POST `/api/chat/domain` prepends domain to message |
| `test_chat_invalid_body` | Missing fields → 422 |

Runner is mocked (not live LLM). Returns a fixed assistant response.

### test_calendar_api.py

| Test | What it verifies |
|------|-----------------|
| `test_grid_structure` | GET `/api/calendar/grid` → 6×7 grid with day objects |
| `test_grid_week_navigation` | `week_start` parameter shifts the grid |
| `test_events_date_filter` | GET `/api/calendar/events?start_date=...&end_date=...` |
| `test_event_count` | Response `count` matches actual event list length |

### test_tasks_api.py

| Test | What it verifies |
|------|-----------------|
| `test_list_tasks` | GET `/api/tasks` → `{tasks: [...], count: N}` |
| `test_move_task` | PATCH `/api/tasks/{id}/status` updates status |
| `test_delete_task` | DELETE `/api/tasks/{id}` removes task |
| `test_task_response_schema` | Response matches `TaskOut` model |

### test_session_api.py

| Test | What it verifies |
|------|-----------------|
| `test_init_session` | POST `/api/session/init` → valid UUID session_id |
| `test_session_default_user` | Default user_id is "default_user" |

### test_routing_logic.py

Mocked LLM — asserts the agent plumbing without calling Gemini.

| Test | What it verifies |
|------|-----------------|
| `test_root_has_6_sub_agents` | Root orchestrator sub_agents count and names |
| `test_wellness_router_has_4_specialists` | Correct sub-agents on WellnessRouter |
| `test_productivity_router_has_4_specialists` | Correct sub-agents on ProductivityRouter |
| `test_social_router_has_2_specialists` | Correct sub-agents on SocialRouter |
| `test_all_specialists_have_skill_toolset` | Each leaf agent's tools[0] is SkillToolset |
| `test_calendar_agent_shared_via_agenttool` | CalendarAgent appears as additional_tool in each specialist |
| `test_skill_toolset_provides_builtin_tools` | list_skills, load_skill, load_skill_resource present |

## Frontend Unit Test Details

### setup.ts

```typescript
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";
import { setupServer } from "msw/node";

afterEach(cleanup);

// MSW server for API mocking
export const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### api.test.ts

| Test | What it verifies |
|------|-----------------|
| `initSession calls POST /api/session/init` | Correct endpoint, returns session data |
| `sendMessage calls POST /api/chat` | Sends sessionId, userId, message in body |
| `sendDomainMessage includes domain` | Domain field included in request body |
| `getCalendarGrid passes week_start` | Query param serialized correctly |
| `getTasks returns typed response` | Response parsed into TaskOut[] |
| `handles network error` | Throws on fetch failure |

### useSession.test.ts

| Test | What it verifies |
|------|-----------------|
| `initializes session on mount` | Calls initSession, sets ready=true |
| `persists to sessionStorage` | Session survives re-render |
| `returns existing session` | Doesn't call API if sessionStorage has data |

### useChat.test.ts

| Test | What it verifies |
|------|-----------------|
| `sends message and appends to history` | Message appears in messages array |
| `sets isThinking during request` | True while awaiting, false after |
| `handles error response` | Sets error state, isThinking=false |
| `clear resets history` | messages becomes empty |
| `invalidates calendar after response` | React Query calendar key invalidated |

### ChatInterface.test.tsx

| Test | What it verifies |
|------|-----------------|
| `renders empty state` | Shows welcome message when no messages |
| `renders message history` | User and assistant messages displayed |
| `input field and send button` | Can type and submit |
| `shows loading during thinking` | Loading indicator visible |
| `scrolls to latest message` | Auto-scroll behavior |

### CalendarView.test.tsx

| Test | What it verifies |
|------|-----------------|
| `renders calendar grid` | 7-day columns visible |
| `displays events with colors` | Event chips show correct color by type |
| `week navigation` | Previous/next week buttons work |
| `today highlighted` | Current date visually distinct |

### TasksPage.test.tsx

| Test | What it verifies |
|------|-----------------|
| `renders 3 kanban columns` | todo, in_progress, done columns present |
| `displays task cards` | Task title, priority, category shown |
| `empty column state` | Empty message when column has no tasks |
| `delete button removes task` | Calls deleteTask, card disappears |

### DomainChat.test.tsx

| Test | What it verifies |
|------|-----------------|
| `renders domain-specific header` | Domain name in header |
| `quick actions prefill input` | Clicking action sets message text |
| `sends domain message` | Uses sendDomainMessage, not sendMessage |

## E2E Test Details (Playwright)

### chat.spec.ts

| Test | What it verifies |
|------|-----------------|
| `page loads with chat interface` | Chat page renders, input visible |
| `send message and get response` | Type, send, assistant response appears |
| `message history preserved on navigation` | Navigate away and back, messages still there |
| `domain chat via sidebar` | Navigate to domain, send message, response received |

### calendar.spec.ts

| Test | What it verifies |
|------|-----------------|
| `calendar page renders grid` | Grid with day cells visible |
| `navigate between weeks` | Click arrows, week label updates |
| `events displayed in cells` | Events show in correct day cells |

### tasks.spec.ts

| Test | What it verifies |
|------|-----------------|
| `tasks page renders board` | Three columns visible |
| `task cards display` | Cards show in correct columns |
| `move task between columns` | Status change reflected on board |

### session.spec.ts

| Test | What it verifies |
|------|-----------------|
| `session persists on refresh` | Refresh page, session_id unchanged |
| `session persists across pages` | Navigate between pages, same session |
| `new tab gets new session` | Open in new tab (no sessionStorage sharing) |

## LLM Eval Suite

Marked with `@pytest.mark.llm`. Run with `pytest tests/llm_eval/ -m llm`. Requires `GOOGLE_API_KEY`.

### test_agent_routing.py

| Test | What it verifies |
|------|-----------------|
| `fitness query routes correctly` | "How are my workouts?" → FitnessAgent handles |
| `calendar query routes correctly` | "What's on my calendar?" → CalendarAgent handles |
| `task creation routes correctly` | "Add a task" → TaskAgent handles |
| `multi-domain query` | "Schedule a workout" → FitnessAgent + CalendarAgent |

### test_agent_tools.py

| Test | What it verifies |
|------|-----------------|
| `agent calls workout tools` | Fitness query triggers get_recent_workouts |
| `agent calls calendar tools` | Schedule request triggers create_calendar_event |
| `agent calls memory tools` | "I prefer mornings" triggers save_memory |

### test_skill_quality.py

| Test | What it verifies |
|------|-----------------|
| `agent loads skill when relevant` | Complex coaching question triggers load_skill |
| `agent loads references for evidence` | Research question triggers load_skill_resource |
| `skill instructions improve response` | Loaded agent references research context in reply |

## Test Commands

```bash
# Backend unit tests (fast, no external deps)
pytest tests/unit/backend/ -v

# Backend integration tests (mocked LLM, mocked BQ)
pytest tests/integration/ -v

# All backend tests with coverage
pytest tests/unit/backend tests/integration --cov=src/assistant --cov-report=html

# Frontend unit tests
cd src/assistant/frontend && pnpm test

# Frontend tests in watch mode
cd src/assistant/frontend && pnpm test:watch

# E2E tests (starts backend + frontend automatically)
cd src/assistant/frontend && pnpm test:e2e

# E2E with Playwright UI
cd src/assistant/frontend && pnpm test:e2e:ui

# LLM eval suite (requires GOOGLE_API_KEY, run manually)
pytest tests/llm_eval/ -m llm -v

# Quick smoke test (unit only)
pytest tests/unit/ -v --tb=short
```
