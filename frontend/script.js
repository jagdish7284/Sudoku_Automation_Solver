/**
 * SUDOKU // CYBER_GRID v4.0
 * ──────────────────────────────────────────────────────────────────────────────
 * Cyberpunk Sudoku Frontend Controller
 *
 * Features:
 *   • Strict single-digit input (1-9 only, keyboard only)
 *   • Row / Column / 3×3 box highlighting on cell focus
 *   • Matrix rain animated background
 *   • Digit pop & glitch animations
 *   • Optional key-press audio feedback
 *   • Cascade reveal animation on solve
 * ──────────────────────────────────────────────────────────────────────────────
 */

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM References ──────────────────────────────────────────────────────
    const boardTable       = document.getElementById('sudoku-board');
    const form             = document.getElementById('sudoku-form');
    const resultDiv        = document.getElementById('result');
    const execTimeDiv      = document.getElementById('exec-time');
    const clearBtn         = document.getElementById('clear-btn');
    const cellCountDisplay = document.getElementById('cell-count');
    const gridStatus       = document.getElementById('grid-status');

    let activeCell = null;   // Currently focused cell { row, col, td, input }

    // ── Audio Feedback (Web Audio API — no external files needed) ────────
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function ensureAudioCtx() {
        if (!audioCtx) {
            try { audioCtx = new AudioCtx(); } catch (_) { /* silent fail */ }
        }
    }

    function playTone(freq, duration, type = 'sine', volume = 0.06) {
        ensureAudioCtx();
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(volume, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
    }

    function playKeySound()   { playTone(880, 0.08, 'square', 0.04); }
    function playClearSound()  { playTone(440, 0.12, 'triangle', 0.04); }
    function playErrorSound()  { playTone(220, 0.2, 'sawtooth', 0.05); }
    function playSolveSound()  { playTone(1200, 0.15, 'sine', 0.06); }

    // ── Matrix Rain Background ──────────────────────────────────────────────
    function initMatrixRain() {
        const canvas = document.getElementById('matrix-rain');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノ789ABCDEF'.split('');
        const fontSize = 14;
        let columns = Math.floor(canvas.width / fontSize);
        let drops = Array(columns).fill(1);

        function draw() {
            ctx.fillStyle = 'rgba(10, 14, 23, 0.06)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00f0ff';
            ctx.font = `${fontSize}px JetBrains Mono, monospace`;

            for (let i = 0; i < drops.length; i++) {
                const char = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(char, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }

        // Recalculate columns on resize
        window.addEventListener('resize', () => {
            columns = Math.floor(canvas.width / fontSize);
            drops = Array(columns).fill(1);
        });

        setInterval(draw, 45);
    }
    initMatrixRain();

    // ── Build 9×9 Grid ──────────────────────────────────────────────────────
    const cells = [];  // 2D array: cells[row][col] = { td, input }

    for (let i = 0; i < 9; i++) {
        cells[i] = [];
        const tr = document.createElement('tr');
        for (let j = 0; j < 9; j++) {
            const td = document.createElement('td');
            const input = document.createElement('input');

            input.type = 'text';  // text, NOT number — gives us full control
            input.maxLength = 1;
            input.autocomplete = 'off';
            input.setAttribute('inputmode', 'numeric');
            input.setAttribute('aria-label', `Cell row ${i + 1} column ${j + 1}`);
            input.dataset.row = i;
            input.dataset.col = j;

            // 3×3 subgrid border classes
            if (j === 2 || j === 5) td.classList.add('border-right');
            if (i === 2 || i === 5) td.classList.add('border-bottom');

            td.appendChild(input);
            tr.appendChild(td);
            cells[i][j] = { td, input };
        }
        boardTable.appendChild(tr);
    }

    // ── Strict Input Control ────────────────────────────────────────────────

    /**
     * KEYDOWN handler — the primary input gate.
     * Allows: digits 1-9, Backspace, Delete, Tab, Arrow keys, Escape
     * Blocks: everything else (letters, symbols, multiple digits, paste shortcuts)
     */
    boardTable.addEventListener('keydown', (e) => {
        const input = e.target;
        if (input.tagName !== 'INPUT') return;

        const row = parseInt(input.dataset.row);
        const col = parseInt(input.dataset.col);
        const key = e.key;

        // Navigation: arrow keys
        if (key === 'ArrowUp' || key === 'ArrowDown' || key === 'ArrowLeft' || key === 'ArrowRight') {
            e.preventDefault();
            let nr = row, nc = col;
            if (key === 'ArrowUp')    nr = Math.max(0, row - 1);
            if (key === 'ArrowDown')  nr = Math.min(8, row + 1);
            if (key === 'ArrowLeft')  nc = Math.max(0, col - 1);
            if (key === 'ArrowRight') nc = Math.min(8, col + 1);
            cells[nr][nc].input.focus();
            return;
        }

        // Allow: Tab (natural navigation), Escape
        if (key === 'Tab' || key === 'Escape') return;

        // Backspace / Delete — clear cell
        if (key === 'Backspace' || key === 'Delete') {
            e.preventDefault();
            input.value = '';
            input.classList.remove('digit-enter');
            cells[row][col].td.classList.remove('cell-error', 'cell-given', 'cell-solved');
            playClearSound();
            updateCellCount();
            updateGridStatus();
            return;
        }

        // Block Ctrl+V / Cmd+V (prevent paste via keyboard shortcut)
        if ((e.ctrlKey || e.metaKey) && (key === 'v' || key === 'V')) {
            e.preventDefault();
            return;
        }

        // Block any ctrl/meta/alt combos except tab
        if (e.ctrlKey || e.metaKey || e.altKey) {
            e.preventDefault();
            return;
        }

        // DIGIT 1-9 — the only valid input
        if (/^[1-9]$/.test(key)) {
            e.preventDefault();

            // Replace previous value
            input.value = key;

            // Pop animation
            input.classList.remove('digit-enter', 'glitch');
            void input.offsetWidth; // force reflow
            input.classList.add('digit-enter');

            // Mark as user-given
            cells[row][col].td.classList.add('cell-given');
            cells[row][col].td.classList.remove('cell-solved', 'cell-error');

            playKeySound();
            updateCellCount();
            updateGridStatus();
            return;
        }

        // Everything else: BLOCKED
        e.preventDefault();
        // Glitch effect for invalid input
        input.classList.remove('glitch');
        void input.offsetWidth;
        input.classList.add('glitch');
        playErrorSound();
    });

    // ── Block paste entirely ────────────────────────────────────────────────
    boardTable.addEventListener('paste', (e) => {
        e.preventDefault();
    });

    // ── Block drop ──────────────────────────────────────────────────────────
    boardTable.addEventListener('drop', (e) => {
        e.preventDefault();
    });

    // ── Block context menu on grid (prevent paste via right-click) ───────
    boardTable.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });

    // ── Extra safety: input event — ensure only single digit 1-9 ────────
    boardTable.addEventListener('input', (e) => {
        const input = e.target;
        if (input.tagName !== 'INPUT') return;

        // Strip anything that isn't 1-9
        const cleaned = input.value.replace(/[^1-9]/g, '');

        if (cleaned.length === 0) {
            input.value = '';
        } else {
            // Only keep the LAST valid digit (handles rapid entry edge cases)
            input.value = cleaned.slice(-1);
        }

        const row = parseInt(input.dataset.row);
        const col = parseInt(input.dataset.col);

        if (input.value) {
            cells[row][col].td.classList.add('cell-given');
            cells[row][col].td.classList.remove('cell-solved', 'cell-error');
        } else {
            cells[row][col].td.classList.remove('cell-given');
        }

        updateCellCount();
        updateGridStatus();
    });

    // ── Focus / Blur — Highlighting ─────────────────────────────────────────
    boardTable.addEventListener('focusin', (e) => {
        const input = e.target;
        if (input.tagName !== 'INPUT') return;

        const row = parseInt(input.dataset.row);
        const col = parseInt(input.dataset.col);
        const td = cells[row][col].td;

        // Clear previous highlights
        clearHighlights();

        // Set active
        activeCell = { row, col, td, input };
        td.classList.add('cell-active');

        // Highlight row, column, and 3×3 box
        const boxRow = Math.floor(row / 3) * 3;
        const boxCol = Math.floor(col / 3) * 3;

        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (r === row && c === col) continue;

                const isRow = (r === row);
                const isCol = (c === col);
                const isBox = (r >= boxRow && r < boxRow + 3 && c >= boxCol && c < boxCol + 3);

                if (isBox) {
                    cells[r][c].td.classList.add('highlight-box');
                } else if (isRow || isCol) {
                    cells[r][c].td.classList.add('highlight-cross');
                }
            }
        }

        // Select text for easy overwrite
        input.select();
    });

    boardTable.addEventListener('focusout', (e) => {
        // Small delay to allow focus to move to another cell
        setTimeout(() => {
            const focused = document.activeElement;
            if (!boardTable.contains(focused)) {
                clearHighlights();
                activeCell = null;
            }
        }, 10);
    });

    // ── Hover effect ────────────────────────────────────────────────────────
    boardTable.addEventListener('mouseover', (e) => {
        const td = e.target.closest('td');
        if (td && boardTable.contains(td)) {
            td.classList.add('cell-hover');
        }
    });

    boardTable.addEventListener('mouseout', (e) => {
        const td = e.target.closest('td');
        if (td) {
            td.classList.remove('cell-hover');
        }
    });

    function clearHighlights() {
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                cells[r][c].td.classList.remove(
                    'cell-active', 'highlight-cross', 'highlight-box'
                );
            }
        }
    }

    // ── Cell Count & Status ─────────────────────────────────────────────────
    function updateCellCount() {
        let count = 0;
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (cells[r][c].input.value) count++;
            }
        }
        cellCountDisplay.textContent = `${count}/81`;
    }

    function updateGridStatus() {
        let count = 0;
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (cells[r][c].input.value) count++;
            }
        }
        if (count === 0) {
            gridStatus.textContent = 'AWAITING_INPUT';
        } else if (count === 81) {
            gridStatus.textContent = 'GRID_COMPLETE';
        } else {
            gridStatus.textContent = 'INPUT_ACTIVE';
        }
    }

    // ── Clear Button ────────────────────────────────────────────────────────
    clearBtn.addEventListener('click', () => {
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                cells[r][c].input.value = '';
                cells[r][c].input.readOnly = false;
                cells[r][c].td.classList.remove(
                    'cell-given', 'cell-solved', 'cell-error', 'cascade-reveal'
                );
            }
        }
        resultDiv.textContent = '';
        resultDiv.className = 'result-display';
        execTimeDiv.textContent = '';
        playClearSound();
        updateCellCount();
        updateGridStatus();
    });

    // ── Solve (Manual) ──────────────────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Build board array
        const board = [];
        for (let i = 0; i < 9; i++) {
            const row = [];
            for (let j = 0; j < 9; j++) {
                const val = cells[i][j].input.value;
                row.push(val === '' ? 0 : parseInt(val, 10));
            }
            board.push(row);
        }

        // Clear previous results
        resultDiv.textContent = '';
        resultDiv.className = 'result-display';
        execTimeDiv.textContent = '';

        // Show processing
        resultDiv.innerHTML = '<span class="loading-spinner"></span>SOLVING...';
        resultDiv.classList.add('processing');
        gridStatus.textContent = 'SOLVING';

        const start = performance.now();
        try {
            const response = await fetch('/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ board })
            });
            const data = await response.json();
            const end = performance.now();

            if (data.detail) {
                resultDiv.textContent = `ERROR: ${data.detail}`;
                resultDiv.className = 'result-display error';
                gridStatus.textContent = 'ERROR';
                playErrorSound();
            } else {
                // Fill solved board with cascade animation
                const solvedBoard = data.solved_board;
                let delay = 0;
                for (let i = 0; i < 9; i++) {
                    for (let j = 0; j < 9; j++) {
                        const wasEmpty = !cells[i][j].input.value || cells[i][j].input.value === '0';
                        cells[i][j].input.value = solvedBoard[i][j];

                        if (wasEmpty) {
                            cells[i][j].td.classList.add('cell-solved');
                            // Cascade reveal
                            setTimeout(() => {
                                cells[i][j].td.classList.add('cascade-reveal');
                            }, delay);
                            delay += 15;
                        } else {
                            cells[i][j].td.classList.add('cell-given');
                        }
                    }
                }

                resultDiv.textContent = '✓ SOLUTION_FOUND';
                resultDiv.className = 'result-display success';
                gridStatus.textContent = 'SOLVED';
                playSolveSound();
            }

            execTimeDiv.textContent = `exec_time: ${(end - start).toFixed(2)}ms`;
        } catch (err) {
            resultDiv.textContent = 'ERROR: CONNECTION_FAILED';
            resultDiv.className = 'result-display error';
            gridStatus.textContent = 'ERROR';
            playErrorSound();
        }

        updateCellCount();
    });

    // ── Initial state ───────────────────────────────────────────────────────
    updateCellCount();
    updateGridStatus();
});
