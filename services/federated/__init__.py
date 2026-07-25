"""
Federated AML Learning with Differential Privacy.

Enables multiple AegisOS instances to collaboratively train fraud
detection models without sharing raw transaction data.

Architecture:
- NVIDIA FLARE (NVFlare) coordinates federation
- Each client trains locally on private data
- Only model weight updates are shared (with DP noise)
- Custom FedAvg aggregator with secure aggregation
- Adaptive differential privacy (per-round epsilon tracking)

Requires: pip install aegisos[federated]
"""

from services.federated.aggregator import SecureFedAvgAggregator
from services.federated.dp_mechanism import AdaptiveDPMechanism
from services.federated.trainer import AegisFederatedTrainer

__all__ = [
    "AdaptiveDPMechanism",
    "AegisFederatedTrainer",
    "SecureFedAvgAggregator",
]
