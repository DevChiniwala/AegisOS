from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class FraudPattern:
    pattern_name: str
    description: str
    indicators: List[str]
    fraud_type: str

class FraudKnowledgeGraph:
    def __init__(self):
        self.patterns: Dict[str, FraudPattern] = {}
        self._load_common_typologies()

    def _load_common_typologies(self):
        self.add_pattern(
            "Structuring",
            "Breaking large transactions into smaller ones to avoid reporting thresholds",
            ["multiple_transactions", "just_below_threshold", "short_timeframe"],
            "AML"
        )
        self.add_pattern(
            "Account Takeover",
            "Unauthorized access to user account",
            ["new_device", "new_ip_location", "immediate_password_change"],
            "Fraud"
        )

    def add_pattern(self, pattern_name: str, description: str, indicators: List[str], fraud_type: str) -> None:
        self.patterns[pattern_name] = FraudPattern(pattern_name, description, indicators, fraud_type)

    def match_patterns(self, features: Dict[str, Any], transaction: Any) -> List[FraudPattern]:
        # Simple rule matching
        matches = []
        return matches

    def get_related_patterns(self, pattern_name: str) -> List[FraudPattern]:
        target = self.patterns.get(pattern_name)
        if not target: return []
        
        related = []
        for p in self.patterns.values():
            if p.pattern_name != pattern_name and p.fraud_type == target.fraud_type:
                related.append(p)
        return related
