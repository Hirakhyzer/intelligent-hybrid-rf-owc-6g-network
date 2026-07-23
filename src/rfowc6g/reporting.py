"""Markdown report generation for the independent RF-OWC simulator."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def _table(frame: pd.DataFrame, n: int = 8) -> str:
    if frame.empty:
        return "_No rows generated._"
    return frame.head(n).to_markdown(index=False)


def write_report(
    path: str | Path,
    summary: dict,
    comparison: pd.DataFrame,
    app_quality: pd.DataFrame,
    blockage: pd.DataFrame,
) -> None:
    """Write a compact research report."""
    report = f"""# Synthetic Hybrid RF-OWC 6G Network Report

## Boundary

This independent project is a synthetic research simulator. It is not telecom
infrastructure control, spectrum-management software, deployed network
equipment, or certified public communication service logic.

## Summary

- Policies evaluated: {summary.get("policy_count", 0)}
- Link decisions generated: {summary.get("decision_count", 0)}
- Best policy by service satisfaction: `{summary.get("best_policy_by_service_satisfaction", "none")}`
- Mean OWC utilization: {summary.get("mean_owc_utilization", 0):.3f}
- Mean handover rate: {summary.get("mean_handover_rate", 0):.3f}

## Policy comparison

{_table(comparison)}

## Application quality

{_table(app_quality)}

## Mobility and blockage regime

{_table(blockage)}

## Review notes

The adaptive hybrid scheduler should be inspected for service-satisfaction,
handover rate, latency-reliability trade-offs, and OWC utilization. Photonic
efficiency is represented as a transparent proxy for signal generation,
distribution, beamforming, and control efficiency, not as a hardware-validated
circuit model.
"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(report, encoding="utf-8")
