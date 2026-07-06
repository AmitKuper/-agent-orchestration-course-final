"""SDK entry point for the cop-thief application.

All business logic is exposed through this class.
CLI tools, test scripts, REST routes, and MCP handlers must use
this SDK — never call services or agents directly.
"""

from cop_thief.shared.version import VERSION


class CopThiefSDK:
    """Top-level SDK facade.

    Instantiate once at application startup and inject into routes
    via FastAPI dependency injection.

    Concrete methods are added as each subsystem (game engine,
    orchestrator, actor, agent) is implemented in later milestones.
    """

    def __init__(self, settings) -> None:
        """Initialise the SDK with the application settings object."""
        self._settings = settings

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
