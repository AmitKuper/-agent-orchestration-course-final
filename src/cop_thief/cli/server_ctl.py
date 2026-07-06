"""Standalone CLI for starting, stopping, and listing uvicorn servers.

Usage
-----
    server-ctl list
    server-ctl start <port>
    server-ctl stop <port>

The tool reads and writes ``~/.cop_thief_servers.json`` so state
persists across separate invocations.
"""

from __future__ import annotations

import argparse
import sys

from cop_thief.webserver.server_manager import ServerEntry, ServerManager


def _print_entry(entry: ServerEntry) -> None:
    """Print a single server entry as a formatted line."""
    print(
        f"  port={entry.port:5d}  pid={entry.pid:7d}"
        f"  status={entry.status:<8}  started={entry.started_at}"
    )


def cmd_list(manager: ServerManager, _args: argparse.Namespace) -> int:
    """Print all managed servers; exit 0 even when the list is empty.

    Args:
        manager: Shared ServerManager instance.
        _args: Parsed CLI arguments (unused).

    Returns:
        Exit code (always 0).
    """
    entries = manager.list_servers()
    if not entries:
        print("No managed servers.")
        return 0
    print(f"{'PORT':<7} {'PID':<9} {'STATUS':<10} STARTED")
    print("-" * 55)
    for entry in entries:
        _print_entry(entry)
    return 0


def cmd_start(manager: ServerManager, args: argparse.Namespace) -> int:
    """Start a uvicorn server on args.port.

    Args:
        manager: Shared ServerManager instance.
        args: Parsed CLI arguments; must contain ``port`` (int).

    Returns:
        0 on success, 1 on error.
    """
    try:
        entry = manager.start(args.port)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Started server on port {entry.port} (pid={entry.pid}).")
    return 0


def cmd_stop(manager: ServerManager, args: argparse.Namespace) -> int:
    """Stop the managed server on args.port.

    Args:
        manager: Shared ServerManager instance.
        args: Parsed CLI arguments; must contain ``port`` (int).

    Returns:
        0 on success, 1 on error.
    """
    try:
        entry = manager.stop(args.port)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Stopped server on port {entry.port} (pid={entry.pid}).")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="server-ctl",
        description="Manage cop-thief uvicorn server processes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all managed servers.")

    p_start = sub.add_parser("start", help="Start a server on PORT.")
    p_start.add_argument("port", type=int, help="TCP port (1024–65535).")

    p_stop = sub.add_parser("stop", help="Stop the server on PORT.")
    p_stop.add_argument("port", type=int, help="TCP port of the running server.")

    return parser


_COMMANDS = {
    "list": cmd_list,
    "start": cmd_start,
    "stop": cmd_stop,
}


def main() -> None:
    """Entry point registered in pyproject.toml."""
    parser = _build_parser()
    args = parser.parse_args()
    manager = ServerManager()
    handler = _COMMANDS[args.command]
    sys.exit(handler(manager, args))


if __name__ == "__main__":
    main()
