import argparse
import sys
from pathlib import Path

try:
    from cli.install import InstallSkills
    from cli.remove import RemoveSkills
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from cli.install import InstallSkills
    from cli.remove import RemoveSkills

provider_paths = [
    Path(".gemini/skills"),
    Path(".claude/skills"),
    Path(".agents/skills"),
]
# Origem fixa: sempre o diretório .ai_context físico, independente de onde o
# comando é invocado (evita instalar relativo ao cwd/pai de .ai_context).
skills_path = Path(__file__).resolve().parent.parent
# Destino: sempre a home do usuário, independente de onde o comando é
# invocado (os providers leem as skills a partir de ~/.<provider>/skills).
project_root = Path.home()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli",
        description=(
            "Instala ou remove symlinks de skills (.ai_context) para os "
            "providers suportados (.gemini, .claude)."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "install", help="Cria os symlinks de skills para cada provider."
    )
    subparsers.add_parser(
        "remove", help="Remove os symlinks de skills e restaura backups originais."
    )
    return parser


def _install(
    origin_skills_path: Path, project_root: Path, destin_provider_paths: list[Path]
) -> bool:
    installer = InstallSkills()
    success = True
    for provider_path in destin_provider_paths:
        destin_skills_path = project_root / provider_path
        destin_skills_path.parent.mkdir(parents=True, exist_ok=True)
        installed = installer.install(origin_skills_path, destin_skills_path)
        print(f"{'✔' if installed else '✘'} install {destin_skills_path}")
        success = success and installed
    return success


def _remove(project_root: Path, destin_provider_paths: list[Path]) -> bool:
    remover = RemoveSkills()
    success = True
    for provider_path in destin_provider_paths:
        destin_skills_path = project_root / provider_path
        removed = remover.remove(destin_skills_path)
        print(f"{'✔' if removed else '✘'} remove {destin_skills_path}")
        success = success and removed
    return success


def main() -> int:
    args = _build_parser().parse_args()

    if args.command == "install":
        succeeded = _install(skills_path, project_root, provider_paths)
    else:
        succeeded = _remove(project_root, provider_paths)

    return 0 if succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
