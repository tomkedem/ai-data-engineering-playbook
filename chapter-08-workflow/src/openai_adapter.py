# src/openai_adapter.py
import os
from typing import List, Dict
from openai import OpenAI

# Each message is represented as {"role": "...", "content": "..."}.
Message = Dict[str, str]


class OpenAIAdapter:
    """Adapter that wraps OpenAI Chat Completions for the workflow runtime."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.1):
        # Read API key from environment to match project-wide configuration.
        self.api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        # Only create a client when a non-empty key is available.
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model
        self.temperature = temperature

    def complete(self, messages: List[Message]) -> str:
        # Fail fast with valid JSON when no API key is configured.
        if not self.api_key or self.client is None:
            # Return valid JSON so the agent runtime can finish gracefully.
            return '{"action":"finish","response":"Error: OPENAI_API_KEY environment variable is not set."}'

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            # Return model output as plain text; runtime parses the JSON.
            return resp.choices[0].message.content or ""
        except Exception:
            # Return valid JSON to avoid breaking the runtime on model failures.
            return '{"action":"finish","response":"Error: model call failed. Check API key and connectivity."}'
