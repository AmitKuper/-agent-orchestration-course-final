"""Reports package — generates and serialises match reports.

External callers use the SDK or REST endpoint. Do not import sub-modules directly.
"""

from cop_thief.reports.report_builder import build_report
from cop_thief.reports.report_schema import MatchReport

__all__ = ["build_report", "MatchReport"]
