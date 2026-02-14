"""Generate autosummary module lists for Sphinx API docs."""

from __future__ import annotations

import importlib
import pkgutil
import sys
from collections import defaultdict
from pathlib import Path

PACKAGE = "validation_and_pipelines"

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
OUTPUT_PATH = REPO_ROOT / "docs" / "source" / "api" / "_module_list.rst"
GENERATED_DIR = REPO_ROOT / "docs" / "source" / "api" / "_generated"
GENERATED_MEMBERS_DIR = GENERATED_DIR / "_members"

sys.path.insert(0, str(SRC_ROOT))


def _iter_modules() -> list[tuple[str, bool]]:
    package = importlib.import_module(PACKAGE)
    return [(mod.name, mod.ispkg) for mod in pkgutil.walk_packages(package.__path__, package.__name__ + ".")]


def _group_modules(modules: list[tuple[str, bool]]) -> dict[str, list[tuple[str, bool]]]:
    grouped: dict[str, list[tuple[str, bool]]] = defaultdict(list)
    for name, is_pkg in modules:
        suffix = name[len(PACKAGE) + 1 :]
        top = suffix.split(".", 1)[0]
        grouped[top].append((name, is_pkg))
    return grouped


def _write_group(fp, title: str, entries: list[tuple[str, bool]]) -> None:
    fp.write(f"{title}\n")
    fp.write(f"{'-' * len(title)}\n\n")

    packages = sorted({name for name, is_pkg in entries if is_pkg})
    modules = sorted({name for name, is_pkg in entries if not is_pkg})

    if packages:
        fp.write(".. autosummary::\n")
        fp.write("    :toctree: _generated\n")
        fp.write("    :template: package\n\n")
        for name in packages:
            fp.write(f"    {name}\n")
        fp.write("\n")

    if modules:
        fp.write(".. autosummary::\n")
        fp.write("    :toctree: _generated\n")
        fp.write("    :template: module\n\n")
        for name in modules:
            fp.write(f"    {name}\n")
        fp.write("\n")


def main() -> None:
    """Generate the autosummary module list for the API reference."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_MEMBERS_DIR.mkdir(parents=True, exist_ok=True)
    modules = _iter_modules()
    grouped = _group_modules(modules)

    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        fp.write(".. This file is auto-generated. Do not edit by hand.\n\n")

        _write_group(fp, "Core", grouped.get("core", []))
        _write_group(fp, "Dataframe Validation", grouped.get("dataframe_validation", []))
        _write_group(fp, "Domains", grouped.get("domains", []))

        fp.write("Orchestration\n")
        fp.write("-------------\n\n")
        fp.write(".. autosummary::\n")
        fp.write("    :toctree: _generated\n")
        fp.write("    :template: module\n\n")
        fp.write(f"    {PACKAGE}.main\n")
        fp.write(f"    {PACKAGE}.registry\n\n")

        _write_group(fp, "Utilities", grouped.get("utils", []))


if __name__ == "__main__":
    main()
