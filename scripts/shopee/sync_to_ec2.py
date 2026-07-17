#!/usr/bin/env python3
"""Copy local Shopee JSON to EC2 and create candidate notes remotely.

The EC2 SSH target comes from ``AFFILIATE_EC2_HOST`` and defaults to the
operator's ``god-of-ai`` SSH alias. The remote repository may be overridden
with ``AFFILIATE_EC2_REPO`` when it is not ``Affiliate-Ai`` below $HOME.

Ref: codex/tasks/004-shopee-scraper.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = REPO_ROOT / ".cache" / "shopee" / "scraped"
DEFAULT_EC2_HOST = "god-of-ai"
DEFAULT_REMOTE_REPO = "Affiliate-Ai"
SAFE_REMOTE_PATH = re.compile(r"^[A-Za-z0-9._~/-]+$")


def _validate_host(host: str) -> str:
    value = host.strip()
    if (
        not value
        or value.startswith("-")
        or any(character.isspace() for character in value)
    ):
        raise ValueError("EC2 host must be a non-empty SSH host or alias without spaces")
    return value


def _validate_remote_repo(remote_repo: str) -> str:
    value = remote_repo.strip().rstrip("/")
    if not value or not SAFE_REMOTE_PATH.fullmatch(value):
        raise ValueError(
            "Remote repository path may contain only letters, numbers, '.', '_', '~', '/', or '-'"
        )
    return value


def _remote_shell_path(path: str) -> str:
    """Quote a validated remote path while preserving SSH-home expansion."""

    if path == "~":
        return "$HOME"
    if path.startswith("~/"):
        return f"$HOME/{path[2:]}"
    return shlex.quote(path)


def _display_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _run(command: Sequence[str], *, dry_run: bool) -> None:
    print(f"[SYNC] {_display_command(command)}", file=sys.stderr)
    if not dry_run:
        subprocess.run(list(command), cwd=REPO_ROOT, check=True)


def sync_to_ec2(
    input_dir: Path,
    *,
    host: str,
    remote_repo: str,
    dry_run: bool = False,
) -> dict[str, object]:
    """Upload every scraped JSON file and transform each one on EC2."""

    target_host = _validate_host(host)
    target_repo = _validate_remote_repo(remote_repo)
    scraped_files = sorted(Path(input_dir).resolve().glob("*.json"))
    if not scraped_files:
        raise FileNotFoundError(f"No scraped JSON files found in {Path(input_dir).resolve()}")

    remote_scraped_dir = str(PurePosixPath(target_repo) / ".cache/shopee/scraped")
    prepare_command = (
        f"cd {_remote_shell_path(target_repo)} && "
        "mkdir -p .cache/shopee/scraped vault/candidates"
    )
    _run(["ssh", target_host, prepare_command], dry_run=dry_run)
    _run(
        [
            "scp",
            *(str(path) for path in scraped_files),
            f"{target_host}:{remote_scraped_dir}/",
        ],
        dry_run=dry_run,
    )

    for scraped_file in scraped_files:
        remote_input = str(PurePosixPath(".cache/shopee/scraped") / scraped_file.name)
        arguments = (
            "scripts/shopee/to_candidate.py "
            f"--input {shlex.quote(remote_input)} --output-dir vault/candidates"
        )
        transform_command = (
            f"cd {_remote_shell_path(target_repo)} && "
            "if [ -x .venv/bin/python ]; then "
            f".venv/bin/python {arguments}; "
            "else "
            f"python3 {arguments}; "
            "fi"
        )
        _run(["ssh", target_host, transform_command], dry_run=dry_run)

    return {
        "status": "dry_run_ok" if dry_run else "success",
        "host": target_host,
        "files_synced": len(scraped_files),
        "remote_scraped_dir": remote_scraped_dir,
        "remote_candidates_dir": str(PurePosixPath(target_repo) / "vault/candidates"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync local Shopee scrape results to the EC2 pipeline host."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument(
        "--host",
        default=os.getenv("AFFILIATE_EC2_HOST", DEFAULT_EC2_HOST),
        help="SSH host or alias (default: AFFILIATE_EC2_HOST or god-of-ai)",
    )
    parser.add_argument(
        "--remote-repo",
        default=os.getenv("AFFILIATE_EC2_REPO", DEFAULT_REMOTE_REPO),
        help="Repository path on EC2 (default: Affiliate-Ai below SSH home)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = sync_to_ec2(
            args.input_dir,
            host=args.host,
            remote_repo=args.remote_repo,
            dry_run=args.dry_run,
        )
    except (
        FileNotFoundError,
        OSError,
        subprocess.CalledProcessError,
        ValueError,
    ) as exc:
        print(f"[ERROR] EC2 sync failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
