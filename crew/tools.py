import re
import time
from pathlib import Path

from crewai.tools import BaseTool

AI_CONTEXT = Path(__file__).parent.parent

_VALID_SKILLS = {
    "task-designer", "daps-analyst", "planner", "test-analyst",
    "eng", "code-reviewer", "project-memory", "commiter", "db",
}
_VALID_DOCS = {"GUIDELINES.md", "DB.md", "DOD.md", "DOR.md", "TASK-TEMPLATE.md", "WORKFLOWS.md"}


class ReadMemoryTool(BaseTool):
    name: str = "read_project_memory"
    description: str = (
        "Reads PMEMORY.md to obtain CURRENT_STATE, last log entries, "
        "and any active BLOCKED status. Must be called before acting."
    )

    def _run(self) -> str:
        memory_file = AI_CONTEXT / "PMEMORY.md"
        if not memory_file.exists():
            return "MEMORY_EMPTY"
        return memory_file.read_text(encoding="utf-8")


class WriteMemoryTool(BaseTool):
    name: str = "write_project_memory"
    description: str = (
        "Appends a single log entry to PMEMORY.md. Call after every ACT step. "
        "Format: [YYYY-MM-DD HH:MM] <role> · <STATE> · <action ≤15 words> · ✓|⚠|✗|BLOCKED[: reason] [· artifact]"
    )

    def _run(self, entry: str) -> str:
        memory_file = AI_CONTEXT / "PMEMORY.md"
        lock_file = AI_CONTEXT / "PMEMORY.lock"

        for _ in range(10):
            if not lock_file.exists():
                break
            time.sleep(0.5)

        lock_file.touch()
        try:
            with open(memory_file, "a", encoding="utf-8") as f:
                f.write(f"{entry}\n")
        finally:
            lock_file.unlink(missing_ok=True)

        return f"Written: {entry}"


class UpdateStateTool(BaseTool):
    name: str = "update_current_state"
    description: str = (
        "Updates CURRENT_STATE in PMEMORY.md. "
        "Only call on confirmed state machine transitions."
    )

    def _run(self, new_state: str) -> str:
        memory_file = AI_CONTEXT / "PMEMORY.md"
        if not memory_file.exists():
            return "PMEMORY.md not found"

        content = memory_file.read_text(encoding="utf-8")
        content = re.sub(
            r"^CURRENT_STATE:.*",
            f"CURRENT_STATE: {new_state}",
            content,
            flags=re.MULTILINE,
        )
        memory_file.write_text(content, encoding="utf-8")
        return f"CURRENT_STATE updated to: {new_state}"


class ReadSkillTool(BaseTool):
    name: str = "read_skill"
    description: str = (
        "Reads SKILL.md for a given role. "
        f"Valid values: {', '.join(sorted(_VALID_SKILLS))}. "
        "Must be called before acting in any role."
    )

    def _run(self, skill_name: str) -> str:
        if skill_name not in _VALID_SKILLS:
            return f"Unknown skill '{skill_name}'. Valid: {', '.join(sorted(_VALID_SKILLS))}"
        skill_file = AI_CONTEXT / skill_name / "SKILL.md"
        if not skill_file.exists():
            return f"Skill file not found: {skill_name}/SKILL.md"
        return skill_file.read_text(encoding="utf-8")


class ReadDocumentTool(BaseTool):
    name: str = "read_document"
    description: str = (
        "Reads a cross-cutting reference document. "
        f"Valid values: {', '.join(sorted(_VALID_DOCS))}."
    )

    def _run(self, document: str) -> str:
        if document not in _VALID_DOCS:
            return f"Unknown document '{document}'. Valid: {', '.join(sorted(_VALID_DOCS))}"
        doc_file = AI_CONTEXT / document
        if not doc_file.exists():
            return f"Document not found: {document}"
        return doc_file.read_text(encoding="utf-8")
