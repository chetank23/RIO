"""
solver
------
Canonical Timetable Optimization & Verification Package for RIO-MJP.
Provides:
- CP-SAT mathematical timetable scheduling engine
- Pre-solve mathematical infeasibility diagnostics
- Zero-dependency independent timetable verifier
"""

from backend.optimizer.timetable_solver import TimetableSolver, SolverResult
from backend.optimizer.validator import validate_timetable, ValidationResult
from backend.optimizer.scorer import compute_score, compute_score as calculate_timetable_score
from solver.presolve import run_presolve_checks, PresolveResult

__all__ = [
    "TimetableSolver",
    "SolverResult",
    "validate_timetable",
    "ValidationResult",
    "calculate_timetable_score",
    "compute_score",
    "run_presolve_checks",
    "PresolveResult",
]

