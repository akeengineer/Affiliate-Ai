#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from track1c_local_backend_api import create_server
from track1c_local_backend_config import load_local_backend_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Track 1C local backend/API skeleton.")
    parser.add_argument("--host", help="Local-only host override. Defaults to AFFILIATE_BACKEND_HOST or 127.0.0.1.")
    parser.add_argument(
        "--port",
        type=int,
        help="Local-only port override. Defaults to AFFILIATE_BACKEND_PORT or 8001.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_local_backend_config(host_override=args.host, port_override=args.port)
        server = create_server(config)
    except Exception as exc:  # ponytail: keep startup failures as one-line stderr for scripts/tests.
        print(str(exc), file=sys.stderr)
        return 1

    bound_port = int(server.server_address[1])
    print(
        json.dumps(
            {
                "service": config.service,
                "runtime_mode": config.runtime_mode,
                "host": config.host,
                "port": bound_port,
                "track": config.track,
            },
            separators=(",", ":"),
            ensure_ascii=True,
        )
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
