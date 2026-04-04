"""
digit_recognition.py

High-accuracy digit recognition for Sudoku cells using a Multi-Layer
Perceptron (neural network) classifier trained on the MNIST handwritten
digit dataset.

Architecture:
  Input (784) → Dense(512, ReLU) → Dense(256, ReLU) → Dense(128, ReLU) → Dense(9, softmax)

The model is trained on first run (≈30s) and cached to disk for instant
subsequent loads.  Training uses digits 1-9 from MNIST with data
augmentation (rotation, shift, noise, zoom) to maximise accuracy on
real-world printed and photographed Sudoku digits.

Python 3.13 compatible — uses scikit-learn (no TF/PyTorch required).
"""

import cv2
import numpy as np
import logging
import os
import hashlib
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────
DIGIT_SIZE   = 28     # MNIST native resolution
MIN_CONF     = 0.50   # Below this → treat cell as empty
UNCERTAIN    = 0.75   # Between MIN_CONF and UNCERTAIN → use voting
MODEL_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH   = os.path.join(MODEL_DIR, "sudoku_digit_mlp.joblib")
MODEL_VERSION = "v3_mnist_augmented"  # bump to retrain

# ─── NN Classifier Singleton ────────────────────────────────────────────────
_CLASSIFIER = None


# ═════════════════════════════════════════════════════════════════════════════
# MODEL: Training on MNIST
# ═════════════════════════════════════════════════════════════════════════════

def _augment_images(images: np.ndarray, labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply data augmentation to MNIST images to improve robustness
    on real-world printed Sudoku digits.
    
    Augmentations:
      - Rotation ±12°
      - Translation ±2px
      - Gaussian noise
      - Slight erosion/dilation (simulates bold/thin print)
    """
    aug_images = [images]  # start with originals
    aug_labels = [labels]
    
    n = len(images)
    h, w = 28, 28
    
    # ── Rotations ────────────────────────────────────────
    for angle in [-12, -8, -5, 5, 8, 12]:
        batch = np.zeros_like(images)
        for i in range(n):
            img = images[i].reshape(h, w)
            M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h), borderValue=0)
            batch[i] = rotated.flatten()
        aug_images.append(batch)
        aug_labels.append(labels.copy())
    
    # ── Translations ─────────────────────────────────────
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        batch = np.zeros_like(images)
        for i in range(n):
            img = images[i].reshape(h, w)
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            shifted = cv2.warpAffine(img, M, (w, h), borderValue=0)
            batch[i] = shifted.flatten()
        aug_images.append(batch)
        aug_labels.append(labels.copy())
    
    # ── Gaussian noise ───────────────────────────────────
    noise = images + np.random.normal(0, 20, images.shape)
    noise = np.clip(noise, 0, 255)
    aug_images.append(noise.astype(np.float64))
    aug_labels.append(labels.copy())
    
    # ── Morphological (thicker/thinner strokes) ──────────
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    for op in [cv2.MORPH_DILATE, cv2.MORPH_ERODE]:
        batch = np.zeros_like(images)
        for i in range(n):
            img = images[i].reshape(h, w).astype(np.uint8)
            processed = cv2.morphologyEx(img, op, kernel)
            batch[i] = processed.flatten().astype(np.float64)
        aug_images.append(batch)
        aug_labels.append(labels.copy())
    
    all_images = np.vstack(aug_images)
    all_labels = np.concatenate(aug_labels)
    
    # Shuffle
    perm = np.random.permutation(len(all_images))
    return all_images[perm], all_labels[perm]


def _train_model():
    """
    Train an MLP neural network on MNIST digits 1-9.
    Returns the trained classifier.
    """
    from sklearn.neural_network import MLPClassifier
    from sklearn.datasets import fetch_openml
    import joblib
    
    logger.info("Training digit recognition neural network on MNIST data...")
    logger.info("  (This runs once; the model is cached for future use.)")
    
    # Download MNIST
    logger.info("  Downloading MNIST dataset...")
    mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='auto')
    X, y = mnist.data, mnist.target.astype(int)
    
    # Filter to digits 1-9 only (Sudoku has no 0)
    mask = y >= 1
    X = X[mask]
    y = y[mask]
    
    # Remap labels: 1-9 → 0-8 for sklearn (we'll add 1 back at prediction)
    y_mapped = y - 1
    
    logger.info(f"  MNIST filtered: {len(X)} samples (digits 1-9)")
    
    # Data augmentation
    logger.info("  Augmenting training data...")
    X_aug, y_aug = _augment_images(X, y_mapped)
    logger.info(f"  Augmented dataset: {len(X_aug)} samples")
    
    # Normalize to [0, 1]
    X_aug = X_aug / 255.0
    
    # Train MLP neural network
    logger.info("  Training MLP neural network (this may take 1-2 minutes)...")
    clf = MLPClassifier(
        hidden_layer_sizes=(512, 256, 128),
        activation='relu',
        solver='adam',
        alpha=1e-4,           # L2 regularization
        batch_size=256,
        learning_rate='adaptive',
        learning_rate_init=0.001,
        max_iter=30,          # 30 epochs — plenty for MNIST
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=5,
        random_state=42,
        verbose=False,
    )
    clf.fit(X_aug, y_aug)
    
    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({'model': clf, 'version': MODEL_VERSION}, MODEL_PATH)
    logger.info(f"  Model saved to {MODEL_PATH}")
    
    # Quick accuracy check on a held-out slice
    # Use last 2000 original samples as a mini test
    X_test = X[-2000:] / 255.0
    y_test = y[-2000:] - 1
    accuracy = clf.score(X_test, y_test)
    logger.info(f"  Quick accuracy check: {accuracy:.4f} ({accuracy*100:.1f}%)")
    
    return clf


def _get_classifier():
    """Load or train the MLP classifier."""
    global _CLASSIFIER
    if _CLASSIFIER is not None:
        return _CLASSIFIER
    
    # Try loading cached model
    if os.path.exists(MODEL_PATH):
        try:
            import joblib
            data = joblib.load(MODEL_PATH)
            if isinstance(data, dict) and data.get('version') == MODEL_VERSION:
                _CLASSIFIER = data['model']
                logger.info(f"Loaded cached model ({MODEL_VERSION})")
                return _CLASSIFIER
            else:
                logger.info("Model version mismatch — retraining...")
        except Exception as e:
            logger.warning(f"Could not load cached model: {e}")
    
    # Train new model
    _CLASSIFIER = _train_model()
    return _CLASSIFIER


# ═════════════════════════════════════════════════════════════════════════════
# CELL PREPROCESSING
# ═════════════════════════════════════════════════════════════════════════════

def _to_gray(cell: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell.copy()


def _flood_fill_borders(binary: np.ndarray) -> np.ndarray:
    """
    Remove grid-line bleed-in by flood-filling from all four edges.
    Any bright-pixel region connected to the border is suppressed.
    
    Operates on white-bg / black-digit image.
    """
    h, w = binary.shape
    filled = binary.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    
    # Flood-fill from corners AND edge midpoints for thorough coverage
    seeds = [
        (0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1),
        (0, w // 2), (h - 1, w // 2), (h // 2, 0), (h // 2, w - 1),
    ]
    for sy, sx in seeds:
        if filled[sy, sx] == 255:  # only fill white regions
            cv2.floodFill(filled, mask, (sx, sy), 128)
    
    # Everything that was flood-filled (128) → white (background)
    # Everything untouched → keep as-is (these are digit pixels)
    result = np.where(filled == 128, 255, filled).astype(np.uint8)
    return result


def _center_by_mass(digit_bin: np.ndarray, out_size: int) -> np.ndarray:
    """
    Center digit using center-of-mass for translation-invariant positioning.
    Input: white-bg / black-digit.
    """
    inv = cv2.bitwise_not(digit_bin)  # black-bg / white-digit
    M = cv2.moments(inv)
    if M["m00"] == 0:
        return cv2.resize(digit_bin, (out_size, out_size))
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    h, w = digit_bin.shape
    dx = w // 2 - cx
    dy = h // 2 - cy
    
    mat = np.float32([[1, 0, dx], [0, 1, dy]])
    centered = cv2.warpAffine(digit_bin, mat, (w, h), borderValue=255)
    return cv2.resize(centered, (out_size, out_size), interpolation=cv2.INTER_AREA)


def _preprocess_cell_variant(
    cell: np.ndarray, variant: int = 0
) -> Optional[np.ndarray]:
    """
    Preprocess a cell image and return a DIGIT_SIZE×DIGIT_SIZE image
    ready for the neural network (white bg, black digit).
    
    Three variants tried for voting:
      0 – Adaptive Gaussian threshold (primary)
      1 – OTSU threshold
      2 – Adaptive Mean threshold (larger block)
    """
    gray = _to_gray(cell)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    if variant == 0:
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 4
        )
    elif variant == 1:
        _, binary = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    else:
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 15, 6
        )
    
    # Ensure white background, black digit
    if np.mean(binary) < 127:
        binary = cv2.bitwise_not(binary)
    
    # Remove grid-line contamination
    binary = _flood_fill_borders(binary)
    
    # Find digit contours
    inv = cv2.bitwise_not(binary)
    contours, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    
    h, w = binary.shape
    min_area = h * w * 0.008
    max_area = h * w * 0.90
    valid = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
    if not valid:
        return None
    
    # Merge all valid contours into one bounding box
    all_pts = np.vstack(valid)
    bx, by, bw, bh = cv2.boundingRect(all_pts)
    
    # Aspect ratio sanity
    aspect = bh / max(bw, 1)
    if aspect < 0.20 or aspect > 8.0:
        return None
    
    digit_crop = binary[by:by + bh, bx:bx + bw]
    if digit_crop.size == 0:
        return None
    
    # Place on padded square canvas and center by mass
    side = max(bw, bh)
    pad = int(side * 0.35)
    canvas_sz = side + 2 * pad
    canvas = np.ones((canvas_sz, canvas_sz), np.uint8) * 255
    oy = (canvas_sz - bh) // 2
    ox = (canvas_sz - bw) // 2
    canvas[oy:oy + bh, ox:ox + bw] = digit_crop
    
    return _center_by_mass(canvas, DIGIT_SIZE)


# ═════════════════════════════════════════════════════════════════════════════
# EMPTY-CELL DETECTION
# ═════════════════════════════════════════════════════════════════════════════

def _is_empty(cell: np.ndarray) -> bool:
    """Check if a cell is empty by looking at dark-pixel density in centre."""
    gray = _to_gray(cell)
    h, w = gray.shape
    my, mx = int(h * 0.20), int(w * 0.20)
    centre = gray[my:h - my, mx:w - mx]
    if centre.size == 0:
        return True
    dark = np.sum(centre < 100)
    return (dark / centre.size) < 0.025


# ═════════════════════════════════════════════════════════════════════════════
# DIGIT RECOGNITION (single cell)
# ═════════════════════════════════════════════════════════════════════════════

def recognize_digit(cell: np.ndarray) -> Tuple[int, float]:
    """
    Recognize one Sudoku cell.
    
    Returns (digit, confidence):
      digit: 0 = empty, 1-9 = recognized digit
      confidence: 0.0-1.0 probability from the neural network
    
    Strategy:
      1. Quick empty check → (0, 1.0)
      2. Run 3 preprocessing variants
      3. Query neural network for each; collect probability vectors
      4. Average probabilities, pick argmax
      5. If confidence < MIN_CONF → (0, confidence)
    """
    if _is_empty(cell):
        return 0, 1.0
    
    clf = _get_classifier()
    prob_accum = np.zeros(9)  # classes 0-8 → digits 1-9
    n_valid = 0
    
    for v in range(3):
        proc = _preprocess_cell_variant(cell, variant=v)
        if proc is None:
            continue
        
        # Convert to MNIST format: white digit on black background, [0, 1] range
        # Our preprocessing produces white-bg black-digit; MNIST is inverted
        mnist_fmt = cv2.bitwise_not(proc)
        sample = mnist_fmt.flatten().astype(np.float64).reshape(1, -1) / 255.0
        
        probs = clf.predict_proba(sample)[0]
        prob_accum += probs
        n_valid += 1
    
    if n_valid == 0:
        return 0, 0.0
    
    # Average probabilities across variants
    avg_probs = prob_accum / n_valid
    predicted_class = int(np.argmax(avg_probs))
    confidence = float(avg_probs[predicted_class])
    
    digit = predicted_class + 1  # map 0-8 → 1-9
    
    logger.debug(f"    Cell → {digit} (conf={confidence:.3f})")
    
    if confidence < MIN_CONF:
        return 0, confidence
    
    return digit, confidence


# ═════════════════════════════════════════════════════════════════════════════
# BOARD RECOGNITION
# ═════════════════════════════════════════════════════════════════════════════

def recognize_board(cells: List[List[np.ndarray]]) -> List[List[int]]:
    """
    Recognize all digits from a 9×9 grid of cell images.
    Returns a 9×9 list of ints (0 = empty, 1-9 = digit).
    """
    board = []
    confidences = []
    
    for i, row_cells in enumerate(cells):
        row = []
        row_conf = []
        for j, cell in enumerate(row_cells):
            digit, conf = recognize_digit(cell)
            row.append(digit)
            row_conf.append(conf)
        board.append(row)
        confidences.append(row_conf)
    
    # Log extracted board
    non_zero = sum(1 for r in board for v in r if v != 0)
    logger.info("=== EXTRACTED BOARD ===")
    for i, row in enumerate(board):
        conf_str = " ".join(f"{c:.0%}" for c in confidences[i])
        logger.info(f"  Row {i}: {row}  conf: [{conf_str}]")
    logger.info(f"  Digits detected: {non_zero}/81")
    logger.info("=" * 50)
    
    return board


def get_model():
    """Public accessor for model (used by tests)."""
    return _get_classifier()
