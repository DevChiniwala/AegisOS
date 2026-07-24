import ast
import operator
import yaml
import os
import logging
from dataclasses import dataclass
from typing import Any, Dict
from core.schemas.transaction import TransactionCreate

logger = logging.getLogger(__name__)

SAFE_COMPARATORS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

SAFE_FUNCTIONS = {"get", "abs", "len", "min", "max", "int", "float"}


class UnsafeExpressionError(Exception):
    pass


class SafeExpressionEvaluator(ast.NodeVisitor):
    """AST-based expression evaluator that rejects dangerous constructs."""

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def evaluate(self, expression: str) -> Any:
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise UnsafeExpressionError(f"Invalid syntax: {e}")
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in self.context:
                return self.context[node.id]
            raise UnsafeExpressionError(f"Undefined variable: {node.id}")
        elif isinstance(node, ast.BoolOp):
            return self._eval_boolop(node)
        elif isinstance(node, ast.UnaryOp):
            return self._eval_unaryop(node)
        elif isinstance(node, ast.Compare):
            return self._eval_compare(node)
        elif isinstance(node, ast.BinOp):
            return self._eval_binop(node)
        elif isinstance(node, ast.Call):
            return self._eval_call(node)
        elif isinstance(node, ast.Attribute):
            return self._eval_attribute(node)
        elif isinstance(node, ast.Subscript):
            return self._eval_subscript(node)
        elif isinstance(node, ast.IfExp):
            test = self._eval_node(node.test)
            return self._eval_node(node.body) if test else self._eval_node(node.orelse)
        else:
            raise UnsafeExpressionError(f"Disallowed expression type: {type(node).__name__}")

    def _eval_boolop(self, node: ast.BoolOp) -> bool:
        if isinstance(node.op, ast.And):
            return all(self._eval_node(v) for v in node.values)
        elif isinstance(node.op, ast.Or):
            return any(self._eval_node(v) for v in node.values)
        raise UnsafeExpressionError(f"Unknown boolean operator: {type(node.op).__name__}")

    def _eval_unaryop(self, node: ast.UnaryOp) -> Any:
        operand = self._eval_node(node.operand)
        if isinstance(node.op, ast.Not):
            return not operand
        elif isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        raise UnsafeExpressionError(f"Unknown unary operator: {type(node.op).__name__}")

    def _eval_compare(self, node: ast.Compare) -> bool:
        left = self._eval_node(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            op_type = type(op)
            if op_type not in SAFE_COMPARATORS:
                raise UnsafeExpressionError(f"Disallowed comparator: {op_type.__name__}")
            right = self._eval_node(comparator)
            if not SAFE_COMPARATORS[op_type](left, right):
                return False
            left = right
        return True

    def _eval_binop(self, node: ast.BinOp) -> Any:
        left = self._eval_node(node.left)
        right = self._eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            if right == 0:
                return 0
            return left / right
        raise UnsafeExpressionError(f"Disallowed binary operator: {type(node.op).__name__}")

    def _eval_call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Attribute):
            obj = self._eval_node(node.func.value)
            method_name = node.func.attr
            if method_name not in SAFE_FUNCTIONS:
                raise UnsafeExpressionError(f"Disallowed method: {method_name}")
            method = getattr(obj, method_name, None)
            if method is None:
                raise UnsafeExpressionError(f"Object has no method: {method_name}")
            args = [self._eval_node(a) for a in node.args]
            return method(*args)
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in SAFE_FUNCTIONS:
                raise UnsafeExpressionError(f"Disallowed function: {func_name}")
            builtin = {"abs": abs, "len": len, "min": min, "max": max, "int": int, "float": float}
            if func_name not in builtin:
                raise UnsafeExpressionError(f"Unknown function: {func_name}")
            args = [self._eval_node(a) for a in node.args]
            return builtin[func_name](*args)
        raise UnsafeExpressionError(f"Disallowed call expression: {ast.dump(node.func)}")

    def _eval_attribute(self, node: ast.Attribute) -> Any:
        obj = self._eval_node(node.value)
        attr = node.attr
        if attr.startswith("_"):
            raise UnsafeExpressionError(f"Access to private attribute: {attr}")
        val = getattr(obj, attr, None)
        if val is None and isinstance(obj, dict):
            return obj.get(attr)
        return val

    def _eval_subscript(self, node: ast.Subscript) -> Any:
        obj = self._eval_node(node.value)
        key = self._eval_node(node.slice)
        return obj[key]


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
        context = {"features": features, "transaction": transaction}

        for rule in self.rules:
            name = rule.get('name')
            action = rule.get('action')
            condition = rule.get('condition', '')

            try:
                evaluator = SafeExpressionEvaluator(context)
                if evaluator.evaluate(condition):
                    return RuleResult(
                        triggered=True,
                        rule_name=name,
                        action=action,
                        reason=rule.get('reason', f"Triggered by {name}")
                    )
            except UnsafeExpressionError as e:
                logger.error(f"Rule '{name}' contains unsafe expression: {e}")
            except Exception as e:
                logger.warning(f"Rule '{name}' evaluation failed: {e}")

        return RuleResult(triggered=False, rule_name="", action="ALLOW", reason="")
