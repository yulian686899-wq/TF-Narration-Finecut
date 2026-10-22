import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import skill_package as package


class SkillPackageTests(unittest.TestCase):
    def test_documented_user_directories(self):
        home = Path("/example-home")
        expected = {
            "codex": ".agents/skills", "shared": ".agents/skills",
            "claude-code": ".claude/skills", "gemini-cli": ".gemini/skills",
            "cursor": ".cursor/skills", "copilot": ".copilot/skills",
            "opencode": ".config/opencode/skills",
        }
        for agent, relative in expected.items():
            with self.subTest(agent=agent):
                self.assertEqual(package.installation_dir(agent, "user", home=home),
                                 home / relative / "tf-narration-finecut")

    def test_project_install_for_all_hosts(self):
        expected = {
            "codex": ".agents/skills", "shared": ".agents/skills",
            "claude-code": ".claude/skills", "gemini-cli": ".gemini/skills",
            "cursor": ".cursor/skills", "copilot": ".github/skills",
            "opencode": ".opencode/skills",
        }
        for agent, relative in expected.items():
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as temp:
                project = Path(temp)
                result = subprocess.run([
                    sys.executable, str(ROOT / "tools/skill_package.py"), "install",
                    "--agent", agent, "--scope", "project", "--project", str(project),
                ], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                installed = project / relative / "tf-narration-finecut"
                files = {p.relative_to(installed).as_posix() for p in installed.rglob("*") if p.is_file()}
                self.assertEqual(files, set(package.BUNDLE_FILES))
                for relative_file in files:
                    self.assertEqual((installed / relative_file).read_bytes(), (ROOT / relative_file).read_bytes())

    def test_existing_install_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "tf-narration-finecut"
            target.mkdir()
            marker = target / "my-review-notes.md"
            marker.write_text("keep my edits", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                package.install(target)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep my edits")
            self.assertEqual(list(target.iterdir()), [marker])

    def test_dry_run_has_no_filesystem_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "not-created" / "tf-narration-finecut"
            package.install(target, dry_run=True)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_project_scope_requires_real_project(self):
        with self.assertRaises(ValueError):
            package.installation_dir("claude-code", "project")
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                package.installation_dir("codex", "project", Path(temp) / "missing")

    def test_folder_name_and_source_are_checked_before_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                package.install(root / "wrong-name")
            with self.assertRaises(ValueError):
                package.install(root / "tf-narration-finecut", source=root)
            self.assertEqual(list(root.iterdir()), [])

    def test_release_archives_and_checksums(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            package.build(output)
            archive = output / "tf-narration-finecut.zip"
            skill = output / "tf-narration-finecut.skill"
            self.assertEqual(archive.read_bytes(), skill.read_bytes())
            with zipfile.ZipFile(archive) as handle:
                self.assertEqual(set(handle.namelist()),
                                 {f"tf-narration-finecut/{p}" for p in package.BUNDLE_FILES})
                for relative in package.BUNDLE_FILES:
                    self.assertEqual(handle.read(f"tf-narration-finecut/{relative}"), (ROOT / relative).read_bytes())
            for line in (output / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
                digest, name = line.split("  ", 1)
                self.assertEqual(digest, hashlib.sha256((output / name).read_bytes()).hexdigest())

    def test_standalone_export_contains_all_rules_without_file_dependencies(self):
        text = package.standalone_instructions(ROOT)
        for heading in ("# 怎么剪", "# 调用什么工具", "# 标准是什么", "# 审核和复盘"):
            self.assertIn(heading, text)
        self.assertNotIn("](references/", text)
        self.assertNotIn("](quality-standards.md)", text)
        self.assertIn("不误删信息", text)
        self.assertIn("没有新反馈不视为认可", text)


if __name__ == "__main__":
    unittest.main()
