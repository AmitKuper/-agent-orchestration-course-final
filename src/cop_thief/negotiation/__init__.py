"""Negotiation strategy package — pre-match config proposal and selection.

External callers use the SDK. Do not import sub-modules directly.
"""

from cop_thief.negotiation.base import NegotiationStrategy
from cop_thief.negotiation.performance_table import PerformanceTable
from cop_thief.negotiation.rule_based import RuleBasedNegotiator

__all__ = ["NegotiationStrategy", "RuleBasedNegotiator", "PerformanceTable"]
