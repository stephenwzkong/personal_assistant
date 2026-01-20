# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands

```bash
# Setup virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Run the Meal Hour Tracker web app (from src/meal_hour directory)
cd src/meal_hour && reflex run

# Run agents with Google ADK
cd tests && adk run agent.py
```

## Architecture Overview

This is a personal assistant project with two main components:

### 1. Meal Hour Tracker (`src/meal_hour/`)
A Reflex web application for intermittent fasting tracking:
- **`app/app.py`**: Main application with `MealState` class managing all state. Handles food image uploads to GCS, AI analysis via Gemini, and meal logging to BigQuery.
- **`rxconfig.py`**: Reflex config for Cloud Run deployment (single port serving both frontend and backend).
- **`Dockerfile`**: Production container for Cloud Run deployment.

Data flow: User uploads food image → GCS storage → Gemini vision analysis → BigQuery persistence

### 2. Agent System (`tests/agent.py`)
Google ADK-based agent examples using `SequentialAgent` pattern:
- Chains multiple specialized agents (research → planning → optimization)
- Uses `output_key` to pass data between agents in sequence

## Key Integrations

- **Google Cloud**: BigQuery (`personal_assistant.meal_hour` table), Cloud Storage (`personal_assistant_agent` bucket), Vertex AI
- **AI Models**: `gemini-3-flash-preview` for vision/analysis, `gemini-2.5-flash` for agents
- **LiteLLM**: Universal LLM interface supporting Ollama, OpenAI, and Google models

## Environment Variables

Required in `.env`:
```
GOOGLE_API_KEY=your_key
GOOGLE_CLOUD_PROJECT=your_project_id
```

For service account auth: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
