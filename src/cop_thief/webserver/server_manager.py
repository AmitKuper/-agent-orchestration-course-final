"""Manages uvicorn sub-processes — one process per port.

Callers use ``ServerManager`` to start, stop, and list servers.
All business logic is exposed through the SDK; this module must not
be imported directly by route handlers.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime

SERVER_MODULE = "cop_thief.webserver.main:app"

# Ports that the manager is not allowed to bind (reserved / privileged).
RESERVED_PORTS: frozenset[int] = frozenset(range(1, 1024))
MAX_PORT = 65535


@dataclass
class ServerEntry:
    """Snapshot of a managed server process."""

    port: int
    pid: int
    started_at: str
    status: str  # "running" | "stopped" | "crashed"


@dataclass
class ServerManager:
    """Owns uvicorn subprocesses keyed by port.

    Thread-safety: all public methods run in the FastAPI event loop
    (single-threaded); no locks are needed.
    """

    _processes: dict[int, subprocess.Popen] = field(default_factory=dict)
    _meta: dict[int, str] = field(default_factory=dict)  # port -> ISO start time

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, port: int) -> ServerEntry:
        """Launch a uvicorn process on *port* and return its entry.

        Args:
            port: TCP port to bind. Must be in [1024, 65535].

        Raises:
            ValueError: If *port* is reserved or already managed.
            RuntimeError: If the subprocess fails to launch.
        """
        self._validate_port(port)
        if port in self._processes:
            proc = self._processes[port]
            if proc.poll() is None:
                raise ValueError(f"Server on port {port} is already running (pid={proc.pid}).")
            # Previous process crashed — allow restart.
            del self._processes[port]
            del self._meta[port]

        cmd = [
            sys.executable, "-m", "uvicorn",
            SERVER_MODULE,
            "--port", str(port),
            "--host", "127.0.0.1",
        ]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            raise RuntimeError(f"Failed to start uvicorn on port {port}: {exc}") from exc

        started_at = datetime.now(UTC).isoformat()
        self._processes[port] = proc
        self._meta[port] = started_at
        return ServerEntry(port=port, pid=proc.pid, started_at=started_at, status="running")

    def stop(self, port: int) -> ServerEntry:
        """Terminate the server on *port* and return its final entry.

        Args:
            port: Port of the server to stop.

        Raises:
            KeyError: If no server is managed on *port*.
        """
        if port not in self._processes:
            raise KeyError(f"No managed server on port {port}.")
        proc = self._processes.pop(port)
        started_at = self._meta.pop(port)
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        status = "stopped" if proc.returncode in (0, -15, 1) else "crashed"
        return ServerEntry(port=port, pid=proc.pid, started_at=started_at, status=status)

    def list_servers(self) -> list[ServerEntry]:
        """Return a snapshot of all managed servers with live status.

        Crashed processes (non-zero return code while still in the dict)
        are reported with status ``"crashed"``.
        """
        entries = []
        for port, proc in self._processes.items():
            if proc.poll() is None:
                srv_status = "running"
            else:
                srv_status = "crashed"
            entries.append(
                ServerEntry(
                    port=port,
                    pid=proc.pid,
                    started_at=self._meta[port],
                    status=srv_status,
                )
            )
        return sorted(entries, key=lambda e: e.port)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_port(self, port: int) -> None:
        """Raise ValueError if *port* is out of range or reserved."""
        if port in RESERVED_PORTS or port > MAX_PORT:
            raise ValueError(f"Port {port} is reserved or out of range [1024, {MAX_PORT}].")


# Module-level singleton — imported by the SDK.
_manager = ServerManager()


def get_server_manager() -> ServerManager:
    """Return the process-wide ServerManager singleton."""
    return _manager
