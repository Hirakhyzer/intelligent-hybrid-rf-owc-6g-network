"""Matplotlib visualizations for synthetic RF-OWC experiments."""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def _save(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_service_satisfaction(comparison: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not comparison.empty:
        comparison.sort_values("mean_service_satisfaction").plot.barh(x="policy", y="mean_service_satisfaction", ax=ax, legend=False)
    ax.set_title("Mean service satisfaction by orchestration policy")
    ax.set_xlabel("Satisfaction proxy")
    _save(path)


def plot_latency_reliability(comparison: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    if not comparison.empty:
        ax.scatter(comparison["p95_latency_ms"], comparison["mean_reliability"])
        for row in comparison.itertuples(index=False):
            ax.annotate(row.policy, (row.p95_latency_ms, row.mean_reliability), fontsize=8)
    ax.set_title("Latency-reliability policy trade-off")
    ax.set_xlabel("p95 latency (ms)")
    ax.set_ylabel("Mean reliability")
    _save(path)


def plot_link_utilization(comparison: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not comparison.empty:
        comparison.sort_values("owc_utilization").plot.barh(x="policy", y="owc_utilization", ax=ax, legend=False)
    ax.set_title("OWC utilization by policy")
    ax.set_xlabel("Share of decisions using OWC")
    _save(path)


def plot_mobility_blockage(summary: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if not summary.empty:
        summary.plot.bar(x="zone", y=["mean_mobility_index", "mean_owc_blockage_probability"], ax=ax)
    ax.set_title("Mobility and OWC blockage by zone")
    ax.set_ylabel("Mean proxy value")
    ax.tick_params(axis="x", rotation=30)
    _save(path)


def plot_application_quality(app_quality: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    if not app_quality.empty:
        best = app_quality.groupby("application", as_index=False)["mean_service_satisfaction"].mean()
        best.sort_values("mean_service_satisfaction").plot.barh(x="application", y="mean_service_satisfaction", ax=ax, legend=False)
    ax.set_title("Average service satisfaction by application class")
    ax.set_xlabel("Satisfaction proxy")
    _save(path)
