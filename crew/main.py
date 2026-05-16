#!/usr/bin/env python3
"""
Entry point for the .ai_context CrewAI workflow.

Usage:
    python -m crew.main
    python -m crew.main "describe the task here"
    python -m crew.main --daps "structural scope to analyse"
"""

import sys

from .crew import AIContextCrew

_ENTRYPOINT = """\
TASK: {task}
STATE: {state}
ROLE: auto
STATUS: {status}
MOTIVO: {motivo}"""


def _read_multiline_input(prompt: str) -> str:
    print(prompt)
    lines: list[str] = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _interactive() -> tuple[str, str, str, str]:
    task = _read_multiline_input("Task description (blank line twice to finish):")
    print("STATE [TASK_DESIGN]:", end=" ")
    state = input().strip() or "TASK_DESIGN"
    print("STATUS (READY|BLOCKED) [READY]:", end=" ")
    status = input().strip() or "READY"
    motivo = ""
    if status == "BLOCKED":
        print("MOTIVO:", end=" ")
        motivo = input().strip()
    return task, state, status, motivo


def main() -> None:
    args = sys.argv[1:]
    daps_mode = "--daps" in args

    if daps_mode:
        args = [a for a in args if a != "--daps"]
        scope = " ".join(args).strip() if args else input("DAPS scope: ").strip()
        result = AIContextCrew().run_daps(scope)
        print("\n=== DAPS RESULT ===")
        print(result)
        return

    if args:
        task, state, status, motivo = " ".join(args), "TASK_DESIGN", "READY", ""
    else:
        task, state, status, motivo = _interactive()

    if status == "BLOCKED" and not motivo:
        print("ERROR: BLOCKED status requires MOTIVO.")
        sys.exit(1)

    short_task = (task[:50] + "...") if len(task) > 50 else task
    print()
    print(_ENTRYPOINT.format(task=short_task, state=state, status=status, motivo=motivo or "N/A"))
    print()

    result = AIContextCrew().run(task)

    print("\n=== WORKFLOW COMPLETE ===")
    print(result)


if __name__ == "__main__":
    main()
