from __future__ import annotations

import argparse
import os
import sys


GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def provider_key(provider_id: str) -> str | None:
    """Resolve a provider key without persisting or printing it."""
    key = os.getenv("FINROBOT_LLM_API_KEY")
    if key:
        return key
    environment_names = {
        "anthropic": ("ANTHROPIC_API_KEY",),
        "openai": ("OPENAI_API_KEY",),
        "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    }
    for name in environment_names.get(provider_id, ()):
        if value := os.getenv(name):
            return value
    return None


def custom_provider_kwargs(provider_id: str) -> list[dict[str, object]]:
    """Describe non-built-in OpenAI-compatible providers for FinRobot."""
    if provider_id != "gemini":
        return []
    return [
        {
            "id": "gemini",
            "label": "Google Gemini",
            "kind": "openai-compatible",
            "base_url": GEMINI_OPENAI_BASE_URL,
            "models": [],
        }
    ]


def candidate_models(primary: str, fallback_value: str | None) -> list[str]:
    """Return unique, same-provider model candidates in priority order."""
    provider_id = primary.partition(":")[0]
    candidates = [primary]
    for raw in (fallback_value or "").split(","):
        model = raw.strip()
        if not model:
            continue
        if ":" not in model:
            model = f"{provider_id}:{model}"
        if model.partition(":")[0] == provider_id and model not in candidates:
            candidates.append(model)
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one bounded event-analysis prompt through FinRobot V2")
    parser.add_argument("question")
    parser.add_argument("--model", required=True)
    parser.add_argument("--fallback-models", default=os.getenv("FINROBOT_FALLBACK_MODELS"))
    args = parser.parse_args()

    provider_id = args.model.partition(":")[0]
    key = provider_key(provider_id)
    if not key:
        raise SystemExit(
            "No FinRobot LLM key found. Set FINROBOT_LLM_API_KEY, "
            "GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY in the current terminal session."
        )

    from finrobot.config import ProviderConfig, get_settings
    from pydantic_ai import Agent
    from pydantic_ai.exceptions import (
        ModelQuotaExceededError,
        ModelRateLimitError,
        ModelRequestTimeout,
        ModelTimeoutError,
        ModelUnavailableError,
    )

    fallback_value = args.fallback_models
    if fallback_value is None and provider_id == "gemini":
        fallback_value = "gemini:gemini-3.5-flash-lite"

    request_timeout = float(os.getenv("FINROBOT_REQUEST_TIMEOUT", "45"))

    retryable_errors = (
        ModelUnavailableError,
        ModelQuotaExceededError,
        ModelRateLimitError,
        ModelRequestTimeout,
        ModelTimeoutError,
    )
    last_retryable: Exception | None = None
    for model_name in candidate_models(args.model, fallback_value):
        settings = get_settings(
            model_name=model_name,
            provider_keys={provider_id: key},
            custom_providers=[ProviderConfig(**item) for item in custom_provider_kwargs(provider_id)],
            fmp_api_key=os.getenv("FINROBOT_FMP_API_KEY", ""),
            finnhub_api_key=os.getenv("FINROBOT_FINNHUB_API_KEY", ""),
            # Event causality analysis does not require SEC filings. Keep EDGAR
            # disabled unless the operator explicitly supplies a real SEC identity.
            sec_user_agent=os.getenv("FINROBOT_SEC_USER_AGENT", "FinRobot admin@example.com"),
        )
        settings.validate_runtime_config()
        # A bounded news event needs one structured causal-analysis call, not
        # FinRobot's full equity-research team and tool loop. We still use
        # FinRobot's provider registry, runtime validation and model factory,
        # while the deterministic adapter validates/scorers the JSON afterward.
        agent = Agent(settings.create_model())
        try:
            result = agent.run_sync(
                args.question,
                model_settings={"timeout": request_timeout, "request_timeout": request_timeout},
            )
        except retryable_errors as exc:
            last_retryable = exc
            print(f"Model temporarily unavailable or limited: {model_name}; trying fallback.", file=sys.stderr)
            continue
        print(result.output)
        return

    if last_retryable is not None:
        raise last_retryable


if __name__ == "__main__":
    main()
