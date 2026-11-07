"""MPU6050 raw 16-bit samples -> 32-frame, 12-feature windows.

Feature order: [mean(ax,ay,az in g), mean(gx,gy,gz in deg/s),
                std(ax,ay,az in g), std(gx,gy,gz in deg/s)].
Uses population std (ddof=0) as in the embedded C implementation.
"""
import csv
from pathlib import Path
import numpy as np

WINDOW = 32
FEATURES = 12
RAW_COLS = ("ax", "ay", "az", "gx", "gy", "gz")
UNIT_SCALE = np.array([16384., 16384., 16384., 131., 131., 131.], dtype=np.float32)


def read_capture(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not all(c in (reader.fieldnames or []) for c in RAW_COLS):
            raise ValueError(f"{path}: CSV requires {', '.join(RAW_COLS)}")
        samples = []
        for n, row in enumerate(reader, start=2):
            try:
                samples.append([int(row[c]) for c in RAW_COLS])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}:{n} invalid sample") from exc
    return np.asarray(samples, dtype=np.int16).reshape(-1, 6)


def extract_features(samples, window=WINDOW):
    samples = np.asarray(samples, dtype=np.float32)
    if samples.ndim != 2 or samples.shape[1] != 6:
        raise ValueError("samples must have six columns")
    n = len(samples) // window
    if n == 0:
        raise ValueError(f"Need at least {window} samples, got {len(samples)}")
    # Dividing first, as embedded C does, limits numerical disagreement.
    units = (samples[:n*window] / UNIT_SCALE).reshape(n, window, 6)
    return np.concatenate([units.mean(axis=1), units.std(axis=1, ddof=0)], axis=1).astype(np.float32)
