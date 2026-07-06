"""Unit tests for ServerManager — uses tmp state file and mock subprocesses."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cop_thief.webserver.server_manager import ServerManager


def _mock_proc(pid: int = 12345) -> MagicMock:
    """Return a mock Popen with a fixed pid."""
    proc = MagicMock()
    proc.pid = pid
    return proc


@pytest.fixture
def manager(tmp_path: Path) -> ServerManager:
    """Fresh ServerManager backed by a temporary state file."""
    return ServerManager(state_file=tmp_path / "servers.json")


def _running(pid: int) -> bool:  # noqa: D401
    """Simulate _is_running returning True for specific pid."""
    return True


# ------------------------------------------------------------------
# start()
# ------------------------------------------------------------------


def test_start_returns_entry(manager):
    """start() returns a ServerEntry with correct port, pid, and status."""
    proc = _mock_proc(pid=9001)
    with patch("subprocess.Popen", return_value=proc), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        entry = manager.start(8100)
    assert entry.port == 8100
    assert entry.pid == 9001
    assert entry.status == "running"


def test_start_persists_state(manager):
    """State file is written after start()."""
    proc = _mock_proc(pid=9002)
    with patch("subprocess.Popen", return_value=proc), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8101)
    assert manager._state_file.exists()


def test_start_duplicate_running_raises(manager):
    """Starting the same port while it is running raises ValueError."""
    proc = _mock_proc(pid=9003)
    with patch("subprocess.Popen", return_value=proc), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8102)
    with patch("cop_thief.webserver.server_manager._is_running", return_value=True), \
         pytest.raises(ValueError, match="already running"):
        manager.start(8102)


def test_start_reserved_port_raises(manager):
    """Port ≤ 1023 raises ValueError without touching the state file."""
    with pytest.raises(ValueError, match="reserved"):
        manager.start(80)


def test_start_crashed_process_allows_restart(manager):
    """A previously crashed entry (pid not running) can be restarted."""
    proc1 = _mock_proc(pid=9004)
    proc2 = _mock_proc(pid=9005)
    with patch("subprocess.Popen", return_value=proc1), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8103)
    with patch("subprocess.Popen", return_value=proc2), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        entry = manager.start(8103)
    assert entry.pid == 9005


# ------------------------------------------------------------------
# stop()
# ------------------------------------------------------------------


def test_stop_returns_entry(manager):
    """stop() returns a ServerEntry and removes port from state."""
    proc = _mock_proc(pid=9006)
    with patch("subprocess.Popen", return_value=proc), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8104)
    with patch("cop_thief.webserver.server_manager._kill_process"):
        entry = manager.stop(8104)
    assert entry.port == 8104
    assert entry.pid == 9006


def test_stop_removes_from_state(manager):
    """Stopped server is absent from the next list_servers() call."""
    proc = _mock_proc(pid=9007)
    with patch("subprocess.Popen", return_value=proc), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8105)
    with patch("cop_thief.webserver.server_manager._kill_process"):
        manager.stop(8105)
    assert manager.list_servers() == []


def test_stop_unknown_port_raises(manager):
    """Stopping a port with no state entry raises KeyError."""
    with pytest.raises(KeyError):
        manager.stop(9999)


# ------------------------------------------------------------------
# list_servers()
# ------------------------------------------------------------------


def test_list_servers_empty_initially(manager):
    """list_servers() returns an empty list when state file is missing."""
    assert manager.list_servers() == []


def test_list_servers_sorted_by_port(manager):
    """list_servers() returns entries in ascending port order."""
    procs = [_mock_proc(pid=i) for i in range(9010, 9013)]
    ports = [8200, 8100, 8150]
    with patch("subprocess.Popen", side_effect=procs), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        for port in ports:
            manager.start(port)
    with patch("cop_thief.webserver.server_manager._is_running", return_value=True):
        result = [e.port for e in manager.list_servers()]
    assert result == sorted(ports)


def test_list_servers_crashed_process_status(manager):
    """A pid that is no longer running is reported as 'crashed'."""
    proc = _mock_proc(pid=9013)
    with patch("subprocess.Popen", return_value=proc), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8201)
    # _is_running returns False → process has crashed
    with patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        entries = manager.list_servers()
    assert entries[0].status == "crashed"
