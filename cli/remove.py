import contextlib
from pathlib import Path


class RemoveSkills:
    def __init__(self, conflict_suffix_name: str = "_old_{}"):
        self._conflict_suffix_name = conflict_suffix_name

    def _unlink_symlink_if_exists(self, destin_skills_path: Path) -> bool:
        if not destin_skills_path.is_symlink():
            return False
        with contextlib.suppress(OSError):
            destin_skills_path.unlink()
            return True
        return False

    def _find_oldest_backup_path(self, destin_skills_path: Path) -> Path | None:
        suffix_prefix = self._conflict_suffix_name.split("{}")[0]
        pattern = f"{destin_skills_path.name}{suffix_prefix}*"
        candidates = sorted(
            destin_skills_path.parent.glob(pattern),
            key=lambda backup_path: backup_path.name,
        )
        return candidates[0] if candidates else None

    def _restore_oldest_backup_if_exists(self, destin_skills_path: Path) -> bool:
        backup_path = self._find_oldest_backup_path(destin_skills_path)
        if backup_path is None:
            return False
        with contextlib.suppress(OSError):
            _ = backup_path.rename(destin_skills_path)
            return True
        return False

    def remove(self, destin_skills_path: Path) -> bool:
        if not destin_skills_path.parent.exists():
            return False
        if not self._unlink_symlink_if_exists(destin_skills_path):
            return False
        self._restore_oldest_backup_if_exists(destin_skills_path)
        return True
