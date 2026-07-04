"""LLM agent package — communication and message generation for game turns.

All LLM calls go through the Gatekeeper. External callers use the SDK.
"""

from cop_thief.agents.communication_agent import CommunicationAgent
from cop_thief.agents.hidden_state_filter import filter_observation

__all__ = ["CommunicationAgent", "filter_observation"]
