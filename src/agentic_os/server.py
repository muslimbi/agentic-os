from __future__ import annotations

import argparse

import uvicorn


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local GOD AI OS dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 0 < args.port < 65536:
        parser.error("--port must be between 1 and 65535.")
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        print(
            "Warning: this unauthenticated scaffold is exposed on the network.",
            flush=True,
        )
    uvicorn.run("agentic_os.api:app", host=args.host, port=args.port)
    return 0
