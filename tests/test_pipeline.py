import json
import subprocess
import sys


def test_synthetic_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    cmd = [
        sys.executable,
        "scripts/run_synthetic_rf_owc_lab.py",
        "--users",
        "16",
        "--time-steps",
        "12",
        "--seed",
        "11",
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)
    summary_path = output_dir / "results" / "synthetic_rf_owc_6g_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["user_count"] == 16
    assert summary["decision_count"] > 0
    assert summary["audit_log"]["valid"] is True
