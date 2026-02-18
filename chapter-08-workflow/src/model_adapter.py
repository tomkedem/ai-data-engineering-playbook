# src/model_adapter.py
from __future__ import annotations

from typing import Protocol, List, Dict


Message = Dict[str, str]


class ModelAdapter(Protocol):
    def complete(self, messages: List[Message]) -> str:
        """
        Returns model text output.
        Must not raise on normal model failures, return best effort text instead.
        """
        ...
