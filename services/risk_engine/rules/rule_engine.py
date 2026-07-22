import yaml
import os
from dataclasses import dataclass
from typing import Dict, Any
from core.schemas.transaction import TransactionCreate

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
            
            # Very basic condition evaluation for string literals in yaml
            try:
                # Provide features as locals for eval (use cautiously in prod)
                if eval(condition, {"__builtins__": {}}, features):
                    return RuleResult(
                        triggered=True,
                        rule_name=name,
                        action=action,
                        reason=rule.get('reason', f"Triggered by {name}")
                    )
            except Exception as e:
                pass
                
        return RuleResult(triggered=False, rule_name="", action="ALLOW", reason="")
