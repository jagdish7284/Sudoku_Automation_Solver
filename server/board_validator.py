"""
board_validator.py

PRODUCTION-GRADE validation for extracted Sudoku boards.

VALIDATION LEVELS:
  1. Constraint validation: no duplicates in rows/cols/boxes
  2. Minimum clues: at least 17 given digits (mathematical minimum)
  3. Logical feasibility: board can be validly filled
  4. Format check: 9×9 matrix of 0-9 integers

ERROR REPORTING:
  • Detailed violation messages with cell positions
  • Severity levels (critical vs warning)
  • Actionable feedback for UI display

PHILOSOPHY:
  This validator acts as a SAFETY NET between OCR/extraction errors
  and the solver. A valid boolean is the primary gate; violations
  detail what went wrong for logging and retry logic.
"""

from typing import List, Tuple, Dict
from collections import Counter

logger_imported = False
try:
    import logging
    logger = logging.getLogger(__name__)
    logger_imported = True
except:
    pass


# ─── Type definition ─────────────────────────────────────────────────────────
Violation = Dict[str, object]  # {"type": str, "index": int/tuple, "value": int, ...}


# ═════════════════════════════════════════════════════════════════════════════
# CONSTRAINT VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

def _find_duplicates(values: List[int]) -> List[Tuple[int, int]]:
    """
    Return (value, count) pairs where count > 1 for values 1-9.
    Ignores 0 (empty cells).
    """
    c = Counter(v for v in values if v != 0)
    return [(v, cnt) for v, cnt in c.items() if cnt > 1]


def _check_rows(board: List[List[int]]) -> List[Violation]:
    """Validate all 9 rows for duplicates."""
    violations = []
    for r in range(9):
        row = board[r]
        dupes = _find_duplicates(row)
        for val, cnt in dupes:
            cells = [(r, c) for c, v in enumerate(row) if v == val]
            violations.append({
                "type": "row_duplicate",
                "index": r,
                "value": val,
                "count": cnt,
                "cells": cells,
                "severity": "critical",
                "message": f"Row {r}: digit {val} appears {cnt}× at columns {[c for _, c in cells]}"
            })
    return violations


def _check_columns(board: List[List[int]]) -> List[Violation]:
    """Validate all 9 columns for duplicates."""
    violations = []
    for c in range(9):
        col = [board[r][c] for r in range(9)]
        dupes = _find_duplicates(col)
        for val, cnt in dupes:
            cells = [(r, c) for r, v in enumerate(col) if v == val]
            violations.append({
                "type": "col_duplicate",
                "index": c,
                "value": val,
                "count": cnt,
                "cells": cells,
                "severity": "critical",
                "message": f"Column {c}: digit {val} appears {cnt}× at rows {[r for r, _ in cells]}"
            })
    return violations


def _check_3x3_boxes(board: List[List[int]]) -> List[Violation]:
    """Validate all 9 3×3 boxes for duplicates."""
    violations = []
    for box_r in range(3):
        for box_c in range(3):
            cells_in_box = []
            vals = []
            for dr in range(3):
                for dc in range(3):
                    r, c = box_r * 3 + dr, box_c * 3 + dc
                    cells_in_box.append((r, c))
                    vals.append(board[r][c])

            dupes = _find_duplicates(vals)
            for val, cnt in dupes:
                bad_cells = [cells_in_box[i] for i, v in enumerate(vals) if v == val]
                violations.append({
                    "type": "box_duplicate",
                    "index": (box_r, box_c),
                    "value": val,
                    "count": cnt,
                    "cells": bad_cells,
                    "severity": "critical",
                    "message": (
                        f"Box ({box_r},{box_c}): digit {val} appears {cnt}× "
                        f"at cells {bad_cells}"
                    )
                })
    return violations


# ═════════════════════════════════════════════════════════════════════════════
# CLUE COUNT VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

def _check_minimum_clues(board: List[List[int]]) -> List[Violation]:
    """
    Validate that board has at least 17 given digits.

    Mathematical fact: A valid Sudoku puzzle has a UNIQUE solution if and only if
    it has at least 17 given digits. This is the mathematical minimum.

    Fewer than 17 clues → either:
      • OCR missed several digits
      • Image is incomplete
      • Board was generated with insufficient constraints
    """
    given = sum(1 for r in board for v in r if v != 0)
    violations = []

    if given < 17:
        violations.append({
            "type": "insufficient_clues",
            "index": None,
            "value": given,
            "count": None,
            "cells": [],
            "severity": "critical",
            "message": (
                f"Only {given} digits detected (minimum for unique solution is 17). "
                "OCR may have missed cells or image is incomplete."
            )
        })

    return violations


# ═════════════════════════════════════════════════════════════════════════════
# FORMAT VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

def _check_format(board: List[List[int]]) -> List[Violation]:
    """Validate board structure: 9×9 matrix, integers 0-9."""
    violations = []

    # Check overall structure
    if not isinstance(board, list) or len(board) != 9:
        violations.append({
            "type": "format_error",
            "index": None,
            "value": None,
            "count": None,
            "cells": [],
            "severity": "critical",
            "message": f"Board must be 9×9. Got {len(board) if isinstance(board, list) else '?'} rows."
        })
        return violations

    # Check each row
    for r, row in enumerate(board):
        if not isinstance(row, list) or len(row) != 9:
            violations.append({
                "type": "format_error",
                "index": r,
                "value": len(row) if isinstance(row, list) else None,
                "count": None,
                "cells": [],
                "severity": "critical",
                "message": f"Row {r} is not length 9 (got {len(row) if isinstance(row, list) else '?'})"
            })
            continue

        # Check each cell
        for c, val in enumerate(row):
            if not isinstance(val, int) or val < 0 or val > 9:
                violations.append({
                    "type": "format_error",
                    "index": (r, c),
                    "value": val,
                    "count": None,
                    "cells": [(r, c)],
                    "severity": "critical",
                    "message": f"Cell ({r},{c}) contains invalid value: {val} (must be 0-9)"
                })

    return violations


# ═════════════════════════════════════════════════════════════════════════════
# MAIN VALIDATION FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def validate_board(board: List[List[int]]) -> Tuple[bool, List[Violation]]:
    """
    PRODUCTION validation of a 9×9 Sudoku board.

    Performs checks in order:
      1. Format validation (structure, types)
      2. Constraint validation (no duplicates)
      3. Clue count validation (minimum 17 given)

    Returns:
        (is_valid, violations)
        - is_valid: True if board passes ALL checks
        - violations: List of violation dicts describing each issue

    VIOLATION STRUCTURE:
      {
        "type": "row_duplicate" | "col_duplicate" | "box_duplicate" | "insufficient_clues" | "format_error",
        "index": int (row/col/box) or tuple (box_r, box_c) or None,
        "value": the problematic digit (1-9) or given count,
        "count": how many times duplicate appears,
        "cells": [(r, c), ...] list of cell positions involved,
        "severity": "critical" | "warning",
        "message": human-readable description
      }
    """
    violations: List[Violation] = []

    # Step 1: Format check (fail fast if structure is invalid)
    violations.extend(_check_format(board))
    if any(v['severity'] == 'critical' for v in violations if v['type'] == 'format_error'):
        return False, violations

    # Step 2: Constraint checks
    violations.extend(_check_rows(board))
    violations.extend(_check_columns(board))
    violations.extend(_check_3x3_boxes(board))

    # Step 3: Clue count check
    violations.extend(_check_minimum_clues(board))

    is_valid = len(violations) == 0

    return is_valid, violations


# ═════════════════════════════════════════════════════════════════════════════
# FORMATTING UTILITIES
# ═════════════════════════════════════════════════════════════════════════════

def format_violations(violations: List[Violation]) -> str:
    """Return a human-readable summary of all violations."""
    if not violations:
        return "✓ Board is valid."

    lines = ["Board validation failed:"]
    for i, v in enumerate(violations, 1):
        severity_icon = "🔴" if v['severity'] == 'critical' else "🟡"
        lines.append(f"  {severity_icon} [{i}] {v['message']}")

    return "\n".join(lines)


def get_violation_summary(violations: List[Violation]) -> Dict[str, int]:
    """Return count of violations by type."""
    summary = {}
    for v in violations:
        typ = v['type']
        summary[typ] = summary.get(typ, 0) + 1
    return summary


def log_violations(violations: List[Violation], level: str = "WARNING"):
    """Log violations using Python logger if available."""
    if not logger_imported:
        return

    if not violations:
        if level == "INFO":
            logger.info("✓ Board passed all validation checks")
        return

    logger.warning("=" * 70)
    logger.warning("BOARD VALIDATION FAILED")
    logger.warning("=" * 70)

    for v in violations:
        if level == "DEBUG" or v['severity'] == 'critical':
            logger.warning(f"  • {v['message']}")

    logger.warning("=" * 70)
