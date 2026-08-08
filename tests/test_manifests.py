import json
from pathlib import Path


def test_deployments_are_real_addresses():
    deployments = json.loads(Path("deployments.json").read_text(encoding="utf-8"))
    for deployment in deployments["contracts"].values():
        assert deployment["address"].startswith("0x")
        assert len(deployment["address"]) == 42


def test_manifests_have_no_fake_live_receipts():
    for path in Path("manifests").glob("*.json"):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        assert manifest["contract"]["chain"] == "studionet"
        assert manifest["contract"]["address"].startswith("0x")
        for run in manifest["runs"]:
            if run["mode"] == "mock":
                for episode in run["episodes"]:
                    for step in episode["steps"]:
                        assert step.get("illustrative") is True
                        assert "tx" not in step
                        assert "consensus" not in step
