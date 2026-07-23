"""Hybrid RF and optical wireless channel-quality estimation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_link_states(traces: pd.DataFrame) -> pd.DataFrame:
    """Estimate synthetic RF and OWC link states for each user-time record."""
    rows = []
    for row in traces.itertuples(index=False):
        rf_quality = float(np.clip(0.92 - 0.55 * row.rf_interference - 0.08 * row.mobility_index, 0.05, 1.0))
        owc_quality = float(np.clip(0.98 * row.line_of_sight_score - 0.50 * row.beam_alignment_error, 0.02, 1.0))
        rf_throughput = 620 * rf_quality * (1 - 0.18 * row.rf_interference)
        owc_throughput = 2600 * owc_quality * (1 - 0.10 * row.owc_blockage_probability)
        rf_latency = 7.5 + 22.0 * (1 - rf_quality) + 6.0 * row.rf_interference
        owc_latency = 2.8 + 13.0 * (1 - owc_quality) + 18.0 * row.owc_blockage_probability
        rf_reliability = float(np.clip(0.985 + 0.014 * rf_quality - 0.004 * row.rf_interference, 0.92, 0.9995))
        owc_reliability = float(np.clip(0.990 + 0.010 * owc_quality - 0.030 * row.owc_blockage_probability, 0.80, 0.9999))
        rows.append({
            **row._asdict(),
            "rf_quality": round(rf_quality, 4),
            "owc_quality": round(owc_quality, 4),
            "rf_throughput_mbps": round(float(rf_throughput), 3),
            "owc_throughput_mbps": round(float(owc_throughput), 3),
            "rf_latency_ms": round(float(rf_latency), 3),
            "owc_latency_ms": round(float(owc_latency), 3),
            "rf_reliability": round(rf_reliability, 5),
            "owc_reliability": round(owc_reliability, 5),
            "photonic_efficiency_gain": round(float(np.clip(0.18 + 0.60 * owc_quality - 0.20 * row.beam_alignment_error, 0, 0.75)), 4),
        })
    return pd.DataFrame(rows)
