"""SDK entry point for the cop-thief application.

All business logic is exposed through this class.
CLI tools, test scripts, REST routes, and MCP handlers must use
this SDK — never call services or agents directly.
"""

from cop_thief.shared.version import VERSION
from cop_thief.webserver.server_manager import ServerEntry, ServerManager, get_server_manager


class CopThiefSDK:
    """Top-level SDK facade.

    Instantiate once at application startup and inject into routes
    via FastAPI dependency injection.

    Concrete methods are added as each subsystem (game engine,
    orchestrator, actor, agent) is implemented in later milestones.
    """

    def __init__(self, settings, manager: ServerManager | None = None) -> None:
        """Initialise the SDK with the application settings object.

        Args:
            settings: Application settings instance.
            manager: Optional ServerManager override (used in tests).
        """
        self._settings = settings
        self._manager = manager or get_server_manager()

    @property
    def version(self) -> str:
        """Return the application version string."""
        return VERSION

    # ------------------------------------------------------------------
    # Game orchestration — implemented in Milestone 2
    # ------------------------------------------------------------------

    async def create_human_vs_server_game(self, config: dict, initiator_username: str) -> dict:
        """Create a new human-vs-server match and return its public_id.

        Raises NotImplementedError until Milestone 2.
        """
        raise NotImplementedError("Game orchestrator not yet implemented (Milestone 2).")

    async def submit_human_action(self, public_id: str, action: dict, username: str) -> dict:
        """Submit a human player action and return the updated observation.

        Raises NotImplementedError until Milestone 2.
        """
        raise NotImplementedError("Game orchestrator not yet implemented (Milestone 2).")

    # ------------------------------------------------------------------
    # Server management
    # ------------------------------------------------------------------

    def list_servers(self) -> list[ServerEntry]:
        """Return a snapshot of all managed uvicorn processes."""
        return self._manager.list_servers()

    def start_server(self, port: int) -> ServerEntry:
        """Start a uvicorn process on *port* and return its entry.

        Args:
            port: TCP port in [1024, 65535].

        Raises:
            ValueError: Port is reserved or already in use.
            RuntimeError: Subprocess failed to launch.
        """
        return self._manager.start(port)

    def stop_server(self, port: int) -> ServerEntry:
        """Stop the managed server on *port* and return its final entry.

        Args:
            port: Port of the server to stop.

        Raises:
            KeyError: No managed server on that port.
        """
        return self._manager.stop(port)
