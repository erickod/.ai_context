import contextlib
from datetime import UTC, datetime
from pathlib import Path


class InstallSkills:
    def __init__(self, conflict_suffix_name: str = "_old_{}"):
        self._conflict_suffix_name = conflict_suffix_name

    def _symlink_skills_from_origin(
        self,
        origin_skills_path: Path,
        destin_skills_path: Path,
    ) -> bool:
        with contextlib.suppress(OSError):
            destin_skills_path.symlink_to(origin_skills_path)
            return True
        return False

    def _rename_destin_skills_path_if_in_conflict(
        self, destin_skills_path: Path
    ) -> None:
        if destin_skills_path.exists() or destin_skills_path.is_symlink():
            datetime_format = "%Y%m%d_%H%M%S"
            destin_save_suffix = self._conflict_suffix_name.format(
                datetime.now(tz=UTC).strftime(datetime_format)
            )
            rename_name = f"{destin_skills_path.name}{destin_save_suffix}"
            backup_path = destin_skills_path.with_name(rename_name)
            _ = destin_skills_path.rename(backup_path)

    def install(self, origin_skills_path: Path, destin_skills_path: Path) -> bool:
        if not destin_skills_path.parent.exists():
            return False
        self._rename_destin_skills_path_if_in_conflict(destin_skills_path)
        return self._symlink_skills_from_origin(origin_skills_path, destin_skills_path)
