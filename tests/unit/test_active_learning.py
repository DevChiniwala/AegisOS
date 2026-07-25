"""
Tests for Active Learning Loop.
"""

import pytest

from services.risk_engine.active_learning import (
    ActiveLearningLoop,
    AnalystFeedback,
    FeedbackType,
)


class TestFeedbackClassification:
    def setup_method(self):
        self.loop = ActiveLearningLoop()

    def test_false_positive(self):
        fb = self.loop.record_feedback(
            case_id="C-001",
            model_prediction="BLOCK",
            analyst_decision="LEGITIMATE",
        )
        assert fb.feedback_type == FeedbackType.FALSE_POSITIVE

    def test_false_negative(self):
        fb = self.loop.record_feedback(
            case_id="C-002",
            model_prediction="APPROVE",
            analyst_decision="FRAUD",
        )
        assert fb.feedback_type == FeedbackType.FALSE_NEGATIVE

    def test_confirmed_fraud(self):
        fb = self.loop.record_feedback(
            case_id="C-003",
            model_prediction="ESCALATE",
            analyst_decision="FRAUD",
        )
        assert fb.feedback_type == FeedbackType.CONFIRMED_FRAUD

    def test_confirmed_legitimate(self):
        fb = self.loop.record_feedback(
            case_id="C-004",
            model_prediction="APPROVE",
            analyst_decision="LEGITIMATE",
        )
        assert fb.feedback_type == FeedbackType.CONFIRMED_LEGITIMATE


class TestPriority:
    def setup_method(self):
        self.loop = ActiveLearningLoop()

    def test_false_negative_highest_priority(self):
        fn = self.loop.record_feedback("C-001", "APPROVE", "FRAUD", risk_score=0.3)
        fp = self.loop.record_feedback("C-002", "BLOCK", "LEGITIMATE", risk_score=0.8)
        assert fn.priority > fp.priority

    def test_false_positive_higher_than_confirmed(self):
        fp = self.loop.record_feedback("C-001", "BLOCK", "LEGITIMATE", risk_score=0.7)
        cf = self.loop.record_feedback("C-002", "BLOCK", "FRAUD", risk_score=0.9)
        assert fp.priority > cf.priority

    def test_uncertainty_boosts_priority(self):
        # Risk score 0.5 = maximum uncertainty
        uncertain = self.loop.record_feedback("C-001", "BLOCK", "LEGITIMATE", risk_score=0.5)
        # Risk score 0.95 = very certain
        certain = self.loop.record_feedback("C-002", "BLOCK", "LEGITIMATE", risk_score=0.95)
        assert uncertain.priority > certain.priority


class TestTrainingBatch:
    def setup_method(self):
        self.loop = ActiveLearningLoop()

    def test_empty_batch(self):
        batch = self.loop.get_training_priority_batch()
        assert batch == []

    def test_batch_sorted_by_priority(self):
        self.loop.record_feedback("C-001", "APPROVE", "FRAUD", risk_score=0.3)  # FN
        self.loop.record_feedback("C-002", "BLOCK", "LEGITIMATE", risk_score=0.8)  # FP
        self.loop.record_feedback("C-003", "APPROVE", "LEGITIMATE", risk_score=0.1)  # CL

        batch = self.loop.get_training_priority_batch(batch_size=3)
        assert len(batch) == 3
        assert batch[0]["priority"] >= batch[1]["priority"] >= batch[2]["priority"]
        assert batch[0]["case_id"] == "C-001"  # FN is highest priority

    def test_batch_labels(self):
        self.loop.record_feedback("C-001", "APPROVE", "FRAUD")  # FN → label 1
        self.loop.record_feedback("C-002", "BLOCK", "LEGITIMATE")  # FP → label 0

        batch = self.loop.get_training_priority_batch()
        fn_sample = next(s for s in batch if s["case_id"] == "C-001")
        fp_sample = next(s for s in batch if s["case_id"] == "C-002")
        assert fn_sample["label"] == 1.0
        assert fp_sample["label"] == 0.0

    def test_batch_size_limit(self):
        for i in range(20):
            self.loop.record_feedback(f"C-{i:03d}", "BLOCK", "LEGITIMATE")
        batch = self.loop.get_training_priority_batch(batch_size=5)
        assert len(batch) == 5


class TestUncertaintySampling:
    def setup_method(self):
        self.loop = ActiveLearningLoop()

    def test_most_uncertain_first(self):
        predictions = [
            {"case_id": "A", "risk_score": 0.5},   # max uncertainty
            {"case_id": "B", "risk_score": 0.95},  # low uncertainty
            {"case_id": "C", "risk_score": 0.05},  # low uncertainty
            {"case_id": "D", "risk_score": 0.45},  # high uncertainty
        ]
        samples = self.loop.get_uncertainty_samples(predictions, top_k=2)
        assert len(samples) == 2
        assert samples[0]["case_id"] == "A"
        assert samples[1]["case_id"] == "D"

    def test_uncertainty_score_range(self):
        predictions = [{"risk_score": i / 10.0} for i in range(11)]
        samples = self.loop.get_uncertainty_samples(predictions, top_k=11)
        for s in samples:
            assert 0.0 <= s["uncertainty"] <= 1.0


class TestStats:
    def setup_method(self):
        self.loop = ActiveLearningLoop()

    def test_initial_stats(self):
        stats = self.loop.get_stats()
        assert stats["total_feedback"] == 0
        assert stats["false_positive_rate"] == 0.0

    def test_stats_after_feedback(self):
        self.loop.record_feedback("C-001", "BLOCK", "LEGITIMATE")  # FP
        self.loop.record_feedback("C-002", "APPROVE", "FRAUD")     # FN
        self.loop.record_feedback("C-003", "BLOCK", "FRAUD")       # CF
        self.loop.record_feedback("C-004", "APPROVE", "LEGITIMATE")  # CL

        stats = self.loop.get_stats()
        assert stats["total_feedback"] == 4
        assert stats["false_positive_rate"] == 0.25
        assert stats["false_negative_rate"] == 0.25
