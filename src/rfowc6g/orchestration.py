"""AI-inspired hybrid RF-OWC orchestration and resource allocation policies."""

from __future__ import annotations

import numpy as np
import pandas as pd

POLICIES = [
    "rf_only",
    "owc_preferred",
    "latency_aware",
    "energy_aware",
    "adaptive_hybrid",
]


def orchestrate_links(predicted_states: pd.DataFrame, policies: list[str] | None = None) -> pd.DataFrame:
    """Run link-selection policies and return per-user decisions."""
    chosen_policies = policies or POLICIES
    invalid = [policy for policy in chosen_policies if policy not in POLICIES]
    if invalid:
        raise ValueError(f"Unknown policies: {invalid}")
    frames = [_apply_policy(predicted_states, policy) for policy in chosen_policies]
    return pd.concat(frames, ignore_index=True).sort_values(["policy", "time_step", "user_id"]).reset_index(drop=True)


def _apply_policy(states: pd.DataFrame, policy: str) -> pd.DataFrame:
    rows = []
    last_link: dict[str, str] = {}
    for row in states.sort_values(["time_step", "user_id"]).itertuples(index=False):
        link = _choose_link(row, policy)
        perf = _performance(row, link)
        handover = int(last_link.get(row.user_id, link) != link)
        last_link[row.user_id] = link
        rows.append({
            "policy": policy,
            "time_step": int(row.time_step),
            "user_id": row.user_id,
            "application": row.application,
            "zone": row.zone,
            "selected_link": link,
            "traffic_demand_mbps": float(row.traffic_demand_mbps),
            "served_throughput_mbps": round(perf["served_throughput_mbps"], 3),
            "latency_ms": round(perf["latency_ms"], 3),
            "reliability": round(perf["reliability"], 5),
            "energy_cost": round(perf["energy_cost"], 4),
            "beam_steering_load": round(float(row.beam_alignment_error if link == "OWC" else 0.12 * row.mobility_index), 4),
            "handover_flag": handover,
            "service_satisfaction": round(_service_satisfaction(row, perf), 4),
            "decision_rationale": _rationale(row, link, policy),
        })
    return pd.DataFrame(rows)


def _choose_link(row, policy: str) -> str:
    if policy == "rf_only":
        return "RF"
    if policy == "owc_preferred":
        return "OWC" if row.owc_quality >= 0.22 and row.predicted_owc_blockage < 0.78 else "RF"
    if policy == "latency_aware":
        if row.owc_latency_ms <= row.rf_latency_ms and row.owc_reliability >= row.reliability_target - 0.008:
            return "OWC"
        return "RF"
    if policy == "energy_aware":
        owc_safe = row.owc_quality > 0.30 and row.predicted_owc_blockage < 0.70
        return "OWC" if owc_safe and row.energy_sensitivity >= 0.35 else "RF"
    owc_score = (
        0.34 * row.owc_quality
        + 0.22 * (1 - row.predicted_owc_blockage)
        + 0.16 * (1 - min(row.owc_latency_ms / max(row.latency_target_ms * 2.0, 1), 1))
        + 0.14 * row.photonic_efficiency_gain
        + 0.08 * min(row.owc_throughput_mbps / max(row.traffic_demand_mbps, 1), 1)
        - 0.18 * row.predicted_mobility_index
    )
    rf_score = (
        0.30 * row.rf_quality
        + 0.18 * (1 - row.rf_interference)
        + 0.18 * min(row.rf_throughput_mbps / max(row.traffic_demand_mbps, 1), 1)
        + 0.16 * (1 - min(row.rf_latency_ms / max(row.latency_target_ms * 2.5, 1), 1))
        + 0.14 * row.predicted_mobility_index
    )
    return "OWC" if owc_score > rf_score and row.owc_reliability >= row.reliability_target - 0.015 else "RF"


def _performance(row, link: str) -> dict[str, float]:
    if link == "OWC":
        throughput = min(float(row.traffic_demand_mbps), float(row.owc_throughput_mbps))
        latency = float(row.owc_latency_ms)
        reliability = float(row.owc_reliability)
        energy_cost = throughput * max(0.16, 0.42 - float(row.photonic_efficiency_gain) * 0.25)
    else:
        throughput = min(float(row.traffic_demand_mbps), float(row.rf_throughput_mbps))
        latency = float(row.rf_latency_ms)
        reliability = float(row.rf_reliability)
        energy_cost = throughput * (0.72 + 0.20 * float(row.rf_interference))
    return {"served_throughput_mbps": throughput, "latency_ms": latency, "reliability": reliability, "energy_cost": energy_cost}


def _service_satisfaction(row, perf: dict[str, float]) -> float:
    throughput_term = min(perf["served_throughput_mbps"] / max(float(row.throughput_target_mbps), 1), 1.2)
    latency_term = min(float(row.latency_target_ms) / max(perf["latency_ms"], 0.1), 1.2)
    reliability_term = min(perf["reliability"] / max(float(row.reliability_target), 0.1), 1.05)
    return float(np.clip(0.42 * throughput_term + 0.30 * latency_term + 0.28 * reliability_term, 0, 1.1))


def _rationale(row, link: str, policy: str) -> str:
    if policy == "rf_only":
        return "RF baseline selected for coverage and mobility robustness."
    if link == "OWC":
        return "OWC selected because optical quality, latency, or photonic efficiency is favorable."
    return "RF selected because mobility, blockage, reliability, or line-of-sight risk makes RF safer."
