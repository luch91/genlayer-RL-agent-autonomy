"""Export truthful demo-suite manifests from local mock training and deployments."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.domains import get_domain  # noqa: E402
from agent.env import MockEnvironment  # noqa: E402
from agent.q_learning import QLearningAgent  # noqa: E402
DEPLOYMENTS = json.loads((ROOT / "deployments.json").read_text(encoding="utf-8"))
OUT = ROOT / "manifests"

DOMAIN_META = {
    "crisis": ("crisis-negotiator", "Crisis Negotiator", "Crisis Response", "sends emergency resources efficiently", "Disaster response"),
    "immunologist": ("protocol-immunologist", "Protocol Immunologist", "DAO Treasury Defense", "protects treasury capital proportionately", "Protocol security"),
    "heretic": ("scientific-heretic", "Scientific Heretic", "Hypothesis Generation", "proposes novel and falsifiable hypotheses", "Scientific research"),
    "interpreter": ("diplomatic-interpreter", "Diplomatic Interpreter", "Cross-community Mediation", "drafts compromises that reduce polarization", "Community mediation"),
}

LIVE_VERIFICATIONS = {
    "crisis": {
        "run_id": "studionet-verification-2026-08-19",
        "label": "Accepted Studionet verification transaction (reward read from contract)",
        "step": {
            "i": 2,
            "action": {"id": "action-0", "label": "action 0"},
            "state_after": {"bucket": 2, "step": 2},
            "reward": 0.0,
            "reward_kind": "llm",
            "reason": "Reward persisted by the deployed contract after an accepted transaction.",
            "consensus": {
                "outcome": "MAJORITY",
                "validators": [
                    {"vote": "agree"},
                    {"vote": "disagree"},
                    {"vote": "disagree"},
                    {"vote": "agree"},
                    {"vote": "agree"},
                ],
            },
            "tx": {
                "hash": "0xa0e7c9799b29fa1ea51be5e52846eaf80dd9ffa1663d7f465e49ece48a9be5c6",
                "explorer": "https://explorer-studio.genlayer.com/tx/0xa0e7c9799b29fa1ea51be5e52846eaf80dd9ffa1663d7f465e49ece48a9be5c6",
            },
            "notes": [
                {
                    "text": "Accepted Studionet transaction; no leader numeric score or validator model names are claimed.",
                    "source": "genlayer CLI receipt",
                }
            ],
        },
    }
}


def current_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def one_manifest(manifest_id: str) -> dict:
    domain_name, display_name, plain_name, blurb, world = DOMAIN_META[manifest_id]
    domain = get_domain(domain_name)
    agent = QLearningAgent(domain.actions, seed=7)
    env = MockEnvironment(domain, max_steps=8)
    rewards = agent.train(env, episodes=500)

    replay_agent = QLearningAgent(domain.actions, epsilon=0.0, seed=7)
    replay_agent.q = agent.q
    state = env.reset(0)
    steps = []
    for index in range(1, 4):
        action = replay_agent.choose_action(state)
        next_state, reward, done, _ = env.step(action)
        steps.append({
            "i": index,
            "action": {"id": f"action-{action}", "label": f"action {action}"},
            "state_before": {"bucket": state, "step": index},
            "state_after": {"bucket": next_state, "step": index + 1},
            "reward": reward,
            "reward_kind": "deterministic",
            "reason": "Recorded from the local MockEnvironment; no live receipt is claimed.",
            "epsilon": 0.0,
            "illustrative": True,
            "notes": [{"text": "Mock replay only; this step has no on-chain transaction or validator receipt.", "source": "MockEnvironment"}],
        })
        state = next_state
        if done:
            break

    deployment = DEPLOYMENTS["contracts"][manifest_id]
    runs = [{
        "id": "mock-replay",
        "mode": "mock",
        "label": "Local deterministic mock replay (no live receipts)",
        "episodes": [{"i": 1, "steps": steps}],
    }]
    live = LIVE_VERIFICATIONS.get(manifest_id)
    if live:
        runs.append({
            "id": live["run_id"],
            "mode": "live",
            "label": live["label"],
            "episodes": [{"i": 1, "steps": [live["step"]]}],
        })

    return {
        "schema_version": "1.0",
        "domain": {"id": manifest_id, "name": display_name, "plain_name": plain_name, "plain_blurb": blurb, "world": world},
        "provenance": {
            "repo": "https://github.com/luch91/genlayer-RL-agent-autonomy",
            "commit": current_commit(),
            "sdk": "genlayer-py >=0.2.9",
            "runner_pin": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "contract": {
            "address": deployment["address"],
            "chain": DEPLOYMENTS["chain"],
            "explorer": f"{DEPLOYMENTS['explorer']}/address/{deployment['address']}",
        },
        "reward": {
            "kind": "llm_comparative",
            "scale": [0, 10],
            "principle": "Validator scores are accepted when they differ by at most 20 points on the 0-100 judge scale.",
            "prompt_template": "Score the domain action from 0 to 100 and return JSON with an integer score.",
        },
        "learning": {
            "rolling_window": 20,
            "episodes": [{"i": i + 1, "reward": round(reward / env.max_steps, 3)} for i, reward in enumerate(rewards)],
            "epsilon": [{"i": i + 1, "value": round(max(agent.min_epsilon, 1.0 * agent.epsilon_decay ** (i + 1)), 6)} for i in range(500)],
        },
        "runs": runs,
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for manifest_id in DOMAIN_META:
        path = OUT / f"{manifest_id}.json"
        path.write_text(json.dumps(one_manifest(manifest_id), indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
