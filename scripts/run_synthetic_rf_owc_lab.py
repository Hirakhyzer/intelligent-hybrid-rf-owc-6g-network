"""Run the independent synthetic hybrid RF-OWC 6G network lab.

The command uses only fictional users, applications, mobility traces, RF channel
states, optical wireless channel states, and photonic-efficiency proxies. It
demonstrates traffic prediction, mobility/blockage estimation, AI-inspired
orchestration, resource allocation, service-quality evaluation, reporting,
figures, and a hash-chained audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rfowc6g.audit import append_record, verify_log
from rfowc6g.channels import estimate_link_states
from rfowc6g.config import ensure_output_dirs, set_seed
from rfowc6g.metrics import application_quality, blockage_and_mobility_summary, policy_comparison, summary_metrics
from rfowc6g.orchestration import orchestrate_links
from rfowc6g.prediction import add_predictions
from rfowc6g.reporting import write_report
from rfowc6g.synthetic import SyntheticNetworkConfig, generate_synthetic_network_data
from rfowc6g.visualization import (
    plot_application_quality,
    plot_latency_reliability,
    plot_link_utilization,
    plot_mobility_blockage,
    plot_service_satisfaction,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic hybrid RF-OWC 6G network orchestration lab.")
    parser.add_argument("--users", type=int, default=72)
    parser.add_argument("--time-steps", type=int, default=96)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_network_data(SyntheticNetworkConfig(users=args.users, time_steps=args.time_steps, seed=args.seed))
    users = data["users"]
    infrastructure = data["infrastructure"]
    traces = data["traces"]

    link_states = estimate_link_states(traces)
    predicted = add_predictions(link_states)
    decisions = orchestrate_links(predicted)
    comparison = policy_comparison(decisions)
    app_quality = application_quality(decisions)
    blockage = blockage_and_mobility_summary(predicted)

    summary = summary_metrics(comparison, decisions)
    summary.update({
        "seed": args.seed,
        "user_count": int(len(users)),
        "time_steps": int(args.time_steps),
        "trace_count": int(len(traces)),
        "infrastructure_node_count": int(len(infrastructure)),
    })

    users.to_csv(outputs["results"] / "synthetic_users.csv", index=False)
    infrastructure.to_csv(outputs["results"] / "synthetic_infrastructure.csv", index=False)
    traces.to_csv(outputs["results"] / "synthetic_network_traces.csv", index=False)
    link_states.to_csv(outputs["results"] / "synthetic_link_states.csv", index=False)
    predicted.to_csv(outputs["results"] / "synthetic_predictions.csv", index=False)
    decisions.to_csv(outputs["results"] / "synthetic_link_decisions.csv", index=False)
    comparison.to_csv(outputs["results"] / "synthetic_policy_comparison.csv", index=False)
    app_quality.to_csv(outputs["results"] / "synthetic_application_quality.csv", index=False)
    blockage.to_csv(outputs["results"] / "synthetic_mobility_blockage_summary.csv", index=False)

    audit_path = outputs["audit"] / "rf_owc_6g_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "independent synthetic 6G network simulator only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_rf_owc_6g_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_rf_owc_6g_report.md", summary, comparison, app_quality, blockage)
    plot_service_satisfaction(comparison, outputs["figures"] / "synthetic_service_satisfaction.png")
    plot_latency_reliability(comparison, outputs["figures"] / "synthetic_latency_reliability.png")
    plot_link_utilization(comparison, outputs["figures"] / "synthetic_link_utilization.png")
    plot_mobility_blockage(blockage, outputs["figures"] / "synthetic_mobility_blockage.png")
    plot_application_quality(app_quality, outputs["figures"] / "synthetic_application_quality.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
