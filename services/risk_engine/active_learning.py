"""
Active Learning Loop for fraud model improvement.

When analysts override model decisions, those samples become highest
priority for the next training batch. Uncertainty sampling identifies
cases where the model is least confident — these are the most
informative samples for model improvement.

Feedback types:
- False Positive: Model flagged, analyst cleared → model too aggressive
- False Negative: Model approved, later identified as fraud → model too lenient
- Confirmed: Model flagged, analyst agreed → model correct (low learning value)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import time

from core.utils.logging import get_logger

logger = get_logger(__name__)


class FeedbackType(str, Enum):
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    CONFIRMED_FRAUD = "confirmed_fraud"
    CONFIRMED_LEGITIMATE = "confirmed_legitimate"


@dataclass
class AnalystFeedback:
    """Record of analyst feedback on a model prediction."""

    case_id: str
    model_prediction: str
    analyst_decision: str
    feedback_type: FeedbackType
    timestamp: float = field(default_factory=time.time)
    features: Dict[str, float] = field(default_factory=dict)
    risk_score: float = 0.0
    priority: float = 0.0


class ActiveLearningLoop:
    """Feedback loop integrating analyst decisions into model training.

    Priority scoring for training samples:
    - False negatives get highest priority (model missed real fraud)
    - False positives get high priority (model incorrectly flagged)
    - Uncertain cases (model confidence 0.4-0.6) get medium priority
    - Confirmed cases get lowest priority (model already knows these)
    """

    def __init__(self, max_buffer_size: int = 10000):
        self._feedback_buffer: deque = deque(maxlen=max_buffer_size)
        self._false_positive_count: int = 0
        self._false_negative_count: int = 0
        self._total_feedback: int = 0

    @property
    def buffer_size(self) -> int:
        return len(self._feedback_buffer)

    @property
    def false_positive_rate(self) -> float:
        if self._total_feedback == 0:
            return 0.0
        return self._false_positive_count / self._total_feedback

    @property
    def false_negative_rate(self) -> float:
        if self._total_feedback == 0:
            return 0.0
        return self._false_negative_count / self._total_feedback

    def record_feedback(
        self,
        case_id: str,
        model_prediction: str,
        analyst_decision: str,
        features: Optional[Dict[str, float]] = None,
        risk_score: float = 0.0,
    ) -> AnalystFeedback:
        """Record analyst feedback and compute training priority."""
        feedback_type = self._classify_feedback(model_prediction, analyst_decision)

        priority = self._compute_priority(feedback_type, risk_score)

        feedback = AnalystFeedback(
            case_id=case_id,
            model_prediction=model_prediction,
            analyst_decision=analyst_decision,
            feedback_type=feedback_type,
            features=features or {},
            risk_score=risk_score,
            priority=priority,
        )

        self._feedback_buffer.append(feedback)
        self._total_feedback += 1

        if feedback_type == FeedbackType.FALSE_POSITIVE:
            self._false_positive_count += 1
        elif feedback_type == FeedbackType.FALSE_NEGATIVE:
            self._false_negative_count += 1

        logger.info(
            "Analyst feedback recorded",
            case_id=case_id,
            feedback_type=feedback_type.value,
            priority=f"{priority:.2f}",
            buffer_size=self.buffer_size,
        )

        return feedback

    def get_training_priority_batch(self, batch_size: int = 100) -> List[Dict[str, Any]]:
        """Get highest-priority samples for next training iteration.

        Returns samples sorted by priority (highest first).
        """
        sorted_feedback = sorted(
            self._feedback_buffer, key=lambda f: f.priority, reverse=True
        )

        batch = []
        for feedback in sorted_feedback[:batch_size]:
            batch.append({
                "case_id": feedback.case_id,
                "features": feedback.features,
                "label": 1.0 if feedback.feedback_type in (
                    FeedbackType.FALSE_NEGATIVE, FeedbackType.CONFIRMED_FRAUD
                ) else 0.0,
                "priority": feedback.priority,
                "feedback_type": feedback.feedback_type.value,
                "risk_score": feedback.risk_score,
            })

        return batch

    def get_uncertainty_samples(
        self,
        predictions: List[Dict[str, Any]],
        top_k: int = 50,
    ) -> List[Dict[str, Any]]:
        """Identify predictions where model is least confident.

        Uncertainty = closeness to decision boundary (score near 0.5).
        These are the most informative samples for active labeling.
        """
        scored = []
        for pred in predictions:
            risk_score = pred.get("risk_score", 0.5)
            uncertainty = 1.0 - abs(2 * risk_score - 1.0)
            scored.append({**pred, "uncertainty": uncertainty})

        scored.sort(key=lambda x: x["uncertainty"], reverse=True)
        return scored[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """Get active learning statistics."""
        type_counts = {}
        for fb in self._feedback_buffer:
            type_counts[fb.feedback_type.value] = type_counts.get(fb.feedback_type.value, 0) + 1

        return {
            "total_feedback": self._total_feedback,
            "buffer_size": self.buffer_size,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
            "feedback_distribution": type_counts,
        }

    def _classify_feedback(self, model_prediction: str, analyst_decision: str) -> FeedbackType:
        """Classify feedback based on model prediction vs analyst decision."""
        model_flagged = model_prediction.upper() in ("BLOCK", "ESCALATE", "REVIEW", "FRAUD")
        analyst_fraud = analyst_decision.upper() in ("FRAUD", "BLOCK", "SAR", "ESCALATE")

        if model_flagged and not analyst_fraud:
            return FeedbackType.FALSE_POSITIVE
        elif not model_flagged and analyst_fraud:
            return FeedbackType.FALSE_NEGATIVE
        elif model_flagged and analyst_fraud:
            return FeedbackType.CONFIRMED_FRAUD
        else:
            return FeedbackType.CONFIRMED_LEGITIMATE

    def _compute_priority(self, feedback_type: FeedbackType, risk_score: float) -> float:
        """Compute training priority for a feedback instance."""
        base_priority = {
            FeedbackType.FALSE_NEGATIVE: 1.0,
            FeedbackType.FALSE_POSITIVE: 0.8,
            FeedbackType.CONFIRMED_FRAUD: 0.3,
            FeedbackType.CONFIRMED_LEGITIMATE: 0.2,
        }

        priority = base_priority[feedback_type]

        uncertainty_boost = 1.0 - abs(2 * risk_score - 1.0)
        priority += uncertainty_boost * 0.2

        return min(1.0, priority)
