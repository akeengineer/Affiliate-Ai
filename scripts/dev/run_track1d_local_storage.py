#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from track1d_local_storage import (
    get_storage_status,
    init_storage,
    load_local_storage_config,
    reset_storage,
    seed_demo_data,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Track 1D local SQLite storage commands.")
    parser.add_argument("command", choices=("init", "reset", "seed", "status"))
    parser.add_argument("--database-path", help="Local SQLite database path override.")
    return parser


def _emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, separators=(",", ":"), ensure_ascii=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_local_storage_config(database_path_override=args.database_path)
        if args.command == "init":
            _emit(init_storage(config))
        elif args.command == "reset":
            _emit(reset_storage(config))
        elif args.command == "seed":
            _emit(seed_demo_data(config))
        else:
            _emit(get_storage_status(config))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
