#!/usr/bin/env python3
"""Install or package the same Agent Skills files for supported hosts (stdlib only)."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "tf-narration-finecut"
VERSION = "0.2.0"
BUNDLE_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/how-to-cut.md",
    "references/toolchain.md",
    "references/quality-standards.md",
    "references/review-and-learning.md",
)
AGENTS = ("codex", "claude-code", "gemini-cli", "cursor", "copilot", "opencode", "shared")


def bundle_files(source: Path) -> list[Path]:
    source = source.resolve()
    paths = [source / relative for relative in BUNDLE_FILES]
    if (source / "LICENSE").is_file():
        paths.append(source / "LICENSE")
    for path in paths:
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError(f"Missing or unsupported bundle file: {path.name}")
    if not re.search(rf"(?m)^name:\s*{re.escape(NAME)}\s*$", paths[0].read_text(encoding="utf-8")):
        raise ValueError("SKILL.md name does not match the installation directory")
    return paths


def installation_dir(agent: str, scope: str, project: Path | None = None,
                     home: Path | None = None) -> Path:
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent: {agent}")
    if scope not in {"user", "project"}:
        raise ValueError(f"Unknown scope: {scope}")
    if scope == "project":
        if project is None or not project.expanduser().is_dir():
            raise ValueError("Project scope requires --project pointing to an existing directory")
        base = project.expanduser().resolve()
        relative = {
            "codex": ".agents/skills", "shared": ".agents/skills",
            "claude-code": ".claude/skills", "gemini-cli": ".gemini/skills",
            "cursor": ".cursor/skills", "copilot": ".github/skills",
            "opencode": ".opencode/skills",
        }[agent]
    else:
        if project is not None:
            raise ValueError("--project is only used with --scope project")
        base = (home or Path.home()).expanduser()
        relative = {
            "codex": ".agents/skills", "shared": ".agents/skills",
            "claude-code": ".claude/skills", "gemini-cli": ".gemini/skills",
            "cursor": ".cursor/skills", "copilot": ".copilot/skills",
            "opencode": ".config/opencode/skills",
        }[agent]
    return base / relative / NAME


def install(destination: Path, source: Path = ROOT, dry_run: bool = False) -> Path:
    destination = destination.expanduser().absolute()
    if destination.name != NAME:
        raise ValueError(f"Destination directory must be named {NAME}")
    paths = bundle_files(source)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists; no files changed: {destination}")
    if dry_run:
        return destination
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for path in paths:
            target = destination / path.relative_to(source.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    except Exception:
        shutil.rmtree(destination)
        raise
    return destination


def standalone_instructions(source: Path) -> str:
    def rewrite(text: str) -> str:
        return re.sub(r"\[([^\]]+)\]\((?:references/)?(?:how-to-cut|toolchain|quality-standards|review-and-learning)\.md\)",
                      r"\1（见本文对应章节）", text)

    main = (source / "SKILL.md").read_text(encoding="utf-8")
    main = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", main, count=1, flags=re.S)
    sections = [
        f"# TF-Narration-Finecut 通用指令 · v{VERSION}\n\n"
        "适用于不能加载技能目录、但能读取完整文本的智能体。以下已合并技能正文及四份参考规则。\n\n"
        "执行剪辑仍需访问原片、运行本地工具并有可用转写；缺少这些能力时仅提供内容判断或剪辑建议，"
        "不要报告已经剪辑或导出。此文本不会自动提供工具、模型、长期记忆或网页审核台。\n",
        rewrite(main.strip()),
    ]
    for relative in BUNDLE_FILES:
        if relative.startswith("references/"):
            sections.append(rewrite((source / relative).read_text(encoding="utf-8").strip()))
    return "\n\n---\n\n".join(sections) + "\n"


def build(output: Path, source: Path = ROOT) -> list[Path]:
    source = source.resolve()
    paths = bundle_files(source)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{NAME}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in paths:
            entry = zipfile.ZipInfo(f"{NAME}/{path.relative_to(source).as_posix()}", (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            handle.writestr(entry, path.read_bytes())
    skill_archive = output / f"{NAME}.skill"
    shutil.copyfile(archive, skill_archive)
    instructions = output / f"{NAME}.instructions.md"
    instructions.write_text(standalone_instructions(source), encoding="utf-8")
    artifacts = [archive, skill_archive, instructions]
    checksums = output / "SHA256SUMS"
    checksums.write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts
    ), encoding="utf-8")
    return artifacts + [checksums]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    install_parser = sub.add_parser("install", help="Copy one skill into a selected host directory")
    install_parser.add_argument("--agent", choices=AGENTS, required=True)
    install_parser.add_argument("--scope", choices=("user", "project"), default="user")
    install_parser.add_argument("--project", type=Path)
    install_parser.add_argument("--destination", type=Path, help="Override with a full destination ending in the skill name")
    install_parser.add_argument("--dry-run", action="store_true")
    build_parser = sub.add_parser("build", help="Build .zip, .skill, standalone instructions and checksums")
    build_parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        if args.command == "install":
            target = args.destination or installation_dir(args.agent, args.scope, args.project)
            target = install(target, dry_run=args.dry_run)
            print(f"{'Would install to' if args.dry_run else 'Installed to'}: {target}")
        else:
            for artifact in build(args.output_dir.expanduser()):
                print(artifact)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
