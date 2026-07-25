"""
Tests for Streaming Temporal Graph Network service.

Tests transaction processing, coordination detection, and temporal
pattern scoring without requiring full PyTorch (tests heuristic logic).
"""

import time

from services.graph_engine.streaming_tgn import (
    CoordinationScore,
    StreamingTGNService,
    TemporalEvent,
)


class TestTemporalEvent:
    def test_create_event(self):
        event = TemporalEvent(
            source_id="user_A",
            target_id="user_B",
            timestamp=1000.0,
            amount=5000.0,
        )
        assert event.source_id == "user_A"
        assert event.target_id == "user_B"
        assert event.amount == 5000.0
        assert event.event_type == "transaction"


class TestStreamingTGNService:
    def setup_method(self):
        self.service = StreamingTGNService(max_nodes=1000)

    def test_initial_state(self):
        assert self.service.node_count == 0
        assert self.service.event_count == 0

    def test_process_single_transaction(self):
        self.service.process_transaction({
            "sender_id": "user_A",
            "receiver_id": "user_B",
            "amount": 5000,
            "timestamp": time.time(),
        })
        assert self.service.node_count == 2
        assert self.service.event_count == 1

    def test_process_multiple_transactions(self):
        for i in range(5):
            self.service.process_transaction({
                "sender_id": "user_A",
                "receiver_id": f"user_{i}",
                "amount": 1000 * (i + 1),
                "timestamp": time.time() + i,
            })
        assert self.service.node_count == 6  # user_A + 5 receivers
        assert self.service.event_count == 5

    def test_skip_empty_entities(self):
        self.service.process_transaction({"amount": 5000})
        assert self.service.node_count == 0
        assert self.service.event_count == 0

    def test_entity_activity(self):
        self.service.process_transaction({
            "sender_id": "user_A",
            "receiver_id": "user_B",
            "amount": 1000,
            "timestamp": 1000.0,
        })
        self.service.process_transaction({
            "sender_id": "user_A",
            "receiver_id": "user_C",
            "amount": 2000,
            "timestamp": 1001.0,
        })

        activity = self.service.get_entity_activity("user_A")
        assert activity["transaction_count"] == 2
        assert activity["last_active"] == 1001.0
        assert activity["has_embedding"] is True

    def test_unknown_entity_activity(self):
        activity = self.service.get_entity_activity("nonexistent")
        assert activity["transaction_count"] == 0
        assert activity["last_active"] is None


class TestCoordinationDetection:
    def setup_method(self):
        self.service = StreamingTGNService(max_nodes=1000)

    def test_no_coordination_single_entity(self):
        score = self.service.get_coordination_score(["user_A"])
        assert score.score == 0.0

    def test_no_coordination_unknown_entities(self):
        score = self.service.get_coordination_score(["x", "y", "z"])
        assert score.score == 0.0

    def test_synchronized_activity(self):
        base_time = time.time()
        # All entities active within 1 second
        for i in range(5):
            self.service.process_transaction({
                "sender_id": f"ring_{i}",
                "receiver_id": "collector",
                "amount": 9500,
                "timestamp": base_time + i * 0.1,
            })

        entities = [f"ring_{i}" for i in range(5)]
        score = self.service.get_coordination_score(entities, window_hours=1.0)
        assert score.score > 0.5
        assert len(score.evidence) > 0

    def test_relay_chain_detection(self):
        base_time = time.time()
        # A→B→C→D relay chain
        chain = ["A", "B", "C", "D", "E"]
        for i in range(len(chain) - 1):
            self.service.process_transaction({
                "sender_id": chain[i],
                "receiver_id": chain[i + 1],
                "amount": 9000,
                "timestamp": base_time + i * 60,
            })

        score = self.service.get_coordination_score(chain, window_hours=1.0)
        assert score.score > 0.3

    def test_velocity_synchronization(self):
        base_time = time.time()
        # 3 entities each making exactly 5 transactions
        for entity_idx in range(3):
            for tx_idx in range(5):
                self.service.process_transaction({
                    "sender_id": f"sync_{entity_idx}",
                    "receiver_id": f"target_{entity_idx}_{tx_idx}",
                    "amount": 1000,
                    "timestamp": base_time + tx_idx,
                })

        entities = [f"sync_{i}" for i in range(3)]
        score = self.service.get_coordination_score(entities, window_hours=24.0)
        assert score.score > 0.3

    def test_no_coordination_dispersed_activity(self):
        # Entities active at very different times (beyond window)
        # and with very different activity patterns
        self.service.process_transaction({
            "sender_id": "old_user",
            "receiver_id": "target_1",
            "amount": 1000,
            "timestamp": 1000.0,
        })
        # Give old_user many more transactions to create velocity difference
        for i in range(10):
            self.service.process_transaction({
                "sender_id": "old_user",
                "receiver_id": f"target_old_{i}",
                "amount": 500,
                "timestamp": 1000.0 + i,
            })
        self.service.process_transaction({
            "sender_id": "new_user",
            "receiver_id": "target_2",
            "amount": 1000,
            "timestamp": 1000.0 + 100 * 3600,  # 100 hours later
        })

        score = self.service.get_coordination_score(
            ["old_user", "new_user"], window_hours=1.0
        )
        # temporal_sync should be 0 (dispersed), velocity should differ
        assert score.score < 0.7

    def test_coordination_score_bounded(self):
        base_time = time.time()
        for i in range(10):
            self.service.process_transaction({
                "sender_id": f"entity_{i}",
                "receiver_id": "hub",
                "amount": 9999,
                "timestamp": base_time,
            })

        entities = [f"entity_{i}" for i in range(10)]
        score = self.service.get_coordination_score(entities, window_hours=1.0)
        assert 0.0 <= score.score <= 1.0

    def test_pattern_type_classification(self):
        base_time = time.time()
        # Create relay pattern
        chain = ["R1", "R2", "R3", "R4", "R5"]
        for i in range(len(chain) - 1):
            self.service.process_transaction({
                "sender_id": chain[i],
                "receiver_id": chain[i + 1],
                "amount": 8000,
                "timestamp": base_time + i * 10,
            })

        score = self.service.get_coordination_score(chain, window_hours=1.0)
        assert score.pattern_type in ["relay_chain", "synchronized_burst", "coordinated_velocity", "unknown"]


class TestCoordinationScore:
    def test_create_score(self):
        score = CoordinationScore(
            score=0.85,
            entities=["A", "B", "C"],
            time_window_hours=24.0,
            evidence=["Relay chain detected"],
            pattern_type="relay_chain",
        )
        assert score.score == 0.85
        assert len(score.entities) == 3
        assert score.pattern_type == "relay_chain"
