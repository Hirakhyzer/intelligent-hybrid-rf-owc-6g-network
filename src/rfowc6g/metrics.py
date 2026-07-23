"""Evaluation metrics for hybrid RF-OWC orchestration experiments."""

from __future__ import annotations

import pandas as pd


def policy_comparison(decisions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate policy-level performance metrics."""
    if decisions.empty:
        return pd.DataFrame()
    out = decisions.groupby("policy", as_index=False).agg(
        mean_throughput_mbps=("served_throughput_mbps", "mean"),
        p95_latency_ms=("latency_ms", lambda s: float(s.quantile(0.95))),
        mean_latency_ms=("latency_ms", "mean"),
        mean_reliability=("reliability", "mean"),
        mean_energy_cost=("energy_cost", "mean"),
        owc_utilization=("selected_link", lambda s: float((s == "OWC").mean())),
        handover_rate=("handover_flag", "mean"),
        mean_service_satisfaction=("service_satisfaction", "mean"),
    )
    out["energy_efficiency_mbps_per_cost"] = out["mean_throughput_mbps"] / out["mean_energy_cost"].clip(lower=1e-9)
    return out.sort_values("mean_service_satisfaction", ascending=False).reset_index(drop=True)


def application_quality(decisions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate service quality by application and policy."""
    if decisions.empty:
        return pd.DataFrame()
    return decisions.groupby(["policy", "application"], as_index=False).agg(
        user_time_records=("user_id", "count"),
        mean_throughput_mbps=("served_throughput_mbps", "mean"),
        mean_latency_ms=("latency_ms", "mean"),
        mean_reliability=("reliability", "mean"),
        mean_service_satisfaction=("service_satisfaction", "mean"),
        owc_utilization=("selected_link", lambda s: float((s == "OWC").mean())),
    ).sort_values(["policy", "mean_service_satisfaction"], ascending=[True, False]).reset_index(drop=True)


def blockage_and_mobility_summary(states: pd.DataFrame) -> pd.DataFrame:
    """Summarize blockage and mobility regimes by zone."""
    return states.groupby("zone", as_index=False).agg(
        records=("user_id", "count"),
        mean_mobility_index=("mobility_index", "mean"),
        mean_owc_blockage_probability=("owc_blockage_probability", "mean"),
        mean_line_of_sight_score=("line_of_sight_score", "mean"),
        mean_beam_alignment_error=("beam_alignment_error", "mean"),
    ).sort_values("mean_owc_blockage_probability", ascending=False).reset_index(drop=True)


def summary_metrics(comparison: pd.DataFrame, decisions: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact experiment summary."""
    best = comparison.sort_values("mean_service_satisfaction", ascending=False).iloc[0] if len(comparison) else None
    return {
        "policy_count": int(comparison["policy"].nunique()) if len(comparison) else 0,
        "decision_count": int(len(decisions)),
        "best_policy_by_service_satisfaction": str(best["policy"]) if best is not None else "none",
        "best_policy_mean_service_satisfaction": float(best["mean_service_satisfaction"]) if best is not None else 0.0,
        "mean_owc_utilization": float(comparison["owc_utilization"].mean()) if len(comparison) else 0.0,
        "mean_handover_rate": float(comparison["handover_rate"].mean()) if len(comparison) else 0.0,
        "data_origin": "synthetic independent 6G RF-OWC network simulation traces",
        "decision_boundary": "research simulator only; not telecom infrastructure control or spectrum-management software",
    }
