from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts.finrobot_event_runner import (
    GEMINI_OPENAI_BASE_URL,
    candidate_models,
    custom_provider_kwargs,
    provider_key,
)


class FinRobotEventRunnerTests(unittest.TestCase):
    def test_gemini_provider_uses_google_openai_compatible_endpoint(self) -> None:
        providers = custom_provider_kwargs("gemini")
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0]["kind"], "openai-compatible")
        self.assertEqual(providers[0]["base_url"], GEMINI_OPENAI_BASE_URL)

    def test_gemini_key_is_read_from_environment(self) -> None:
        clean = {key: value for key, value in os.environ.items() if key not in {
            "FINROBOT_LLM_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"
        }}
        with patch.dict(os.environ, {**clean, "GEMINI_API_KEY": "test-key"}, clear=True):
            self.assertEqual(provider_key("gemini"), "test-key")

    def test_generic_override_takes_precedence(self) -> None:
        with patch.dict(
            os.environ,
            {"FINROBOT_LLM_API_KEY": "override", "GEMINI_API_KEY": "gemini"},
            clear=True,
        ):
            self.assertEqual(provider_key("gemini"), "override")

    def test_unknown_provider_does_not_inherit_an_unrelated_key(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini"}, clear=True):
            self.assertIsNone(provider_key("other"))

    def test_fallback_models_are_normalized_and_deduplicated(self) -> None:
        self.assertEqual(
            candidate_models(
                "gemini:gemini-3.8-flash",
                "gemini-3.7-flash,gemini:gemini-3.8-flash,openai:gpt-4o",
            ),
            ["gemini:gemini-3.8-flash", "gemini:gemini-3.7-flash"],
        )


if __name__ == "__main__":
    unittest.main()
