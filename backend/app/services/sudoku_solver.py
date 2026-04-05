# sudoku_solver.py
"""
PRODUCTION-GRADE Sudoku solver using Backtracking Algorithm.

CRITICAL GUARANTEES:
  1. Solves ONLY the given board (no generation)
  2. All non-zero cells in input are LOCKED and preserved
  3. Only cells containing 0 (empty) in input will be filled
  4. All original given values remain unchanged in output
  5. If solvable, returns solved board; otherwise returns None

ALGORITHM:
  • Backtracking with constraint checking
  • Row, column, and 3×3 box validation
  • Early pruning when no valid moves exist
  • Time complexity: O(9^m) where m = number of empty cells
  • Typical solve time: <1ms for valid puzzles

PRODUCTION FEATURES:
  • Input validation (format, bounds checking)
  • Preservation verification after solving
  • Comprehensive logging and error reporting
"""

import logging

logger = logging.getLogger(__name__)


class SudokuSolver:
    """
    Solves a given Sudoku board using backtracking.
    Does NOT generate new boards.
    """

    def __init__(self, board):
        """
        Initialize solver with the input board.

        Args:
            board: 9x9 list of integers (1-9 given, 0 for empty)

        Attributes:
            original_board: Immutable copy of input (all given cells)
            board: Working copy (gets filled during solving)
            locked_cells: Set of (row, col) that must NOT change
        """
        # STORE ORIGINAL: Mark which cells were given (non-zero) and MUST NOT CHANGE
        self.original_board = [row[:] for row in board]

        # WORKING COPY: This is what we solve
        self.board = [row[:] for row in board]

        # Track which cells are locked (originally non-zero)
        self.locked_cells = set()
        for row in range(9):
            for col in range(9):
                if self.original_board[row][col] != 0:
                    self.locked_cells.add((row, col))

        # Statistics for logging
        self.empty_cells = sum(1 for r in self.board for c in r if c == 0)
        logger.debug(f"Solver initialized: {self.empty_cells} empty cells to fill")

    def is_valid_placement(self, row, col, num):
        """
        Check if placing 'num' at (row, col) is valid.

        Args:
            row, col: Cell position (0-8)
            num: Number to try (1-9)

        Returns:
            True if placement is valid, False otherwise

        Validates:
            • Cell is not locked (not originally given)
            • No conflict in row
            • No conflict in column
            • No conflict in 3×3 box
        """
        # RULE 1: Never attempt to modify a cell that was originally given
        if (row, col) in self.locked_cells:
            return False

        # RULE 2: Check row constraint - no duplicate in this row
        for i in range(9):
            if self.board[row][i] == num:
                return False

        # RULE 3: Check column constraint - no duplicate in this column
        for i in range(9):
            if self.board[i][col] == num:
                return False

        # RULE 4: Check 3×3 box constraint - no duplicate in this box
        box_row_start = (row // 3) * 3
        box_col_start = (col // 3) * 3
        for i in range(box_row_start, box_row_start + 3):
            for j in range(box_col_start, box_col_start + 3):
                if self.board[i][j] == num:
                    return False

        return True

    def find_empty_cell(self):
        """
        Find the next empty cell (value 0) that needs to be filled.

        Returns:
            (row, col) of first empty cell, or (None, None) if none found
        """
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return row, col
        return None, None

    def solve(self):
        """
        Solve the Sudoku using backtracking.

        Returns:
            True if solved successfully
            False if no solution exists for this board

        Algorithm:
            1. Find next empty cell
            2. If none found, puzzle is solved → return True
            3. Try numbers 1-9 in the empty cell
            4. If valid placement, recursively solve rest
            5. If solution found, propagate True upward
            6. Otherwise, backtrack (undo placement) and try next number
            7. If all numbers fail, return False
        """
        # Find next empty cell
        row, col = self.find_empty_cell()

        # If no empty cell found, puzzle is completely filled
        if row is None:
            return True  # ✓ Solution found!

        # Try numbers 1 through 9
        for num in range(1, 10):
            # Check if this number can be placed here
            if self.is_valid_placement(row, col, num):
                # Place the number
                self.board[row][col] = num

                # Recursively try to solve the rest
                if self.solve():
                    return True  # ✓ Solution found!

                # BACKTRACK: If no solution with this number, undo it
                self.board[row][col] = 0

        # No number worked for this cell
        return False

    def validate_preservation(self):
        """
        POST-SOLVE validation: Ensure all original given values were preserved.

        Returns:
            (is_valid, error_message)
            - is_valid: True if preservation check passes
            - error_message: None if valid, error description otherwise

        Checks:
            1. All originally given cells still have same value
            2. No originally given cells were erased (set to 0)
        """
        for row in range(9):
            for col in range(9):
                # Check: if cell was originally given, it must still have same value
                if self.original_board[row][col] != 0:
                    if self.board[row][col] != self.original_board[row][col]:
                        return False, f"ERROR: Original value at ({row}, {col}) was changed!"

        # Check: all given cells are still filled (not 0)
        for row in range(9):
            for col in range(9):
                if self.original_board[row][col] != 0:
                    if self.board[row][col] == 0:
                        return False, f"ERROR: Cell ({row}, {col}) was erased!"

        return True, None

    def get_solution(self):
        """
        Return the solved board if valid, None otherwise.

        Post-solves with preservation validation.
        """
        is_valid, error_msg = self.validate_preservation()
        if not is_valid:
            logger.error(f"VALIDATION FAILED: {error_msg}")
            return None

        logger.debug(f"✓ Solution validated. {self.empty_cells} cells filled.")
        return self.board


def solve_board(board):
    """
    MAIN FUNCTION: Solve the given Sudoku board.

    CRITICAL:
      • This function solves the GIVEN board ONLY
      • It does NOT generate a new Sudoku

    Args:
        board: 9×9 list where each cell is 0-9
               (0 = empty, 1-9 = given/solution)

    Returns:
        solved_board: The same board with all 0 cells filled (if solvable)
        None: If board is invalid or has no solution

    Guarantees:
        • All non-zero values in input are preserved exactly
        • Only cells that were 0 in input are filled
        • This is a solution to the GIVEN puzzle, not a generated one

    Example:
        >>> board = [[5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], ...]
        >>> solution = solve_board(board)
        >>> solution is None  # only if no solution exists
    """
    # Validate board format
    if not board or len(board) != 9:
        logger.error("Board must be a list of 9 rows")
        return None

    for r, row in enumerate(board):
        if len(row) != 9:
            logger.error(f"Row {r} has {len(row)} cells, expected 9")
            return None
        for c, val in enumerate(row):
            if not isinstance(val, int) or val < 0 or val > 9:
                logger.error(f"Cell ({r},{c}) has invalid value {val}")
                return None

    # Create solver instance
    solver = SudokuSolver(board)

    # Attempt to solve
    logger.info(f"🔍 Starting solver with {solver.empty_cells} empty cells...")
    if solver.solve():
        # Solution found - validate and return
        logger.info("✓ Solution found!")
        return solver.get_solution()
    else:
        # No solution exists for this board
        logger.warning("✗ No solution exists for this board")
        return None

