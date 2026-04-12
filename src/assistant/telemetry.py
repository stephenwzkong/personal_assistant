"""Arize Phoenix telemetry for the personal assistant.

Phoenix receives OpenTelemetry traces with OpenInference semantic conventions,
giving us per-agent, per-tool, per-LLM-call visibility in its local UI.

Enable by setting PA_ENABLE_PHOENIX=1. Defaults to off so the normal dev flow
doesn't depend on Phoenix running.

Usage:
    1. In one terminal: `phoenix serve` (starts UI at http://localhost:6006)
    2. Export: `PA_ENABLE_PHOENIX=1`
    3. Start the API as usual; traces stream to Phoenix automatically.
"""
import os

_initialized = False


def init_phoenix() -> None:
    """Initialize Phoenix tracer provider and instrument the google-genai SDK.

    Idempotent — safe to call multiple times. No-op unless PA_ENABLE_PHOENIX=1.
    """
    global _initialized
    if _initialized:
        return
    if os.environ.get("PA_ENABLE_PHOENIX", "0") not in ("1", "true", "True"):
        return

    try:
        from phoenix.otel import register
    except ImportError:
        print("[telemetry] arize-phoenix-otel not installed; skipping Phoenix init")
        return

    endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    project_name = os.environ.get("PHOENIX_PROJECT_NAME", "personal-assistant")

    try:
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
            auto_instrument=False,  # we instrument explicitly below
        )
    except Exception as e:
        print(f"[telemetry] Phoenix register failed: {e}")
        return

    # Instrument google-genai (used by ADK under the hood) so every LLM call
    # emits a span with OpenInference attributes (model, prompt, completion, tokens).
    try:
        from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
        GoogleGenAIInstrumentor().instrument(tracer_provider=tracer_provider)
    except ImportError:
        print("[telemetry] openinference-instrumentation-google-genai not installed")
    except Exception as e:
        print(f"[telemetry] GoogleGenAIInstrumentor failed: {e}")

    _initialized = True
    print(f"[telemetry] Phoenix enabled → project='{project_name}' endpoint={endpoint}")
