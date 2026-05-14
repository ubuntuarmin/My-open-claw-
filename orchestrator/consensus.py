"""Dialectic consensus loop for sovereign component approval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from orchestrator.shared_memory import SharedMemoryEngine


class ModelAdapter(Protocol):
    """Simple protocol for model responders used in the debate loop."""

    name: str

    def generate(self, *, prompt: str, context: dict) -> str:
        """Return model completion for the given prompt and context."""


@dataclass(slots=True)
class DebateResult:
    """Final consensus artifact produced by the dialectic loop."""

    approved: bool
    rounds: int
    component: str
    moderator_verdict: str
    transcript: list[dict]


class DialecticConsensusEngine:
    """Runs Claude-vs-Gemini debate moderated by local DeepSeek-R1."""

    def __init__(self, memory: SharedMemoryEngine | None = None, max_rounds: int = 3) -> None:
        self.memory = memory or SharedMemoryEngine()
        self.max_rounds = max_rounds

    def run(
        self,
        *,
        component_request: str,
        claude: ModelAdapter,
        gemini: ModelAdapter,
        deepseek: ModelAdapter,
    ) -> DebateResult:
        """Execute consensus rounds until approved or round budget is exhausted."""
        context = self.memory.read_for_agent("consensus-engine", component_request)
        transcript: list[dict] = []

        proposal = claude.generate(
            prompt=(
                "Propose a UI component with production-grade React/Tailwind details. "
                f"Request: {component_request}"
            ),
            context=context,
        )
        critique = gemini.generate(
            prompt=(
                "Critique this proposal for logic, SEO, and structural integrity. "
                f"Proposal: {proposal}"
            ),
            context=context,
        )

        for round_number in range(1, self.max_rounds + 1):
            verdict = deepseek.generate(
                prompt=(
                    "Moderate this debate and decide approval. "
                    "Approval rule: include 'Human-Grade' and 'lacks AI-slop' when approved. "
                    f"Round: {round_number}. Proposal: {proposal}. Critique: {critique}"
                ),
                context=context,
            )
            approved = _is_human_grade_approved(verdict)
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "round": round_number,
                "claude_proposal": proposal,
                "gemini_critique": critique,
                "deepseek_verdict": verdict,
                "approved": approved,
            }
            transcript.append(entry)
            self.memory.append_consensus_log(entry)

            if approved:
                self.memory.append_thought_trace(
                    agent="deepseek-r1-architect",
                    task="dialectic-consensus",
                    summary="Approved component after dialectic loop.",
                    artifacts=[component_request],
                )
                return DebateResult(
                    approved=True,
                    rounds=round_number,
                    component=proposal,
                    moderator_verdict=verdict,
                    transcript=transcript,
                )

            if round_number == self.max_rounds:
                break

            rebuttal = claude.generate(
                prompt=(
                    "Rebut Gemini critique and refine the UI component. "
                    f"Critique: {critique}. Prior proposal: {proposal}"
                ),
                context=context,
            )
            proposal = rebuttal
            critique = gemini.generate(
                prompt=(
                    "Evaluate revised proposal. Flag unresolved logic, SEO, or structure issues. "
                    f"Revised proposal: {proposal}"
                ),
                context=context,
            )

        self.memory.append_thought_trace(
            agent="deepseek-r1-architect",
            task="dialectic-consensus",
            summary="Rejected component after max rebuttal rounds.",
            artifacts=[component_request],
        )
        final_verdict = transcript[-1]["deepseek_verdict"] if transcript else "No verdict"
        final_component = transcript[-1]["claude_proposal"] if transcript else proposal
        return DebateResult(
            approved=False,
            rounds=len(transcript),
            component=final_component,
            moderator_verdict=final_verdict,
            transcript=transcript,
        )


def _is_human_grade_approved(verdict: str) -> bool:
    lowered = verdict.lower()
    has_human_grade = "human-grade" in lowered
    has_no_slop = "lacks ai-slop" in lowered or "ai-slop: none" in lowered
    return has_human_grade and has_no_slop
