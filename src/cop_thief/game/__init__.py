"""Game orchestration package.

Provides the runtime loop for human-vs-server and server-vs-server matches.
External callers go through ``CopThiefSDK``; do not import sub-modules directly.
"""

from cop_thief.game.orchestrator import GameOrchestrator
from cop_thief.game.state_serializer import state_from_dict, state_to_dict

__all__ = ["GameOrchestrator", "state_to_dict", "state_from_dict"]
