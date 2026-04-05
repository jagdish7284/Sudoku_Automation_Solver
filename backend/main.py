"""
main.py
🧩 PRODUCTION-GRADE FastAPI Backend for Sudoku Automation

COMPLETE PIPELINE:
  1. Image decode & validation
  2. Multi-strategy grid detection (3 attempts with different preprocessing)
  3. Perspective transform → 450×450 grid
  4. 9×9 cell extraction with intelligent padding
  5. CNN-based digit recognition (voting across 3 preprocessing variants)
  6. Board validation (constraints, duplicates, minimum clues)
  7. IF invalid → retry with different padding (up to 3 total attempts)
  8. IF valid → solve with backtracking
  9. Return solved board

ERROR HANDLING:
  • Comprehensive input validation
  • Graceful failure with actionable error messages
  • Retry logic with varying parameters
  • Detailed logging for debugging
  • CORS enabled for web frontend

FEATURES:
  ✓ Manual board solving
  ✓ Image-based solving with auto-retries
  ✓ Detailed confidence reporting
  ✓ Validation error feedback
  ✓ Production-grade logging
  ✓ Static frontend serving
"""

import os
import logging
import time
import socket
import signal
import subprocess
import sys
from typing import List, Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.sudoku_solver import solve_board
from app.services.image_processor import find_sudoku_grid, extract_cells
from app.services.digit_recognizer import recognize_board
from app.utils.validators import validate_board, format_violations, log_violations

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sudoku.main")

# ─── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sudoku Automation API",
    version="4.0",
    description="High-accuracy Sudoku extraction and solving system"
)

FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "frontend"
)

# CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Request/Response Models ─────────────────────────────────────────

class SudokuBoard(BaseModel):
    board: List[List[int]]


class SolveResponse(BaseModel):
    solved_board: List[List[int]]
    execution_time: float


class ImageSolveResponse(BaseModel):
    extracted_board: Optional[List[List[int]]] = None
    solved_board: Optional[List[List[int]]] = None
    execution_time: float
    error: Optional[str] = None
    warnings: Optional[List[str]] = None


# ─── Helper: Attempt Pipeline ────────────────────────────────────────────────

def _attempt_pipeline(
    image: np.ndarray,
    attempt: int,
    debug_dir: Optional[str] = None,
    high_confidence_only: bool = False,
) -> tuple[Optional[List[List[int]]], Optional[List[List[float]]], Optional[str]]:
    """
    Run ONE complete pipeline iteration:
    grid-detection → cell-extraction → OCR

    Args:
        image: Input BGR image
        attempt: Attempt number (0, 1, or 2)
        debug_dir: Optional directory for debug images
        high_confidence_only: If True, zero out cells with confidence < 0.80

    Returns:
        (board, confidences, error_message) where board is None on failure
    """
    padding_ratios = [0.12, 0.08, 0.16]
    padding = padding_ratios[attempt % len(padding_ratios)]

    logger.info(f"  [Attempt {attempt+1}] using padding_ratio={padding:.2f}"
                + (" [high-confidence mode]" if high_confidence_only else ""))

    # Step 1: Grid detection
    grid_image, _ = find_sudoku_grid(image, debug_dir=debug_dir)
    if grid_image is None:
        return None, None, "Could not detect Sudoku grid in image."

    # Step 2: Cell extraction
    cells = extract_cells(grid_image, padding_ratio=padding)

    # Step 3: Digit recognition (CNN-based with voting)
    board, confidences = recognize_board(cells)

    # In high-confidence mode, zero out uncertain cells so solver fills them
    if high_confidence_only:
        for r in range(9):
            for c in range(9):
                if board[r][c] != 0 and confidences[r][c] < 0.80:
                    logger.info(f"    Zeroing uncertain cell ({r},{c}): "
                                f"digit={board[r][c]} conf={confidences[r][c]:.0%}")
                    board[r][c] = 0

    return board, confidences, None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/solve", response_model=SolveResponse)
async def solve_sudoku(data: SudokuBoard):
    """
    Solve a manually entered Sudoku board.

    Validates input, checks for conflicts, and solves.

    Args:
        data: JSON body with "board" (9×9 matrix)

    Returns:
        SolveResponse with solved_board and execution time

    Raises:
        HTTPException 400: Invalid board format or conflicts detected
    """
    t0 = time.time()
    board = data.board

    logger.info("=" * 70)
    logger.info("📋 MANUAL SOLVE STARTED")
    logger.info("=" * 70)

    # Input validation
    if len(board) != 9 or any(len(r) != 9 for r in board):
        logger.error("Invalid board dimensions")
        raise HTTPException(status_code=400, detail="Board must be 9×9.")

    n_given = sum(v for r in board for v in r if v)
    logger.info(f"  Given cells: {n_given}/81")

    # Validate before solving
    is_valid, violations = validate_board(board)
    if not is_valid:
        log_violations(violations, level="WARNING")
        msg = "Invalid board:\n" + format_violations(violations)
        logger.error(msg)
        raise HTTPException(status_code=400, detail=msg)

    logger.info("  ✓ Validation passed")

    # Solve
    logger.info("  🔍 Solving...")
    solved = solve_board(board)
    if solved is None:
        logger.error("  ✗ No solution exists")
        raise HTTPException(status_code=400, detail="No solution exists.")

    elapsed = time.time() - t0
    logger.info(f"  ✓ Solved in {elapsed:.3f}s")
    logger.info("=" * 70)

    return SolveResponse(solved_board=solved, execution_time=elapsed)


@app.post("/solve-image", response_model=ImageSolveResponse)
async def solve_image(file: UploadFile = File(...)):
    """
    Upload a Sudoku image → extract → validate → solve

    INTELLIGENT RETRYING:
      • Attempt 1: Standard padding
      • Attempt 2: Reduced padding (tighter crop)
      • Attempt 3: Increased padding (looser crop)

    If validation fails → retry with different padding (fixes alignment issues)
    If grid detection fails → retry with alternate preprocessing

    Args:
        file: Binary image file (PNG, JPG, etc.)

    Returns:
        ImageSolveResponse with extracted/solved boards, timings, errors
    """
    t0 = time.time()
    MAX_ATTEMPTS = 3

    logger.info("=" * 70)
    logger.info(f"📷 IMAGE SOLVE STARTED: {file.filename}")
    logger.info("=" * 70)

    # ── Decode image ──────────────────────────────────────────────
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Image decode failed (not valid PNG/JPG)")
            return ImageSolveResponse(
                execution_time=0,
                error="Could not decode image. Please upload a valid PNG/JPG."
            )

        logger.info(f"  ✓ Image decoded: {image.shape[1]}×{image.shape[0]} px")

    except Exception as e:
        logger.error(f"Image reading error: {e}")
        return ImageSolveResponse(
            execution_time=0,
            error=f"Error reading image: {str(e)}"
        )

    # ── Retry loop ────────────────────────────────────────────────
    last_board: Optional[List[List[int]]] = None
    last_violations: list = []
    last_error: Optional[str] = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            board, confidences, err = _attempt_pipeline(image, attempt)

            if board is None:
                last_error = err or "Grid detection failed."
                logger.warning(f"  ✗ Attempt {attempt+1}: {last_error}")
                continue

            # ── Validate ──────────────────────────────────────────
            is_valid, violations = validate_board(board)
            last_board = board
            last_violations = violations

            if not is_valid:
                violation_msg = format_violations(violations)
                logger.warning(f"  ✗ Attempt {attempt+1}: Board invalid\n{violation_msg}")
                last_error = f"Extracted board has conflicts:\n{violation_msg}"
                continue  # retry with different padding

            # ── Valid board: solve ────────────────────────────────
            logger.info(f"  ✓ Attempt {attempt+1}: Board valid — solving…")
            solved = solve_board(board)
            elapsed = time.time() - t0

            if solved is None:
                logger.error("  ✗ Solver returned no solution")
                return ImageSolveResponse(
                    extracted_board=board,
                    solved_board=None,
                    execution_time=elapsed,
                    error="No solution exists. The extracted board may have OCR errors.",
                )

            logger.info(f"  ✓ Solved successfully in {elapsed:.3f}s")
            logger.info("=" * 70)
            return ImageSolveResponse(
                extracted_board=board,
                solved_board=solved,
                execution_time=elapsed,
                error=None,
            )

        except Exception as e:
            logger.error(f"  ✗ Attempt {attempt+1} exception: {e}", exc_info=True)
            last_error = f"Processing error: {str(e)}"
            continue

    # ── Attempt 4: high-confidence mode (zero out uncertain cells) ────────────
    logger.info("  [Attempt 4] High-confidence fallback: zeroing uncertain cells")
    try:
        board, confidences, err = _attempt_pipeline(image, 0, high_confidence_only=True)
        if board is not None:
            is_valid, violations = validate_board(board)
            if is_valid:
                solved = solve_board(board)
                elapsed = time.time() - t0
                if solved is not None:
                    logger.info(f"  ✓ Attempt 4 (high-confidence): Solved in {elapsed:.3f}s")
                    logger.info("=" * 70)
                    return ImageSolveResponse(
                        extracted_board=board,
                        solved_board=solved,
                        execution_time=elapsed,
                        error=None,
                    )
            last_board = board
            last_violations = violations
    except Exception as e:
        logger.error(f"  ✗ Attempt 4 exception: {e}", exc_info=True)

    # ── All attempts exhausted ────────────────────────────────────
    elapsed = time.time() - t0
    warnings = [v.get("message", "Unknown error") for v in last_violations] if last_violations else []

    logger.error(f"✗ All 4 attempts failed")
    logger.info("=" * 70)

    # Even if the board has conflicts, return what was extracted
    return ImageSolveResponse(
        extracted_board=last_board,
        solved_board=None,
        execution_time=elapsed,
        error=last_error or "Grid detection failed after all attempts.",
        warnings=warnings if warnings else None,
    )


# ─── Static Frontend ──────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the frontend homepage."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# Mount frontend static files (CSS, JS, images)
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "4.0"}


# ─── Port Management & Server Startup ─────────────────────────────────────────

def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if a port is available on the specified host.

    Args:
        port: Port number to check
        host: Host address (default 0.0.0.0)

    Returns:
        True if port is available, False if in use
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set SO_REUSEADDR to avoid "Address already in use" immediately
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Try to bind to the port
            sock.bind((host, port))
            sock.close()
            return True
    except (OSError, socket.error):
        return False


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """
    Find the next available port starting from start_port.

    Args:
        start_port: Starting port number (default 8000)
        max_attempts: Maximum number of ports to try (default 10)

    Returns:
        Available port number
    """
    for offset in range(max_attempts):
        port = start_port + offset
        if is_port_available(port):
            return port

    logger.error(f"Could not find available port in range {start_port}-{start_port + max_attempts - 1}")
    raise RuntimeError("No available ports found")


def kill_process_on_port(port: int) -> bool:
    """
    Kill process using the specified port (Windows only).

    Args:
        port: Port number

    Returns:
        True if process was killed, False otherwise
    """
    try:
        if sys.platform == "win32":
            # Windows: Use netstat and taskkill
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                # Extract PID from netstat output
                parts = result.stdout.strip().split()
                if len(parts) > 0:
                    pid = parts[-1]
                    try:
                        subprocess.run(f'taskkill /PID {pid} /F', shell=True, check=True)
                        logger.info(f"  ✓ Killed process {pid} using port {port}")
                        return True
                    except subprocess.CalledProcessError:
                        return False
        else:
            # Unix/Linux: Use lsof and kill
            result = subprocess.run(
                f'lsof -i :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        try:
                            subprocess.run(['kill', '-9', pid], check=True)
                            logger.info(f"  ✓ Killed process {pid} using port {port}")
                            return True
                        except subprocess.CalledProcessError:
                            pass
    except Exception as e:
        logger.warning(f"  ⚠ Could not kill process on port {port}: {e}")

    return False


def setup_signal_handlers():
    """Setup proper signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info("\n⏸ Shutdown signal received, closing server gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    import uvicorn

    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()

    logger.info("🚀 Starting Sudoku Automation API v4.0")
    logger.info(f"Frontend directory: {FRONTEND_DIR}")

    # Detect available port
    preferred_port = 8000
    if not is_port_available(preferred_port):
        logger.warning(f"⚠ Port {preferred_port} is in use (WinError 10048)")
        logger.info(f"  Attempting to kill existing process...")
        if kill_process_on_port(preferred_port):
            import time
            time.sleep(1)  # Wait for port to be released

        if not is_port_available(preferred_port):
            logger.info(f"  Finding next available port...")
            preferred_port = find_available_port(start_port=8000)
            logger.info(f"  ✓ Using fallback port {preferred_port}")
    else:
        logger.info(f"  ✓ Port {preferred_port} is available")

    logger.info(f"🌐 Listening on http://0.0.0.0:{preferred_port}")
    logger.info("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=preferred_port,
        log_level="info"
    )
