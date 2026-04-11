# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Permissions

- Reading files: allowed without asking for permission.
- Making any changes (edits, writes, deletions, running commands, etc.): always ask for permission first.

## Build and Run Commands

```bash
# Setup virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Run the Meal Hour Tracker (from src/meal_hour directory)
cd src/meal_hour && reflex run

# Run the Fitness Tracker (from src/fitness_tracker directory)
cd src/fitness_tracker && reflex run

# Run the Personal Assistant — FastAPI backend (port 8082)
cd src/assistant && uvicorn api.main:app --host 0.0.0.0 --port 8082 --reload

# Run the Personal Assistant — Vite frontend (port 5173, proxies /api → 8082)
cd src/assistant/frontend && pnpm install && pnpm dev

# Provision BigQuery tables for the assistant (one-time)
cd src/assistant && PYTHONPATH=. python schema/create_tables.py

# Run agents with Google ADK
cd tests && adk run agent.py
```

## Deployment (Cloud Run via Mise)

Each app has a `.mise.toml` with deployment tasks:

```bash
# From src/meal_hour/ or src/fitness_tracker/
mise run build-push-deploy   # Full pipeline: build → push to Artifact Registry → deploy
mise run logs                # View Cloud Run logs
mise run local-build         # Test locally with Docker
```

## Architecture Overview

This is a personal assistant project with four main components:

### 1. Meal Hour Tracker (`src/meal_hour/`)
Reflex web app for intermittent fasting tracking. Core class: `MealState(rx.State)` in `app/app.py`.

Data flow: User uploads food image → GCS (`personal_assistant_agent` bucket) → Gemini vision analysis (`gemini-2.0-flash-preview`) → structured `FoodAnalysis` Pydantic model → BigQuery (`personal_assistant.meal_hour` table)

### 2. Fitness Tracker (`src/fitness_tracker/`)
Reflex web app for workout tracking. Core class: `WorkoutState(rx.State)` in `app/app.py`.

Data flow: User uploads workout screenshot → GCS → Gemini vision analysis → structured `WorkoutAnalysis` Pydantic model → BigQuery (`personal_assistant.fitness_tracker` table). Aggregates daily/weekly statistics from BigQuery.

### 3. Personal Assistant (`src/assistant/`)
Multi-agent app with a Vite + React + shadcn frontend and a FastAPI backend. Single Cloud Run service on port 8082 (FastAPI serves `/api/*` and mounts the built `frontend/dist` at `/`). Vite dev server runs on 5173 with a `/api → 8082` proxy.

**Architecture**: Root `LlmAgent` orchestrator with domain routers (wellness, productivity, social) and standalone specialists (calendar, finance, trivial). Sub-agents use `AgentTool(calendar_agent)` to write calendar events. All data persisted to BigQuery (`personal_assistant` dataset).

**Sessions**: `FirestoreSessionService` (in `memory/firestore_session_service.py`) persists chat history to Firestore collections `adk_sessions` / `adk_user_state` / `adk_app_state`. Toggle with `PA_USE_FIRESTORE_SESSIONS=0` to fall back to in-memory.

**Memory**: `memory/service.py` stores user facts in BigQuery `memory_facts`. `inject_memory_bundle` before-agent callback injects a compact `<user_memory>` block into the orchestrator prompt via `{user_memory_block}`.

**Key files**:
- `agents/root_orchestrator.py` — root `LlmAgent` with domain routers + standalones as `sub_agents`
- `agents/shared/calendar_agent.py` — owns calendar CRUD; shared via `AgentTool`
- `runner.py` — ADK `Runner` singleton, session service selection, `run_agent` entrypoint
- `api/main.py` — FastAPI app; routes in `api/routes/{chat,calendar,session}.py`
- `db/bq_client.py` — BigQuery calendar query helper used by `api/routes/calendar.py`
- `memory/` — session service, fact store, bundle injection callback
- `frontend/src/app/components/` — React pages (Home, CalendarPage, DomainsPage, ChatInterface, DomainChat)
- `frontend/src/lib/api.ts` — typed fetch client for `/api/*`
- `schema/create_tables.py` — provisions BigQuery tables (run with `PYTHONPATH=.`)

### 4. Agent System (`tests/agent.py`)
Google ADK-based travel planning agent using `SequentialAgent` pattern. Chains three agents (research → itinerary → optimization) using `output_key` to pass state between steps. Uses `gemini-2.5-flash`.

## Reflex App Patterns (meal_hour + fitness_tracker only)

The two Reflex trackers follow the same structure:
- `rxconfig.py`: Backend on `0.0.0.0:8080/8081` for Cloud Run (single port serving frontend + backend)
- State class uses async event handlers for uploads and AI calls
- `rx.cond()` for conditional rendering (loading states, preview display)
- Pydantic models for structured Gemini API output via `response_schema` in `GenerationConfig`
- `save_df_to_bq()` uses `pandas-gbq` for BigQuery writes

The `src/assistant/` app was migrated off Reflex to Vite + FastAPI — do not add `rx.*` code there.

## Key Integrations

- **Google Cloud Storage**: Bucket `personal_assistant_agent` — stores uploaded images
- **Gemini Vision**: `gemini-2.0-flash-preview` — analyzes food/workout images with structured JSON output
- **BigQuery**: Dataset `personal_assistant` — persists meal and workout records
- **Google ADK**: `SequentialAgent` for chaining LLM agents
- **LiteLLM**: Universal LLM interface (supports Ollama, OpenAI, Google)

## Environment Variables

Required in `.env`:
```
GOOGLE_API_KEY=your_key
GOOGLE_CLOUD_PROJECT=your_project_id
```

For service account auth: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`

For Application Default Credentials (recommended for local dev):
```bash
gcloud auth application-default login
```
