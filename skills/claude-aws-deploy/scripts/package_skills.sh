#!/usr/bin/env bash
# Build one zip per Skill (for claude.ai upload or the Skills API).
# Usage: scripts/package_skills.sh <skills_dir> [out_dir]
set -euo pipefail
SKILLS_DIR="${1:-.claude/skills}"
OUT_DIR="${2:-dist}"
mkdir -p "$OUT_DIR"
python3 "$(dirname "$0")/validate_skills.py" "$SKILLS_DIR"
for dir in "$SKILLS_DIR"/*/; do
  name="$(basename "$dir")"
  (cd "$SKILLS_DIR" && zip -qr "$OLDPWD/$OUT_DIR/$name.zip" "$name" -x '*/.DS_Store' '*/__pycache__/*')
  echo "packaged $OUT_DIR/$name.zip"
done
