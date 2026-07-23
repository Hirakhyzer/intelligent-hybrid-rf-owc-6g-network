from rfowc6g.channels import estimate_link_states
from rfowc6g.metrics import application_quality, blockage_and_mobility_summary, policy_comparison
from rfowc6g.orchestration import orchestrate_links
from rfowc6g.prediction import add_predictions
from rfowc6g.synthetic import SyntheticNetworkConfig, generate_synthetic_network_data


def test_metric_tables_have_expected_columns():
    data = generate_synthetic_network_data(SyntheticNetworkConfig(users=16, time_steps=12, seed=9))
    states = add_predictions(estimate_link_states(data["traces"]))
    decisions = orchestrate_links(states)
    comparison = policy_comparison(decisions)
    app = application_quality(decisions)
    blockage = blockage_and_mobility_summary(states)
    assert {"policy", "mean_service_satisfaction", "owc_utilization", "handover_rate"}.issubset(comparison.columns)
    assert {"policy", "application", "mean_latency_ms"}.issubset(app.columns)
    assert {"zone", "mean_owc_blockage_probability"}.issubset(blockage.columns)
