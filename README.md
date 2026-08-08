# GenLayer RL Agent Autonomy

**Reinforcement learning agents that learn contested, human-like judgment from an on-chain, LLM-consensus reward - a reward the agent cannot rewrite.**

Traditional RL needs a numeric reward someone writes by hand. That works for chess and Atari. It breaks the moment the thing you care about is subjective: *was that a good triage decision, is this hypothesis genuinely novel, did this compromise lower the temperature in the room.*

GenLayer changes the input to that equation. Intelligent Contracts are Python contracts that call LLMs natively and reach consensus on non-deterministic outputs through Optimistic Democracy. So the reward signal itself can be a judgment call - evaluated by a committee of validators running diverse models, and recorded immutably on-chain. This project connects a normal off-chain RL agent to that on-chain judge.

The agent never sees the rubric. It acts, gets scored by the LLM-consensus reward, updates its policy, and repeats. Over enough rounds it converges on behavior that satisfies human-like judgment, not a hard-coded number. **The reward logic lives in a deployed contract, so the agent cannot rewrite it. That immutability is the safety property** that makes an open-ended "here are the controls, improve" loop tractable instead of reckless.

Framed honestly: this is subjective-reward RL on-chain (RLAIF, judged by validator consensus). It is **not** open-ended self-modification. The agent optimizes a fixed, external, immutable objective. That constraint is a feature.

## Live dashboard

All four agents are visualized in one place: **[the GenLayer RL Demo Suite](https://luch91-org.github.io/genlayer-rl-demo-suite/)**. It is a pure reader of each agent's published `manifest.json` - watch the reward climb over training, step through a recorded episode, read the on-chain judge's verdict for each step, inspect why the agent chose each action, and read the deployed contract's live state. Source and setup: [`genlayer-rl-demo-suite`](https://github.com/luch91-org/genlayer-rl-demo-suite).

![The instrument panel replaying a trained crisis-response episode: the world state, the on-chain judge score, the step timeline, and the policy inspector all advance together, step by step.](https://raw.githubusercontent.com/luch91-org/genlayer-rl-demo-suite/main/docs/instrument-panel.gif)

*Recorded from the live dashboard: the instrument panel stepping through a trained crisis-response rollout. Each step updates the world state, the judge's score, the reward chip, and the policy inspector that explains why the agent chose that action.*

## The loop

```
   off-chain (your machine)                  on-chain (GenLayer)
 ┌───────────────────────────┐        ┌──────────────────────────────┐
 │  RL agent                 │  read  │  Intelligent Contract         │
 │  - reads state            │ <───── │  - holds the environment state│
 │  - picks an action (ε-greedy)      │  - applies the action         │
 │  - updates Q-table        │  write │  - LEADER calls an LLM to     │
 │    from the reward        │ ─────> │    score the new state        │
 │                           │        │  - VALIDATORS agree on the    │
 │                           │ reward │    score via eq_principle     │
 │                           │ <───── │  - records reward on-chain    │
 └───────────────────────────┘        └──────────────────────────────┘
```

The contract is the scorekeeper. The agent is the student. The student keeps guessing, the scorekeeper grades, the student rewrites its notes.

## The four domains

Each domain is included in this self-contained repository. All four contracts
are deployed and verified live on the hosted GenLayer Studio network
(`studionet`); the exact addresses are recorded in [`deployments.json`](deployments.json).

| Contract | Domain | The agent learns to | Verified Studionet address |
|---|---|---|---|
| [`contracts/crisis_negotiator.py`](contracts/crisis_negotiator.py) | Disaster response | Dispatch drones, ambulances, and supplies to critical zones without wasting capacity | `0x9d718F8AAb76517D14917483e1c9Cbd6267aDe24` |
| [`contracts/protocol_immunologist.py`](contracts/protocol_immunologist.py) | DAO treasury defense | Pause, rotate signers, and hedge to preserve capital - but only when a threat is actually trending | `0xC23006cAF6D3b25288F77988592675Bd5439Ed35` |
| [`contracts/scientific_heretic.py`](contracts/scientific_heretic.py) | Hypothesis generation | Propose novel, falsifiable, plausible hypotheses a peer reviewer would find interesting | `0x7847A35eA8C3Bb887C20E5B64BF035e99abd4B16` |
| [`contracts/diplomatic_interpreter.py`](contracts/diplomatic_interpreter.py) | Cross-community mediation | Draft compromises that lower polarization and raise the odds of agreement on both sides | `0xA47132D18B0eD7588426B6234f74d4A15170a4e0` |

> Studio is a shared sandbox that can be reset. If an address stops resolving,
> redeploy the corresponding contract with `genlayer deploy --contract
> contracts/<domain>.py --rpc https://studio.genlayer.com/api` and update
> `deployments.json` only after verifying the new address with `get_state`.

## How this repository is organized

This repository is a self-contained monorepo submission. It includes all four
domains, their Intelligent Contracts, the off-chain Q-learning agent, the
`genlayer-py` transport adapter, and tests for the complete read → write →
reward → Q-table update path.

- `contracts/` contains one deployable contract per domain.
- `agent/env.py` contains the local mock and live SDK environments.
- `agent/q_learning.py` implements epsilon-greedy Q-learning and persistence.
- `agent/train.py` is the runnable training entry point.
- `tests/` verifies the agent and SDK-shaped integration path.
- `policies/` contains reproducible trained Q-table artifacts for all four domains.
- `manifests/` contains demo-suite-compatible metadata, mock learning curves,
  and explicitly labeled mock replays. `deployments.json` records only
  contracts that were accepted by Studionet and verified with `get_state()`.

The older domain repositories and release notes remain useful references, but
they are not required to run or evaluate this repository.

## Why GenLayer specifically

- **Native LLM calls inside the contract.** The reward function is a prompt, not a formula.
- **Validator consensus on subjective outputs.** A single model can be gamed or biased; a diverse committee agreeing under an equivalence principle is far harder to exploit.
- **Immutability.** Once deployed, the reward function cannot be edited by the agent. No wireheading the scorer.
- **Native web access.** Rewards can be grounded in live real-world data with no external oracle.

No other chain lets a reward function say *"score this on diplomatic tact"* and have that score be trustlessly agreed upon.

## What "done" looks like (and what shipped)

Every repo delivers all of the following, and all four are complete:

1. A deployed Intelligent Contract defining state, action space, and an LLM-consensus reward - running on the public Studio testnet with a real address.
2. An off-chain tabular Q-learning agent (ε-greedy, save/resume) that queries state, sends transactions, and learns from the returned reward.
3. **Measurable learning:** rolling per-step reward climbs from ~3-4 to ~8+ over 500 mock episodes. The curve is saved and plotted, not just asserted.
4. A saved policy (`q_table.json`) attached to the release so a reviewer can load a trained agent without retraining.
5. Docs a beginner can follow end to end, plus a live-verified on-chain episode log.

A `MockEnv` (instant, free) is the default for development and CI; a `GenLayerEnv` switches the same agent onto the chain for the real demo.

## Design principles (load-bearing across all four)

- **On-chain reward is slow and costs gas** - never develop RL logic by hammering the chain. Mock first; chain for the demo.
- **LLM rewards are noisy and non-stationary** - the same state won't always score identically; agents smooth and treat consensus as ground truth.
- **Subjective scores never match byte-for-byte** - reward comparison uses a comparative equivalence principle, never `strict_eq`.
- **One concrete LLM number, everything downstream deterministic** - a vaguer multi-facet reward spreads validator scores past tolerance and returns `NO_MAJORITY`. (Learned live; see the `scientific-heretic` and `diplomatic-interpreter` write-ups.)
- **The reward is immutable once deployed.** The agent optimizes it; it cannot edit it.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt

pytest -q
python -m agent.train --domain crisis-negotiator --env mock --episodes 500
# Resume from a saved policy:
python -m agent.train --domain crisis-negotiator --env mock --resume policies/crisis-negotiator-q_table.json --episodes 50
```

Then run the same agent against a deployed contract:

```bash
pip install -e '.[chain]'
python -m agent.train --domain crisis-negotiator --env genlayer --address 0x... --episodes 3
```

The live adapter reads `get_state`, submits `take_action` through
`genlayer-py`, waits for the receipt, reads `get_last_reward`, and reads the
next state. Repeat `--domain` for the other three domains. No Node bridge is
required.

Export or refresh the truthful dashboard manifests after training or a new
deployment:

```bash
python scripts/export_manifests.py
```

Mock replay steps are marked `illustrative` and contain no fabricated
transaction hashes, validator votes, or live receipts.

## Contributing

Issues and Discussions are open on each domain repo. Pick a domain, read its `README.md` and `docs/tutorial.md`, claim an issue, and open a PR under [Conventional Commits](https://www.conventionalcommits.org/). CI must pass, and PRs touching the agent should include a short training-log snippet showing the curve.

## Vision

The first open playground where agents don't just execute tasks - they learn contested, human-like judgment from subjective feedback agreed upon by a decentralized committee and written to a blockchain. Small, legible, forkable. A concrete step toward autonomous systems whose objectives are transparent, external, and impossible for the agent to quietly rewrite.

---

*Sources of truth for the SDK and contract APIs: [docs.genlayer.com](https://docs.genlayer.com) and [sdk.genlayer.com](https://sdk.genlayer.com). Licensed MIT.*
