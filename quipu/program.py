from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .vm import QuipuVM, VMContext, Instruction


@dataclass
class QuipuProgram:
    version: str
    description: str
    secret_hex: Optional[str]
    instructions: List[Instruction]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QuipuProgram":
        version = d.get("version", "1.0")
        description = d.get("description", "")
        secret_hex = d.get("secret_hex")
        inst = [
            Instruction(op=i["op"], args=i.get("args", {}))
            for i in d.get("instructions", [])
        ]
        return cls(
            version=version,
            description=description,
            secret_hex=secret_hex,
            instructions=inst,
        )

    @classmethod
    def from_file(cls, path: str) -> "QuipuProgram":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


def run_program(
    program: QuipuProgram,
    ctx: Optional[VMContext] = None,
) -> VMContext:
    """
    Execute a QuipuProgram against a VMContext.
    If secret_hex is provided, it becomes ctx.secret (for SIGN).
    """
    ctx = ctx or VMContext()
    if program.secret_hex:
        ctx.secret = bytes.fromhex(program.secret_hex)

    vm = QuipuVM(ctx)
    vm.execute(program.instructions)
    return ctx


def run_program_file(path: str, ctx: Optional[VMContext] = None) -> VMContext:
    prog = QuipuProgram.from_file(path)
    return run_program(prog, ctx=ctx)