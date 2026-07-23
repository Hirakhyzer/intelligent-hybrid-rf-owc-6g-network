"""Simple transparent traffic, mobility, and blockage prediction baselines."""

from __future__ import annotations

import pandas as pd


def add_predictions(link_states: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """Add rolling prediction features used by the adaptive scheduler."""
    frame = link_states.sort_values(["user_id", "time_step"]).copy()
    grouped = frame.groupby("user_id", group_keys=False)
    frame["predicted_traffic_mbps"] = grouped["traffic_demand_mbps"].apply(lambda s: s.shift(1).rolling(window, min_periods=1).mean()).reset_index(level=0, drop=True)
    frame["predicted_mobility_index"] = grouped["mobility_index"].apply(lambda s: s.shift(1).rolling(window, min_periods=1).mean()).reset_index(level=0, drop=True)
    frame["predicted_owc_blockage"] = grouped["owc_blockage_probability"].apply(lambda s: s.shift(1).rolling(window, min_periods=1).mean()).reset_index(level=0, drop=True)
    frame["predicted_traffic_mbps"] = frame["predicted_traffic_mbps"].fillna(frame["traffic_demand_mbps"])
    frame["predicted_mobility_index"] = frame["predicted_mobility_index"].fillna(frame["mobility_index"])
    frame["predicted_owc_blockage"] = frame["predicted_owc_blockage"].fillna(frame["owc_blockage_probability"])
    frame["demand_pressure"] = (frame["predicted_traffic_mbps"] / frame["throughput_target_mbps"].clip(lower=1)).clip(0, 3)
    return frame
