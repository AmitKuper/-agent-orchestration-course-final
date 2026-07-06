"""Unit tests for ServerManager — uses mock subprocesses to avoid real ports."""

from unittest.mock import MagicMock, patch

import pytest

from cop_thief.webserver.server_manager import ServerManager


def _mock_proc(pid: int = 12345, returncode: int | None = None) -> MagicMock:
    """Return a mock Popen with controllable poll() behaviour."""
    proc = MagicMock()
    proc.pid = pid
    proc.returncode = returncode
    proc.poll.return_value = returncode  # None = still running
    return proc


@pytest.fixture
def manager() -> ServerManager:
    """Fresh ServerManager with no managed processes."""
    return ServerManager()


# ------------------------------------------------------------------
# start()
# ------------------------------------------------------------------


def test_start_returns_entry(manager):
    """start() returns a ServerEntry with the correct port and pid."""
    proc = _mock_proc(pid=9001)
    with patch("subprocess.Popen", return_value=proc):
        entry = manager.start(8100)
    assert entry.port == 8100
    assert entry.pid == 9001
    assert entry.status == "running"


def test_start_records_server(manager):
    """A started server appears in list_servers()."""
    proc = _mock_proc(pid=9002)
    with patch("subprocess.Popen", return_value=proc):
        manager.start(8101)
    entries = manager.list_servers()
    assert any(e.port == 8101 for e in entries)


def test_start_duplicate_port_raises(manager):
    """Starting the same port twice while the process is running raises ValueError."""
    proc = _mock_proc(pid=9003)
    with patch("subprocess.Popen", return_value=proc):
        manager.start(8102)
    with pytest.raises(ValueError, match="already running"):
        manager.start(8102)


def test_start_reserved_port_raises(manager):
    """Port below 1024 raises ValueError."""
    with pytest.raises(ValueError, match="reserved"):
        manager.start(80)


def test_start_crashed_process_can_restart(manager):
    """If the previous process crashed, start() allows a restart on the same port."""
    crashed = _mock_proc(pid=9004, returncode=1)
    new_proc = _mock_proc(pid=9005)
    with patch("subprocess.Popen", side_effect=[crashed, new_proc]):
        manager.start(8103)
        # Simulate the process crashing
        crashed.poll.return_value = 1
        entry = manager.start(8103)
    assert entry.pid == 9005


# ------------------------------------------------------------------
# stop()
# ------------------------------------------------------------------


def test_stop_returns_entry(manager):
    """stop() returns a ServerEntry with status 'stopped'."""
    proc = _mock_proc(pid=9006)
    with patch("subprocess.Popen", return_value=proc):
        manager.start(8104)
    proc.poll.return_value = -15  # SIGTERM
    proc.returncode = -15
    entry = manager.stop(8104)
    assert entry.port == 8104
    assert entry.status == "stopped"


def test_stop_removes_from_list(manager):
    """Stopped server no longer appears in list_servers()."""
    proc = _mock_proc(pid=9007)
    with patch("subprocess.Popen", return_value=proc):
        manager.start(8105)
    proc.poll.return_value = -15
    proc.returncode = -15
    manager.stop(8105)
    assert not any(e.port == 8105 for e in manager.list_servers())


def test_stop_unknown_port_raises(manager):
    """Stopping a port that was never started raises KeyError."""
    with pytest.raises(KeyError):
        manager.stop(9999)


# ------------------------------------------------------------------
# list_servers()
# ------------------------------------------------------------------


def test_list_servers_empty_initially(manager):
    """list_servers() returns an empty list on a fresh manager."""
    assert manager.list_servers() == []


def test_list_servers_sorted_by_port(manager):
    """list_servers() returns entries sorted ascending by port."""
    procs = [_mock_proc(pid=i) for i in range(9010, 9013)]
    ports = [8200, 8100, 8150]
    with patch("subprocess.Popen", side_effect=procs):
        for port in ports:
            manager.start(port)
    result_ports = [e.port for e in manager.list_servers()]
    assert result_ports == sorted(ports)


def test_list_servers_crashed_process_shown(manager):
    """A crashed process (poll != None) is reported with status 'crashed'."""
    proc = _mock_proc(pid=9013)
    with patch("subprocess.Popen", return_value=proc):
        manager.start(8201)
    proc.poll.return_value = 1  # process exited
    entries = manager.list_servers()
    assert entries[0].status == "crashed"
