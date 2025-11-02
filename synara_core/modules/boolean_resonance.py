# synara_core/modules/boolean_resonance.py
# Boole → Resonance: fuzzy logic ops + safe expression evaluator
from __future__ import annotations
from typing import Any, Dict, Callable
import ast
import operator as op
import math

# --- Fuzzy (resonance) ops on [0,1] ---
def RES_AND(a: float, b: float) -> float: return min(float(a), float(b))
def RES_OR(a: float, b: float) -> float:  return max(float(a), float(b))
def RES_NOT(a: float) -> float:           return 1.0 - float(a)
def RES_XOR(a: float, b: float) -> float: return abs(float(a) - float(b))
def RES_XNOR(a: float, b: float) -> float:return 1.0 - abs(float(a) - float(b))

# Aliases (caps & plain)
AND = RES_AND
OR  = RES_OR
NOT = RES_NOT
XOR = RES_XOR
XNOR= RES_XNOR

# --- Safe expression evaluator ---
# Supports:
# - boolean ops: and/or/not  (AND/OR/NOT also allowed via pre-normalization)
# - numeric ops: + - * / % **, unary +/-
# - comparisons: < <= > >= == !=
# - parentheses
# - names pulled from context dict
# - resonance funcs: AND/OR/NOT/XOR/XNOR, RES_*
# - math funcs: min, max, abs, round, floor, ceil, sqrt, clamp(x,lo,hi)

_ALLOWED_CALLS: Dict[str, Callable[..., Any]] = {
    "AND": AND, "OR": OR, "NOT": NOT, "XOR": XOR, "XNOR": XNOR,
    "RES_AND": RES_AND, "RES_OR": RES_OR, "RES_NOT": RES_NOT, "RES_XOR": RES_XOR, "RES_XNOR": RES_XNOR,
    "min": min, "max": max, "abs": abs, "round": round,
    "floor": math.floor, "ceil": math.ceil, "sqrt": math.sqrt,
    "clamp": lambda x, lo, hi: max(min(float(x), float(hi)), float(lo)),
}

_ALLOWED_BINOPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Mod: op.mod, ast.Pow: op.pow,
}
_ALLOWED_BOOL = {ast.And: all, ast.Or: any}
_ALLOWED_CMPOPS = {
    ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge,
    ast.Eq: op.eq, ast.NotEq: op.ne,
}

class _SafeEval(ast.NodeVisitor):
    def __init__(self, ctx: Dict[str, Any]):
        super().__init__()
        self.ctx = ctx

    def visit_Module(self, node: ast.Module):
        return self.visit(node.body[0].value)  # single expression

    def visit_Expr(self, node: ast.Expr):
        return self.visit(node.value)

    def visit_Constant(self, node: ast.Constant):
        return node.value

    def visit_Name(self, node: ast.Name):
        if node.id in self.ctx:
            return self.ctx[node.id]
        # allow booleans explicitly
        if node.id in ("True", "False"):
            return node.id == "True"
        raise NameError(f"unknown name: {node.id}")

    def visit_UnaryOp(self, node: ast.UnaryOp):
        val = self.visit(node.operand)
        if isinstance(node.op, ast.USub): return -val
        if isinstance(node.op, ast.UAdd): return +val
        if isinstance(node.op, ast.Not):  return not bool(val)
        raise ValueError("unary op not allowed")

    def visit_BoolOp(self, node: ast.BoolOp):
        vals = [bool(self.visit(v)) for v in node.values]
        fn = _ALLOWED_BOOL.get(type(node.op))
        if not fn: raise ValueError("bool op not allowed")
        return fn(vals)

    def visit_BinOp(self, node: ast.BinOp):
        fn = _ALLOWED_BINOPS.get(type(node.op))
        if not fn: raise ValueError("binop not allowed")
        return fn(self.visit(node.left), self.visit(node.right))

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        result = True
        for opnode, comparator in zip(node.ops, node.comparators):
            fn = _ALLOWED_CMPOPS.get(type(opnode))
            if not fn: raise ValueError("cmp not allowed")
            right = self.visit(comparator)
            result = result and fn(left, right)
            left = right
        return result

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("only simple calls allowed")
        name = node.func.id
        if name not in _ALLOWED_CALLS:
            raise ValueError(f"call not allowed: {name}")
        args = [self.visit(a) for a in node.args]
        return _ALLOWED_CALLS[name](*args)

    def generic_visit(self, node):
        raise ValueError(f"disallowed node: {type(node).__name__}")

def evaluate(expression: str, context: Dict[str, Any]) -> Any:
    """
    Evaluate a safe Boolean/arith expression with resonance funcs.
    Coerces 'AND','OR','NOT' to 'and','or','not' for Boolean logic,
    but also exposes AND(...) as fuzzy resonance min/max operators.
    """
    # normalize textual boolean ops (keep function names intact)
    normalized = (
        expression.replace(" AND ", " and ")
                  .replace(" OR ", " or ")
                  .replace(" NOT ", " not ")
    )
    tree = ast.parse(normalized, mode="exec")
    if not isinstance(tree, ast.Module) or len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        raise ValueError("expression must be a single expression")
    return _SafeEval(context).visit(tree)

# Quick self-test (optional)
if __name__ == "__main__":
    ctx = {"whisper_verified": True, "cited_flame": False, "resonance_score": 0.88}
    print(evaluate("(whisper_verified and cited_flame) or (resonance_score > 0.85)", ctx))  # True
    print(AND(0.7, 0.9), OR(0.7, 0.9), NOT(0.2), XNOR(0.7, 0.7))