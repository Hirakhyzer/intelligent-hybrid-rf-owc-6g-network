"""Deterministic synthetic 6G users, applications, mobility, traffic, and testbed traces."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

APPLICATIONS = ["xr", "industrial_automation", "autonomous_system", "ai_device", "emergency_low_latency"]
MOBILITY_PROFILES = ["stationary", "walking", "vehicle", "robotic_cell"]
ZONES = ["indoor_factory", "smart_office", "street_canyon", "transport_hub", "edge_lab"]


@dataclass(frozen=True)
class SyntheticNetworkConfig:
    users: int = 72
    time_steps: int = 96
    seed: int = 42

    def __post_init__(self) -> None:
        if self.users < 12:
            raise ValueError("Use at least 12 users for meaningful orchestration metrics.")
        if self.time_steps < 12:
            raise ValueError("Use at least 12 time steps for mobility and blockage analysis.")


def generate_synthetic_network_data(config: SyntheticNetworkConfig | None = None) -> dict[str, pd.DataFrame]:
    """Generate a fully fictional hybrid RF-OWC network experiment."""
    cfg = config or SyntheticNetworkConfig()
    rng = np.random.default_rng(cfg.seed)
    users = _users(cfg, rng)
    infrastructure = _infrastructure()
    traces = _traces(users, cfg, rng)
    return {"users": users, "infrastructure": infrastructure, "traces": traces}


def _users(cfg: SyntheticNetworkConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(cfg.users):
        app = APPLICATIONS[idx % len(APPLICATIONS)]
        mobility = MOBILITY_PROFILES[(idx * 2 + 1) % len(MOBILITY_PROFILES)]
        zone = ZONES[(idx * 3) % len(ZONES)]
        rows.append({
            "user_id": f"U-{idx+1:04d}",
            "application": app,
            "mobility_profile": mobility,
            "zone": zone,
            "latency_target_ms": {"xr": 18, "industrial_automation": 8, "autonomous_system": 12, "ai_device": 35, "emergency_low_latency": 6}[app],
            "throughput_target_mbps": {"xr": 380, "industrial_automation": 90, "autonomous_system": 160, "ai_device": 70, "emergency_low_latency": 45}[app],
            "reliability_target": {"xr": 0.995, "industrial_automation": 0.999, "autonomous_system": 0.998, "ai_device": 0.990, "emergency_low_latency": 0.9995}[app],
            "energy_sensitivity": round(float(np.clip(rng.normal(0.55, 0.18), 0.10, 0.95)), 3),
        })
    return pd.DataFrame(rows)


def _infrastructure() -> pd.DataFrame:
    return pd.DataFrame([
        {"node_id": "RF-MACRO-01", "link_type": "RF", "coverage_role": "wide_area", "nominal_capacity_mbps": 620, "energy_cost_per_mbit": 0.95, "mobility_support": 0.98},
        {"node_id": "RF-SMALL-01", "link_type": "RF", "coverage_role": "dense_cell", "nominal_capacity_mbps": 880, "energy_cost_per_mbit": 0.78, "mobility_support": 0.92},
        {"node_id": "OWC-AP-01", "link_type": "OWC", "coverage_role": "line_of_sight_hotspot", "nominal_capacity_mbps": 2400, "energy_cost_per_mbit": 0.34, "mobility_support": 0.62},
        {"node_id": "OWC-AP-02", "link_type": "OWC", "coverage_role": "photonic_beam_cluster", "nominal_capacity_mbps": 3200, "energy_cost_per_mbit": 0.26, "mobility_support": 0.58},
    ])


def _traces(users: pd.DataFrame, cfg: SyntheticNetworkConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    mobility_noise = {"stationary": 0.03, "walking": 0.13, "vehicle": 0.30, "robotic_cell": 0.18}
    for t in range(cfg.time_steps):
        time_phase = 0.5 + 0.5 * np.sin(2 * np.pi * t / max(cfg.time_steps, 1))
        for user in users.itertuples(index=False):
            demand_base = float(user.throughput_target_mbps) * rng.normal(0.88 + 0.35 * time_phase, 0.15)
            demand_mbps = max(5.0, demand_base)
            mobility = float(np.clip(rng.normal(mobility_noise[user.mobility_profile], 0.06), 0, 1))
            zone_blockage = 0.22 if user.zone in {"street_canyon", "transport_hub"} else 0.08
            owc_blockage_probability = float(np.clip(zone_blockage + 0.55 * mobility + rng.normal(0, 0.06), 0, 1))
            rf_interference = float(np.clip(rng.normal(0.28 + 0.20 * time_phase, 0.12), 0, 1))
            line_of_sight_score = float(np.clip(1 - owc_blockage_probability + rng.normal(0, 0.08), 0, 1))
            beam_alignment_error = float(np.clip(0.08 + 0.45 * mobility + 0.20 * (1 - line_of_sight_score) + rng.normal(0, 0.04), 0, 1))
            traffic_burst = int(rng.random() < (0.18 if user.application in {"xr", "autonomous_system"} else 0.08))
            rows.append({
                "time_step": t,
                "user_id": user.user_id,
                "application": user.application,
                "zone": user.zone,
                "mobility_profile": user.mobility_profile,
                "traffic_demand_mbps": round(demand_mbps * (1.35 if traffic_burst else 1.0), 3),
                "latency_target_ms": user.latency_target_ms,
                "throughput_target_mbps": user.throughput_target_mbps,
                "reliability_target": user.reliability_target,
                "energy_sensitivity": user.energy_sensitivity,
                "mobility_index": round(mobility, 4),
                "rf_interference": round(rf_interference, 4),
                "owc_blockage_probability": round(owc_blockage_probability, 4),
                "line_of_sight_score": round(line_of_sight_score, 4),
                "beam_alignment_error": round(beam_alignment_error, 4),
                "traffic_burst_flag": traffic_burst,
            })
    return pd.DataFrame(rows)
