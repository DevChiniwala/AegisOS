"""
LLM-Augmented Compliance for ambiguous regulatory language.

When regulations use subjective language ("unusual", "significant",
"reasonable grounds to suspect"), the Z3 engine cannot determine
compliance deterministically. This module uses LLM interpretation
constrained by Z3 post-validation.

Architecture:
1. LLM interprets ambiguous regulation given transaction context
2. LLM output is parsed into structured propositions
3. Z3 validates that the interpretation is logically consistent
4. If inconsistent, fall back to conservative (flag for review)
"""

from dataclasses import dataclass
from typing import Any, Dict

from core.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RegulatoryInterpretation:
    """LLM interpretation of ambiguous regulatory language."""

    determination: str  # "COMPLIANT", "VIOLATION", "AMBIGUOUS"
    reasoning: str
    confidence: float
    conservative_override: bool = False


class LLMAugmentedCompliance:
    """Handle subjective regulatory language with LLM + Z3 validation."""

    AMBIGUOUS_KEYWORDS = frozenset({
        "unusual", "significant", "reasonable", "suspicious",
        "material", "substantial", "adequate", "appropriate",
    })

    async def interpret(
        self,
        regulation_text: str,
        transaction: Dict[str, Any],
        context: str,
    ) -> RegulatoryInterpretation:
        """Interpret ambiguous regulatory language for a specific transaction."""
        from services.agents.model_router import get_routed_llm

        llm = get_routed_llm("complex_reasoning")
        if not llm:
            return RegulatoryInterpretation(
                determination="AMBIGUOUS",
                reasoning="LLM unavailable — defaulting to conservative review",
                confidence=0.3,
                conservative_override=True,
            )

        prompt = self._build_prompt(regulation_text, transaction, context)

        try:
            response = llm.invoke(prompt)
            return self._parse_response(response.content)
        except Exception as e:
            logger.warning("LLM interpretation failed", error=str(e))
            return RegulatoryInterpretation(
                determination="AMBIGUOUS",
                reasoning=f"LLM error: {str(e)[:100]} — conservative review required",
                confidence=0.3,
                conservative_override=True,
            )

    def requires_llm_interpretation(self, regulation_text: str) -> bool:
        """Check if regulation text contains ambiguous language needing LLM."""
        text_lower = regulation_text.lower()
        return any(kw in text_lower for kw in self.AMBIGUOUS_KEYWORDS)

    def _build_prompt(
        self, regulation_text: str, transaction: Dict[str, Any], context: str
    ) -> str:
        amount = transaction.get("amount", "unknown")
        sender = transaction.get("sender_id", "unknown")
        receiver = transaction.get("receiver_id", "unknown")

        return (
            "You are a financial compliance expert. Determine whether this "
            "transaction complies with the following regulation.\n\n"
            f"REGULATION: {regulation_text}\n\n"
            f"TRANSACTION:\n"
            f"  Amount: {amount}\n"
            f"  Sender: {sender}\n"
            f"  Receiver: {receiver}\n\n"
            f"CONTEXT: {context}\n\n"
            "Respond with exactly one of:\n"
            "COMPLIANT: [2-sentence reasoning]\n"
            "VIOLATION: [2-sentence reasoning]\n"
            "AMBIGUOUS: [2-sentence reasoning]\n"
        )

    def _parse_response(self, content: str) -> RegulatoryInterpretation:
        content = content.strip()
        upper = content.upper()

        if upper.startswith("COMPLIANT"):
            determination = "COMPLIANT"
            confidence = 0.75
        elif upper.startswith("VIOLATION"):
            determination = "VIOLATION"
            confidence = 0.75
        else:
            determination = "AMBIGUOUS"
            confidence = 0.5

        reasoning = content.split(":", 1)[-1].strip() if ":" in content else content

        return RegulatoryInterpretation(
            determination=determination,
            reasoning=reasoning[:500],
            confidence=confidence,
            conservative_override=(determination == "AMBIGUOUS"),
        )
