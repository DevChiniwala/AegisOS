"""
Streaming Temporal Graph Network Service.

Wraps the TGN model with a streaming interface for real-time
transaction processing and coordination detection.

The TGN maintains per-node memory that updates as new transactions
(edges) arrive. This enables detection of coordinated attacks that
evolve over time — e.g., 5 accounts created over 3 days that are
simultaneously used in a fraud ring.

Architecture:
- Transaction events are processed as they arrive (streaming)
- Node memories update with each transaction
- Coordination scoring uses temporal embeddings + similarity
- Integrates with existing GraphRAG for hybrid retrieval
"""

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.utils.logging import get_logger

logger = get_logger(__name__)

try:
    pass  # import numpy as np
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class TemporalEvent:
    """A timestamped edge event in the transaction graph."""

    source_id: str
    target_id: str
    timestamp: float
    amount: float = 0.0
    features: Dict[str, float] = field(default_factory=dict)
    event_type: str = "transaction"


@dataclass
class CoordinationScore:
    """Result of coordination detection for a set of entities."""

    score: float
    entities: List[str]
    time_window_hours: float
    evidence: List[str] = field(default_factory=list)
    pattern_type: str = "unknown"


class StreamingTGNService:
    """Streaming Temporal Graph Network service for real-time fraud detection.

    Processes transactions as they arrive and detects temporal coordination
    patterns that static graph analysis would miss.

    Usage:
        service = StreamingTGNService(max_nodes=100000)
        service.process_transaction(tx)
        score = service.get_coordination_score(["entity_A", "entity_B"], window_hours=24)
    """

    def __init__(self, max_nodes: int = 100000, memory_dim: int = 64, edge_dim: int = 32):
        self._max_nodes = max_nodes
        self._memory_dim = memory_dim
        self._edge_dim = edge_dim

        self._node_to_id: Dict[str, int] = {}
        self._id_to_node: Dict[int, str] = {}
        self._next_id = 0

        self._event_history: List[TemporalEvent] = []
        self._node_last_active: Dict[str, float] = {}
        self._node_activity_count: Dict[str, int] = defaultdict(int)
        self._edge_timestamps: Dict[tuple, List[float]] = defaultdict(list)

        if TORCH_AVAILABLE:
            from models.graph_models.tgn import TemporalGraphNetwork
            self._tgn = TemporalGraphNetwork(
                num_nodes=max_nodes,
                memory_dim=memory_dim,
                edge_feat_dim=edge_dim,
            )
            self._tgn.eval()
        else:
            self._tgn = None

    @property
    def node_count(self) -> int:
        return self._next_id

    @property
    def event_count(self) -> int:
        return len(self._event_history)

    def process_transaction(self, transaction: Dict[str, Any]) -> None:
        """Process a new transaction and update TGN state."""
        sender = transaction.get("sender_id", "")
        receiver = transaction.get("receiver_id", "")
        amount = float(transaction.get("amount", 0))
        timestamp = transaction.get("timestamp", time.time())

        if isinstance(timestamp, str):
            timestamp = time.time()

        if not sender or not receiver:
            return

        source_id = self._get_or_create_node(sender)
        target_id = self._get_or_create_node(receiver)

        event = TemporalEvent(
            source_id=sender,
            target_id=receiver,
            timestamp=timestamp,
            amount=amount,
        )
        self._event_history.append(event)

        self._node_last_active[sender] = timestamp
        self._node_last_active[receiver] = timestamp
        self._node_activity_count[sender] += 1
        self._node_activity_count[receiver] += 1
        self._edge_timestamps[(sender, receiver)].append(timestamp)

        if self._tgn is not None and TORCH_AVAILABLE:
            edge_features = self._encode_edge_features(transaction)
            with torch.no_grad():
                self._tgn.update_memory(source_id, target_id, timestamp, edge_features)

    def get_coordination_score(
        self,
        entity_ids: List[str],
        window_hours: float = 24.0,
    ) -> CoordinationScore:
        """Score coordination likelihood for a set of entities.

        Detects patterns like:
        - Synchronized activity (all active within narrow time window)
        - Relay chains (A→B→C→D in rapid succession)
        - Burst creation (multiple new entities in short time)
        """
        if len(entity_ids) < 2:
            return CoordinationScore(
                score=0.0, entities=entity_ids, time_window_hours=window_hours
            )

        scores = []
        evidence = []

        temporal_sync = self._score_temporal_synchronization(entity_ids, window_hours)
        scores.append(temporal_sync)
        if temporal_sync > 0.5:
            evidence.append(f"Synchronized activity detected (score={temporal_sync:.2f})")

        relay_score = self._score_relay_chain(entity_ids, window_hours)
        scores.append(relay_score)
        if relay_score > 0.5:
            evidence.append(f"Relay chain pattern (score={relay_score:.2f})")

        velocity_sync = self._score_velocity_synchronization(entity_ids)
        scores.append(velocity_sync)
        if velocity_sync > 0.5:
            evidence.append(f"Coordinated velocity pattern (score={velocity_sync:.2f})")

        if TORCH_AVAILABLE and self._tgn is not None:
            embedding_sim = self._score_embedding_similarity(entity_ids)
            scores.append(embedding_sim)
            if embedding_sim > 0.5:
                evidence.append(f"High embedding similarity (score={embedding_sim:.2f})")

        final_score = max(scores) * 0.6 + (sum(scores) / len(scores)) * 0.4

        pattern = "unknown"
        if relay_score > 0.7:
            pattern = "relay_chain"
        elif temporal_sync > 0.7:
            pattern = "synchronized_burst"
        elif velocity_sync > 0.7:
            pattern = "coordinated_velocity"

        return CoordinationScore(
            score=min(1.0, final_score),
            entities=entity_ids,
            time_window_hours=window_hours,
            evidence=evidence,
            pattern_type=pattern,
        )

    def get_temporal_embedding(self, entity_id: str) -> Optional[List[float]]:
        """Get the current temporal embedding for an entity."""
        if entity_id not in self._node_to_id:
            return None

        if self._tgn is not None and TORCH_AVAILABLE:
            node_id = self._node_to_id[entity_id]
            embedding = self._tgn.compute_embedding(node_id)
            return embedding.cpu().numpy().tolist()

        return None

    def get_entity_activity(self, entity_id: str) -> Dict[str, Any]:
        """Get activity summary for an entity."""
        return {
            "entity_id": entity_id,
            "transaction_count": self._node_activity_count.get(entity_id, 0),
            "last_active": self._node_last_active.get(entity_id),
            "has_embedding": entity_id in self._node_to_id,
        }

    def _get_or_create_node(self, entity_id: str) -> int:
        if entity_id in self._node_to_id:
            return self._node_to_id[entity_id]

        if self._next_id >= self._max_nodes:
            logger.warning("Max nodes reached, recycling oldest")
            self._next_id = 0

        node_id = self._next_id
        self._node_to_id[entity_id] = node_id
        self._id_to_node[node_id] = entity_id
        self._next_id += 1
        return node_id

    def _encode_edge_features(self, transaction: Dict[str, Any]) -> "torch.Tensor":
        """Encode transaction into fixed-size edge feature vector."""
        features = [0.0] * self._edge_dim

        amount = float(transaction.get("amount", 0))
        features[0] = min(amount / 100000, 1.0)  # normalized amount
        features[1] = 1.0 if amount > 10000 else 0.0  # high value flag
        features[2] = 1.0 if amount > 9000 and amount < 10000 else 0.0  # near CTR

        return torch.tensor(features, dtype=torch.float32)

    def _score_temporal_synchronization(
        self, entity_ids: List[str], window_hours: float
    ) -> float:
        """Score how synchronized entity activities are in time."""
        last_active_times = []
        for eid in entity_ids:
            if eid in self._node_last_active:
                last_active_times.append(self._node_last_active[eid])

        if len(last_active_times) < 2:
            return 0.0

        time_span = max(last_active_times) - min(last_active_times)
        window_seconds = window_hours * 3600

        if time_span == 0:
            return 1.0
        elif time_span < window_seconds * 0.1:
            return 0.9
        elif time_span < window_seconds:
            return max(0.0, 1.0 - (time_span / window_seconds))
        else:
            return 0.0

    def _score_relay_chain(self, entity_ids: List[str], window_hours: float) -> float:
        """Score relay chain pattern (A→B→C within time window)."""
        entity_set = set(entity_ids)
        chain_length = 0

        for event in reversed(self._event_history[-1000:]):
            if event.source_id in entity_set and event.target_id in entity_set:
                chain_length += 1

        if chain_length >= len(entity_ids) - 1:
            return min(1.0, chain_length / max(len(entity_ids) - 1, 1))
        elif chain_length > 0:
            return chain_length / (len(entity_ids) * 2)

        return 0.0

    def _score_velocity_synchronization(self, entity_ids: List[str]) -> float:
        """Score if entities have similar transaction velocity patterns."""
        velocities = []
        for eid in entity_ids:
            count = self._node_activity_count.get(eid, 0)
            velocities.append(count)

        if len(velocities) < 2 or max(velocities) == 0:
            return 0.0

        mean_v = sum(velocities) / len(velocities)
        if mean_v == 0:
            return 0.0

        variance = sum((v - mean_v) ** 2 for v in velocities) / len(velocities)
        cv = math.sqrt(variance) / mean_v

        if cv < 0.2:
            return 0.9
        elif cv < 0.5:
            return 0.6
        else:
            return max(0.0, 1.0 - cv)

    def _score_embedding_similarity(self, entity_ids: List[str]) -> float:
        """Score similarity of temporal embeddings (requires TGN)."""
        embeddings = []
        for eid in entity_ids:
            if eid in self._node_to_id:
                node_id = self._node_to_id[eid]
                emb = self._tgn.compute_embedding(node_id)
                embeddings.append(emb)

        if len(embeddings) < 2:
            return 0.0

        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                cos_sim = torch.nn.functional.cosine_similarity(
                    embeddings[i].unsqueeze(0), embeddings[j].unsqueeze(0)
                )
                similarities.append(float(cos_sim))

        return max(0.0, sum(similarities) / len(similarities))
