"""Configuration helpers for the RF-OWC simulator."""

from __future__ import annotations

from pathlib import Path
import random
import numpy as np


def set_seed(seed: int) -> None:
    """Set deterministic seeds for repeatable synthetic experiments."""
    random.seed(seed)
    np.random.seed(seed)


def ensure_output_dirs(base_dir: str | Path = "outputs") -> dict[str, Path]:
    """Create output folders used by the lab runner."""
    base = Path(base_dir)
    paths = {
        "base": base,
        "results": base / "results",
        "figures": base / "figures",
        "reports": base / "reports",
        "audit": base / "audit",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths
