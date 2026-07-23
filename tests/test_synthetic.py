from rfowc6g.synthetic import SyntheticNetworkConfig, generate_synthetic_network_data


def test_synthetic_network_shapes():
    data = generate_synthetic_network_data(SyntheticNetworkConfig(users=16, time_steps=12, seed=4))
    assert set(data) == {"users", "infrastructure", "traces"}
    assert len(data["users"]) == 16
    assert data["traces"]["user_id"].nunique() == 16
    assert data["traces"]["time_step"].nunique() == 12
    assert {"RF", "OWC"}.issubset(set(data["infrastructure"]["link_type"]))


def test_invalid_config_rejected():
    try:
        SyntheticNetworkConfig(users=5, time_steps=10)
    except ValueError:
        assert True
    else:
        raise AssertionError("invalid configuration should fail")
