"""Centralized shared-memory blackboard for sovereign orchestration."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from clawteam.fileutil import atomic_write_text, file_locked


class ThoughtTrace(BaseModel):
    """Single immutable thought trace emitted by an agent."""

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent: str
    task: str = ""
    summary: str
    artifacts: list[str] = Field(default_factory=list)


class SharedContext(BaseModel):
    """Persisted blackboard schema shared across all orchestrator agents."""

    design_dna: dict[str, Any] = Field(default_factory=dict)
    learned_user_preferences: dict[str, Any] = Field(default_factory=dict)
    component_registry: dict[str, Any] = Field(default_factory=dict)
    seo_matrix: dict[str, Any] = Field(default_factory=dict)
    consensus_logs: list[dict[str, Any]] = Field(default_factory=list)
    thought_traces: list[ThoughtTrace] = Field(default_factory=list)


class SharedMemoryEngine:
    """Persistent JSON blackboard that every worker reads and writes."""

    def __init__(self, path: Path | None = None) -> None:
        default = Path.cwd() / "memory" / "shared_context.json"
        configured = os.environ.get("CLAWTEAM_SHARED_MEMORY_PATH")
        self.path = path or Path(configured) if configured else path or default

    def initialize(self) -> SharedContext:
        """Create the memory file if needed and return current context."""
        with file_locked(self.path):
            if not self.path.exists():
                context = SharedContext()
                atomic_write_text(self.path, context.model_dump_json(indent=2))
                return context
        return self.load()

    def load(self) -> SharedContext:
        """Load shared context from disk, creating defaults when missing."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            return self.initialize()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return SharedContext.model_validate(data)
        except Exception:
            context = SharedContext()
            atomic_write_text(self.path, context.model_dump_json(indent=2))
            return context

    def read_for_agent(self, agent: str, task: str) -> dict[str, Any]:
        """Return context snapshot workers must load before executing tasks."""
        context = self.load()
        return {
            "agent": agent,
            "task": task,
            "snapshot": context.model_dump(mode="json"),
            "required_fields": [
                "design_dna",
                "learned_user_preferences",
                "component_registry",
                "seo_matrix",
                "consensus_logs",
            ],
        }

    def write_context(self, context: SharedContext) -> None:
        """Persist shared context atomically."""
        with file_locked(self.path):
            atomic_write_text(self.path, context.model_dump_json(indent=2))

    def append_thought_trace(
        self,
        *,
        agent: str,
        task: str,
        summary: str,
        artifacts: list[str] | None = None,
    ) -> ThoughtTrace:
        """Write an agent thought trace after task completion."""
        trace = ThoughtTrace(
            agent=agent,
            task=task,
            summary=summary,
            artifacts=artifacts or [],
        )
        with file_locked(self.path):
            context = self.load()
            context.thought_traces.append(trace)
            atomic_write_text(self.path, context.model_dump_json(indent=2))
        return trace

    def append_consensus_log(self, entry: dict[str, Any]) -> None:
        """Append dialectic-loop transcript entry to consensus logs."""
        with file_locked(self.path):
            context = self.load()
            context.consensus_logs.append(entry)
            atomic_write_text(self.path, context.model_dump_json(indent=2))
