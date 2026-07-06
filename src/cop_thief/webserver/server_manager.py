"""Manages uvicorn sub-processes with file-backed PID state.

State survives across CLI invocations by persisting port → PID mappings
in a JSON file.  A fresh ``ServerManager`` instance reads that file on
every call so multiple processes see a consistent view.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

_DEFAULT_STATE_FILE = Path.home() / ".cop_thief_servers.json"
SERVER_MODULE = "cop_thief.webserver.main:app"
RESERVED_PORT_MAX = 1023
MAX_PORT = 65535


@dataclass
class ServerEntry:
    """Snapshot of a managed server process."""

    port: int
    pid: int
    started_at: str
    status: str  # "running" | "stopped" | "crashed"


class ServerManager:
    """Start, stop, and list uvicorn processes.  State is file-backed.

    Args:
        state_file: Path to the JSON PID-state file.  Defaults to
            ``~/.cop_thief_servers.json``.
    """

    def __init__(self, state_file: Path | None = None) -> None:
        """Initialise the manager with an optional custom state-file path."""
        self._state_file = state_file or _DEFAULT_STATE_FILE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, port: int) -> ServerEntry:
        """Launch uvicorn on *port* and persist its PID.

        Args:
            port: TCP port in [1024, 65535].

        Raises:
            ValueError: Port is reserved/out-of-range or already running.
            RuntimeError: Subprocess failed to launch.
        """
        self._validate_port(port)
        state = self._read_state()
        if port in state:
            pid = state[port]["pid"]
            if _is_running(pid):
                raise ValueError(f"Server on port {port} is already running (pid={pid}).")

        cmd = [sys.executable, "-m", "uvicorn", SERVER_MODULE,
               "--port", str(port), "--host", "127.0.0.1"]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            raise RuntimeError(f"Failed to start uvicorn on port {port}: {exc}") from exc

        started_at = datetime.now(UTC).isoformat()
        state[port] = {"pid": proc.pid, "started_at": started_at}
        self._write_state(state)
        return ServerEntry(port=port, pid=proc.pid, started_at=started_at, status="running")

    def stop(self, port: int) -> ServerEntry:
        """Terminate the server on *port* and remove it from state.

        Args:
            port: Port of the server to stop.

        Raises:
            KeyError: No managed server on that port.
        """
        state = self._read_state()
        if port not in state:
            raise KeyError(f"No managed server on port {port}.")
        entry_data = state.pop(port)
        self._write_state(state)
        pid = entry_data["pid"]
        _kill_process(pid)
        return ServerEntry(
            port=port, pid=pid,
            started_at=entry_data["started_at"],
            status="stopped",
        )

    def list_servers(self) -> list[ServerEntry]:
        """Return all managed servers sorted by port with live status."""
        state = self._read_state()
        entries = []
        for port, data in state.items():
            pid = data["pid"]
            srv_status = "running" if _is_running(pid) else "crashed"
            entries.append(ServerEntry(
                port=port, pid=pid,
                started_at=data["started_at"],
                status=srv_status,
            ))
        return sorted(entries, key=lambda e: e.port)

    # ------------------------------------------------------------------
    # State file helpers
    # ------------------------------------------------------------------

    def _read_state(self) -> dict[int, dict]:
        """Read state file and return port-keyed dict (empty if missing)."""
        if not self._state_file.exists():
            return {}
        try:
            raw = json.loads(self._state_file.read_text())
            return {int(k): v for k, v in raw.items()}
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_state(self, state: dict[int, dict]) -> None:
        """Persist *state* to disk, creating parent dirs as needed."""
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps(state, indent=2))

    def _validate_port(self, port: int) -> None:
        """Raise ValueError if *port* is reserved or out of range."""
        if port <= RESERVED_PORT_MAX or port > MAX_PORT:
            raise ValueError(f"Port {port} is reserved or out of range [1024, {MAX_PORT}].")


# ------------------------------------------------------------------
# Cross-platform process helpers
# ------------------------------------------------------------------

def _is_running(pid: int) -> bool:
    """Return True if *pid* refers to a live process."""
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, text=True, check=False,
        )
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # process exists but we can't signal it


def _kill_process(pid: int) -> None:
    """Terminate *pid* gracefully; force-kill if it lingers."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=False,
                       capture_output=True)
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass  # already gone
