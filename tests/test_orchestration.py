from rfowc6g.channels import estimate_link_states
from rfowc6g.orchestration import POLICIES, orchestrate_links
from rfowc6g.prediction import add_predictions
from rfowc6g.synthetic import SyntheticNetworkConfig, generate_synthetic_network_data


def _states():
    data = generate_synthetic_network_data(SyntheticNetworkConfig(users=16, time_steps=12, seed=8))
    return add_predictions(estimate_link_states(data["traces"]))


def test_all_policies_generate_decisions():
    decisions = orchestrate_links(_states())
    assert not decisions.empty
    assert set(decisions["policy"].unique()) == set(POLICIES)
    assert decisions["service_satisfaction"].between(0, 1.1).all()


def test_selected_links_are_valid():
    decisions = orchestrate_links(_states(), policies=["adaptive_hybrid"])
    assert set(decisions["selected_link"].unique()).issubset({"RF", "OWC"})
    assert decisions["served_throughput_mbps"].ge(0).all()
