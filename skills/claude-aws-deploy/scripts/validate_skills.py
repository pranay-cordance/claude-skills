#!/usr/bin/env python3
"""Validate every Skill folder under a directory.

Checks: SKILL.md exists, YAML frontmatter has name and description, name format
(lowercase letters, digits and hyphens, at most 64 characters), description at
most 1024 characters, no obvious secrets. Exit code 1 on any failure.

Usage: python validate_skills.py <skills_dir>
"""
import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SECRET_RE = re.compile(r"(AKIA[0-9A-Z]{16}|sk-ant-[A-Za-z0-9_-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def check(skill_dir: Path) -> list[str]:
    errors = []
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return [f"{skill_dir}: missing SKILL.md"]
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return [f"{md}: missing YAML frontmatter"]
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return [f"{md}: invalid YAML: {e}"]
    name, desc = meta.get("name"), meta.get("description")
    if not name or not NAME_RE.match(str(name)):
        errors.append(f"{md}: name must be lowercase letters, digits or hyphens (max 64)")
    if name and name != skill_dir.name:
        errors.append(f"{md}: name '{name}' differs from folder '{skill_dir.name}'")
    if not desc:
        errors.append(f"{md}: missing description")
    elif len(desc) > 1024:
        errors.append(f"{md}: description is {len(desc)} chars (max 1024)")
    for f in skill_dir.rglob("*"):
        if f.is_file() and f.stat().st_size < 1_000_000:
            try:
                if SECRET_RE.search(f.read_text(encoding="utf-8", errors="ignore")):
                    errors.append(f"{f}: looks like it contains a secret")
            except OSError:
                pass
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".claude/skills")
    dirs = [d for d in sorted(root.iterdir()) if d.is_dir()] if root.exists() else []
    if not dirs:
        print(f"No skills found in {root}")
        return 1
    errors = [e for d in dirs for e in check(d)]
    for e in errors:
        print("FAIL", e)
    print(f"{len(dirs)} skill(s) checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
