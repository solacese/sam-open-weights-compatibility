#!/usr/bin/env python3
"""Offline integrity checks for current catalog, generated files and local links."""
import csv
import datetime
import pathlib
import re
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    errors = []
    with (ROOT / "models/index.csv").open() as source:
        rows = list(csv.DictReader(source))
    if not rows or len({row["model_id"] for row in rows}) != len(rows):
        errors.append("empty catalog or duplicate model IDs")
    for row in rows:
        model = row["model_id"]
        for field, value in row.items():
            if value is None or not value.strip():
                errors.append(f"{model}: missing {field}")
        if not re.fullmatch(r"[0-9a-f]{40}", row["model_revision"]):
            errors.append(f"{model}: revision is not a commit SHA")
        try:
            datetime.date.fromisoformat(row["source_checked_at"])
            assert int(row["config_context_tokens"]) > 0
        except (ValueError, AssertionError):
            errors.append(f"{model}: invalid date/context")
        if row["sam_validation"] != "not-run" or row["evidence_status"] != "publisher-documented":
            errors.append(f"{model}: live validation requires a separate reviewed evidence change")
        if row["release_state"] != "downloadable":
            errors.append(f"{model}: announcements belong on watchlist")
        for field in ("source_url", "license_url", "serving_recipe_url"):
            if urllib.parse.urlsplit(row[field]).scheme != "https":
                errors.append(f"{model}: non-HTTPS source in {field}")
        if row["model_revision"] not in row["source_url"]:
            errors.append(f"{model}: source is not pinned to revision")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            target = target.split("#", 1)[0]
            if not target or urllib.parse.urlsplit(target).scheme:
                continue
            resolved = path.parent / urllib.parse.unquote(target)
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link {target}")
    generated = subprocess.run([sys.executable, str(ROOT / "scripts/gen-model-cards.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
    if generated.returncode:
        errors.append(generated.stderr.strip() or generated.stdout.strip())
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Catalog OK: {len(rows)} candidates; generated cards and local Markdown links current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
