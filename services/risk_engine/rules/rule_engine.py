import yaml
import os
import logging
from dataclasses import dataclass
from typing import Dict
from core.schemas.transaction import TransactionCreate

logger = logging.getLogger(__name__)

@dataclass
class RuleResult:
    triggered: bool
    rule_name: str
    action: str
    reason: str

class RuleEngine:
    def __init__(self):
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        rules_path = os.path.join(os.path.dirname(__file__), 'rules.yaml')
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                data = yaml.safe_load(f)
                self.rules = data.get('rules', [])

    def evaluate(self, transaction: TransactionCreate, features: Dict[str, float]) -> RuleResult:
        for rule in self.rules:
            name = rule.get('name')
            action = rule.get('action')
            condition = rule.get('condition', '')

            try:
                context = {"features": features, "transaction": transaction, "__builtins__": {}}
                if eval(condition, context):
                    return RuleResult(
                        triggered=True,
                        rule_name=name,
                        action=action,
                        reason=rule.get('reason', f"Triggered by {name}")
                    )
            except Exception as e:
                logger.warning(f"Rule '{name}' evaluation failed: {e}")

        return RuleResult(triggered=False, rule_name="", action="ALLOW", reason="")
