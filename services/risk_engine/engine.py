from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.schemas.risk import RiskLevel, RiskVerdict
from core.schemas.transaction import TransactionCreate
from core.utils.helpers import Timer
from core.utils.logging import get_logger
from models.base import FraudModel
from services.risk_engine.ensemble import AdaptiveEnsemble
from services.risk_engine.rules.rule_engine import RuleEngine, RuleResult

logger = get_logger(__name__)


@dataclass
class ScoringResult:
    score: float
    level: RiskLevel
    verdict: RiskVerdict
    reasons: List[str] = field(default_factory=list)
    model_weights: Dict[str, float] = field(default_factory=dict)
    features: Dict[str, float] = field(default_factory=dict)
    latency_ms: float = 0.0


class RiskScoringEngine:
    def __init__(self, models: list[FraudModel]):
        self.rule_engine = RuleEngine()
        self.ensemble = AdaptiveEnsemble(models)

    def _fast_path_rules(self, transaction: TransactionCreate, features: Dict[str, float]) -> Optional[RuleResult]:
        result = self.rule_engine.evaluate(transaction, features)
        if result.triggered:
            return result
        return None

    def _ensemble_score(self, features: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        return self.ensemble.predict(features)

    def _determine_verdict(self, score: float, rule_result: Optional[RuleResult]) -> RiskVerdict:
        if rule_result and rule_result.action == "BLOCK":
            return RiskVerdict.BLOCK
        if rule_result and rule_result.action == "FLAG":
            return RiskVerdict.DECLINE

        if score > 0.9:
            return RiskVerdict.BLOCK
        if score > 0.7:
            return RiskVerdict.DECLINE
        if score > 0.4:
            return RiskVerdict.REVIEW
        return RiskVerdict.APPROVE

    def score_transaction(self, transaction: TransactionCreate, features: Dict[str, float]) -> ScoringResult:
        with Timer("risk_scoring") as timer:
            rule_result = self._fast_path_rules(transaction, features)

            score = 0.0
            model_weights = {}
            if not rule_result or rule_result.action != "BLOCK":
                score, model_weights = self._ensemble_score(features)

            verdict = self._determine_verdict(score, rule_result)

            risk_level = RiskLevel.LOW
            if verdict == RiskVerdict.BLOCK:
                risk_level = RiskLevel.CRITICAL
            elif verdict == RiskVerdict.DECLINE:
                risk_level = RiskLevel.HIGH
            elif verdict == RiskVerdict.REVIEW:
                risk_level = RiskLevel.MEDIUM

            reasons = []
            if rule_result:
                reasons.append(f"Rule {rule_result.rule_name} triggered: {rule_result.reason}")
            if score > 0.7:
                reasons.append(f"High ML risk score: {score:.3f}")

        logger.info("Risk scoring complete", verdict=verdict.value, latency_ms=timer.elapsed_ms)

        return ScoringResult(
            score=score,
            level=risk_level,
            verdict=verdict,
            reasons=reasons,
            model_weights=model_weights,
            features=features,
            latency_ms=timer.elapsed_ms
        )
