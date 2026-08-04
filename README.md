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

Each is a **fully independent, forkable repository**. All four are deployed and verified live on the hosted GenLayer Studio network (`studionet`), and each is tagged `v0.1.0-alpha` with a trained `q_table.json` attached to its release.

| Repository | Domain | The agent learns to | Live on studionet |
|---|---|---|---|
| [`genlayer-rl-crisis-negotiator`](https://github.com/luch91-org/genlayer-rl-crisis-negotiator) | Disaster response | Dispatch drones, ambulances, and supplies to critical zones without wasting capacity | [`0xE0CB…5220`](https://github.com/luch91-org/genlayer-rl-crisis-negotiator#verified-live-deployment) |
| [`genlayer-rl-protocol-immunologist`](https://github.com/luch91-org/genlayer-rl-protocol-immunologist) | DAO treasury defense | Pause, rotate signers, and hedge to preserve capital - but only when a threat is actually trending | [`0x4213…55dd`](https://github.com/luch91-org/genlayer-rl-protocol-immunologist#verified-live-deployment) |
| [`genlayer-rl-scientific-heretic`](https://github.com/luch91-org/genlayer-rl-scientific-heretic) | Hypothesis generation | Propose novel, falsifiable, plausible hypotheses a peer reviewer would find interesting | [`0xDd16…35F6`](https://github.com/luch91-org/genlayer-rl-scientific-heretic#verified-live-deployment) |
| [`genlayer-rl-diplomatic-interpreter`](https://github.com/luch91-org/genlayer-rl-diplomatic-interpreter) | Cross-community mediation | Draft compromises that lower polarization and raise the odds of agreement on both sides | [`0xA5cf…EE15`](https://github.com/luch91-org/genlayer-rl-diplomatic-interpreter#verified-live-deployment) |

> Studio is a shared sandbox that can be reset; if an address stops resolving, redeploy with `python -m agent.deploy --chain studionet` and substitute the fresh address.

## How this repository is organized

This repository is the umbrella index for the suite. It holds the shared engineering spec, the organization profile, and the release notes. It coordinates the four domain repositories.

This repository also vendors the four deployed Intelligent Contracts under `contracts/`. Each file is the exact source that runs on the GenLayer Studio network. See `contracts/README.md` for the deployed address, the explorer link, and the canonical source repository of each contract.

The full RL system lives in the four domain repositories. Each domain repository is independent. Each domain repository contains its own code:

- `contracts/` holds the Intelligent Contract. The contract defines the state, the actions, and the LLM-consensus reward.
- `agent/` holds the off-chain Q-learning agent. The agent reads the state, sends actions, and learns from the reward.
- `tests/` holds the contract tests and the agent tests.

The demo suite is a separate repository. It reads the `manifest.json` file that each domain repository publishes. It does not hold RL code.

Each part has a clear job. This repository indexes the suite and mirrors the deployed contracts. The four domain repositories implement. The demo suite shows the results.

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
git clone https://github.com/luch91-org/genlayer-rl-crisis-negotiator.git
cd genlayer-rl-crisis-negotiator
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r agent/requirements.txt

python -m agent.train --env mock --episodes 500     # free, instant
python -m agent.plot                                # renders the learning curve
```

Then deploy and run against the real chain:

```bash
python -m agent.deploy --chain studionet
python -m agent.train --env genlayer --chain studionet --address 0x... --episodes 3
```

Off-chain transport is the first-party [`genlayer-py`](https://pypi.org/project/genlayer-py/) SDK (Python ≥ 3.12) - no Node bridge required.

## Contributing

Issues and Discussions are open on each domain repo. Pick a domain, read its `README.md` and `docs/tutorial.md`, claim an issue, and open a PR under [Conventional Commits](https://www.conventionalcommits.org/). CI must pass, and PRs touching the agent should include a short training-log snippet showing the curve.

## Vision

The first open playground where agents don't just execute tasks - they learn contested, human-like judgment from subjective feedback agreed upon by a decentralized committee and written to a blockchain. Small, legible, forkable. A concrete step toward autonomous systems whose objectives are transparent, external, and impossible for the agent to quietly rewrite.

---

*Sources of truth for the SDK and contract APIs: [docs.genlayer.com](https://docs.genlayer.com) and [sdk.genlayer.com](https://sdk.genlayer.com). Licensed MIT.*
