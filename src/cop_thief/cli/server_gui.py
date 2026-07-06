"""Tkinter GUI for starting, stopping, and listing uvicorn servers.

Launch with:
    uv run server-gui
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from cop_thief.webserver.server_manager import ServerEntry, ServerManager

_REFRESH_MS = 3000
_COL_HEADERS = ("Port", "PID", "Status", "Started")
_COL_WIDTHS = (70, 80, 90, 200)
_STATUS_RUNNING_COLOR = "#2e7d32"
_STATUS_CRASHED_COLOR = "#c62828"


class ServerGui:
    """Main application window for the server control panel.

    Args:
        root: The tkinter root window.
        manager: ServerManager instance to delegate all process operations.
    """

    def __init__(self, root: tk.Tk, manager: ServerManager) -> None:
        """Build the UI and start the auto-refresh loop."""
        self._root = root
        self._manager = manager
        self._after_id: str | None = None
        root.title("Cop-Thief Server Control")
        root.resizable(False, False)
        self._build_ui()
        self._refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Create and grid all widgets."""
        pad = {"padx": 8, "pady": 4}

        # -- top row: port entry + start button --
        top = ttk.Frame(self._root)
        top.grid(row=0, column=0, sticky="ew", **pad)
        ttk.Label(top, text="Port:").pack(side="left")
        self._port_var = tk.StringVar()
        self._port_entry = ttk.Entry(top, textvariable=self._port_var, width=8)
        self._port_entry.pack(side="left", padx=(4, 8))
        ttk.Button(top, text="Start", command=self._on_start).pack(side="left")

        # -- server list --
        frame = ttk.Frame(self._root)
        frame.grid(row=1, column=0, sticky="nsew", **pad)
        self._tree = ttk.Treeview(
            frame, columns=_COL_HEADERS, show="headings", height=10, selectmode="browse",
        )
        for col, width in zip(_COL_HEADERS, _COL_WIDTHS):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=width, anchor="center")
        self._tree.tag_configure("crashed", foreground=_STATUS_CRASHED_COLOR)
        self._tree.tag_configure("running", foreground=_STATUS_RUNNING_COLOR)
        self._tree.pack(side="left", fill="both")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        sb.pack(side="right", fill="y")
        self._tree.configure(yscrollcommand=sb.set)

        # -- bottom row: stop + refresh buttons --
        bot = ttk.Frame(self._root)
        bot.grid(row=2, column=0, sticky="ew", **pad)
        ttk.Button(bot, text="Stop Selected", command=self._on_stop).pack(side="left", padx=(0, 8))
        ttk.Button(bot, text="Refresh", command=self._refresh).pack(side="left")

        # -- status bar --
        self._status_var = tk.StringVar(value="Ready.")
        ttk.Label(self._root, textvariable=self._status_var, anchor="w").grid(
            row=3, column=0, sticky="ew", padx=8, pady=(0, 6),
        )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        """Read the port field and start a server."""
        raw = self._port_var.get().strip()
        if not raw.isdigit():
            self._set_status("Enter a valid port number.")
            return
        port = int(raw)
        try:
            entry = self._manager.start(port)
            self._set_status(f"Started server on port {entry.port} (pid={entry.pid}).")
            self._port_var.set("")
        except (ValueError, RuntimeError) as exc:
            messagebox.showerror("Start failed", str(exc))
        self._refresh()

    def _on_stop(self) -> None:
        """Stop the server selected in the list."""
        selected = self._tree.selection()
        if not selected:
            self._set_status("Select a server to stop.")
            return
        port = int(self._tree.item(selected[0])["values"][0])
        try:
            entry = self._manager.stop(port)
            self._set_status(f"Stopped server on port {entry.port}.")
        except KeyError as exc:
            messagebox.showerror("Stop failed", str(exc))
        self._refresh()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        """Reload server list from manager and reschedule next refresh.

        Cancels any pending timer first so manual and auto refreshes don't stack.
        """
        if self._after_id is not None:
            self._root.after_cancel(self._after_id)
        self._populate(self._manager.list_servers())
        self._after_id = self._root.after(_REFRESH_MS, self._refresh)

    def _populate(self, entries: list[ServerEntry]) -> None:
        """Rebuild the treeview rows, preserving the current port selection."""
        # Remember which port is selected before clearing rows.
        selected_port: int | None = None
        sel = self._tree.selection()
        if sel:
            try:
                selected_port = int(self._tree.item(sel[0])["values"][0])
            except (IndexError, ValueError):
                pass

        self._tree.delete(*self._tree.get_children())
        for e in entries:
            tag = "running" if e.status == "running" else "crashed"
            iid = self._tree.insert(
                "", "end", values=(e.port, e.pid, e.status, e.started_at), tags=(tag,),
            )
            # Restore selection if this row matches the previously selected port.
            if e.port == selected_port:
                self._tree.selection_set(iid)
                self._tree.focus(iid)

    def _set_status(self, message: str) -> None:
        """Update the status bar text."""
        self._status_var.set(message)


def main() -> None:
    """Entry point registered in pyproject.toml as `server-gui`."""
    root = tk.Tk()
    manager = ServerManager()
    ServerGui(root, manager)
    root.mainloop()


if __name__ == "__main__":
    main()
