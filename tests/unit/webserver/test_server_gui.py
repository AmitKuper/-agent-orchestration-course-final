"""Unit tests for ServerGui — creates a hidden Tk window, no real processes."""

import tkinter as tk
from pathlib import Path
from unittest.mock import patch

import pytest

from cop_thief.cli.server_gui import ServerGui
from cop_thief.webserver.server_manager import ServerEntry, ServerManager


@pytest.fixture
def manager(tmp_path: Path) -> ServerManager:
    """ServerManager backed by a temp state file."""
    return ServerManager(state_file=tmp_path / "servers.json")


@pytest.fixture
def gui(manager: ServerManager):
    """Hidden ServerGui instance; destroyed after each test."""
    root = tk.Tk()
    root.withdraw()
    app = ServerGui(root, manager)
    root.update()
    yield app
    root.destroy()


# ------------------------------------------------------------------
# Initialisation
# ------------------------------------------------------------------


def test_gui_creates_without_error(gui):
    """ServerGui initialises without raising."""
    assert gui is not None


def test_status_bar_default_text(gui):
    """Status bar shows 'Ready.' on startup."""
    assert gui._status_var.get() == "Ready."


def test_tree_empty_on_no_servers(gui):
    """Treeview has no rows when no servers are managed."""
    assert gui._tree.get_children() == ()


# ------------------------------------------------------------------
# _populate
# ------------------------------------------------------------------


def test_populate_adds_rows(gui):
    """_populate inserts one row per ServerEntry."""
    entries = [
        ServerEntry(port=8100, pid=111, started_at="2026-01-01T00:00:00+00:00", status="running"),
        ServerEntry(port=8200, pid=222, started_at="2026-01-01T01:00:00+00:00", status="crashed"),
    ]
    gui._populate(entries)
    gui._root.update()
    assert len(gui._tree.get_children()) == 2


def test_populate_clears_previous_rows(gui):
    """Calling _populate twice replaces the old rows."""
    entries = [ServerEntry(port=8100, pid=1, started_at="t", status="running")]
    gui._populate(entries)
    gui._populate([])
    gui._root.update()
    assert gui._tree.get_children() == ()


def test_populate_running_tag(gui):
    """Running servers get the 'running' tag."""
    gui._populate([ServerEntry(port=8100, pid=1, started_at="t", status="running")])
    gui._root.update()
    row = gui._tree.get_children()[0]
    assert "running" in gui._tree.item(row)["tags"]


# ------------------------------------------------------------------
# _on_start
# ------------------------------------------------------------------


def test_on_start_invalid_port_sets_status(gui):
    """Non-numeric port input sets an error status instead of crashing."""
    gui._port_var.set("abc")
    gui._on_start()
    assert "valid" in gui._status_var.get().lower()


def test_on_start_calls_manager(gui, manager):
    """_on_start delegates to manager.start() with the correct port."""
    proc_mock = _mock_proc(pid=9999)
    gui._port_var.set("8300")
    with patch("subprocess.Popen", return_value=proc_mock), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        gui._on_start()
    assert any(e.port == 8300 for e in manager.list_servers())


# ------------------------------------------------------------------
# _on_stop
# ------------------------------------------------------------------


def test_on_stop_no_selection_sets_status(gui):
    """Stop with no selection sets an informational status message."""
    gui._on_stop()
    assert "select" in gui._status_var.get().lower()


def test_on_stop_removes_server(gui, manager):
    """Selecting a row and clicking Stop removes the server."""
    proc_mock = _mock_proc(pid=8888)
    with patch("subprocess.Popen", return_value=proc_mock), \
         patch("cop_thief.webserver.server_manager._is_running", return_value=False):
        manager.start(8400)
    with patch("cop_thief.webserver.server_manager._is_running", return_value=True):
        gui._refresh()
    gui._root.update()
    row = gui._tree.get_children()[0]
    gui._tree.selection_set(row)
    with patch("cop_thief.webserver.server_manager._kill_process"):
        gui._on_stop()
    assert manager.list_servers() == []


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _mock_proc(pid: int):
    """Return a minimal mock Popen."""
    from unittest.mock import MagicMock  # noqa: PLC0415
    m = MagicMock()
    m.pid = pid
    return m
