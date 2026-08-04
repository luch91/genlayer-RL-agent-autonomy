# Submission brief: GenLayer RL Agent Autonomy

Reinforcement-learning agents that learn contested, human-like judgment from an
on-chain, LLM-consensus reward the agent cannot rewrite. Four independent domains,
all deployed and verified live on the GenLayer Studio network, plus a live dashboard.

## Project thesis

The reward function is the hardest, least-examined part of applied RL. When the
objective is subjective, teams either fake a proxy metric or hand-label forever.
GenLayer offers a third option: put the judgment inside an Intelligent Contract, let
a diverse validator committee agree on it under an equivalence principle, and make it
immutable so the learner cannot game the scorer. This project is the first open,
forkable template for that pattern. It proves the loop end to end on four genuinely
subjective domains, and it is deliberately small and legible (tabular Q-learning,
discrete states) so the learning is readable line by line. The claim is narrow and
honest: this is subjective-reward RL on-chain (RLAIF judged by validator consensus),
not open-ended self-modification. The agent optimizes a fixed external objective it
cannot edit. That constraint is the feature.

## Deployed contracts (live on studionet)

Each contract stores the state and action space, and scores each action 0 to 10 with
an LLM call agreed by validators via `gl.eq_principle.prompt_comparative` at tolerance
1.5 (never `strict_eq`). Sources are vendored in `contracts/` in this repository.

| Contract | Source in this repo | Address | Explorer | Sample scoring tx |
|---|---|---|---|---|
| Crisis Response | [crisis_negotiator.py](contracts/crisis_negotiator.py) | `0xE0CBc71F7a3e87523F4A3833d4DdBE8a47595220` | [address](https://explorer-studio.genlayer.com/address/0xE0CBc71F7a3e87523F4A3833d4DdBE8a47595220) | [tx](https://explorer-studio.genlayer.com/tx/0xe32e2fb4c87777c4f360816824e1181b7dced9f7fde04f2a84361adc4bfc3803) |
| Treasury Defense | [protocol_immunologist.py](contracts/protocol_immunologist.py) | `0x4213C3915a314B7A4ef926895A08638F54aE55dd` | [address](https://explorer-studio.genlayer.com/address/0x4213C3915a314B7A4ef926895A08638F54aE55dd) | [tx](https://explorer-studio.genlayer.com/tx/0x44d2b2e8109c444b0bb9eeea34312e888fe336d65fb8922b62fb278d64f8e6d6) |
| Science Ideas | [scientific_heretic.py](contracts/scientific_heretic.py) | `0xDd169FA2FA5D258f1CCBc8CAe61eA652733435F6` | [address](https://explorer-studio.genlayer.com/address/0xDd169FA2FA5D258f1CCBc8CAe61eA652733435F6) | [tx](https://explorer-studio.genlayer.com/tx/0x71bb80ec7438f55b0f3681e3f5da0c4186c6ef1705d26981a196a9ff1a1a9479) |
| Community Mediator | [diplomatic_interpreter.py](contracts/diplomatic_interpreter.py) | `0xA5cf174b2fDC77058C181435040121711312EE15` | [address](https://explorer-studio.genlayer.com/address/0xA5cf174b2fDC77058C181435040121711312EE15) | [tx](https://explorer-studio.genlayer.com/tx/0xf6afecef452d2f101d80cece3c706c9aa4e9235955ab3cee676d06e837e05afa) |

See [`contracts/README.md`](contracts/README.md) for the full index. Studio is a
resettable sandbox; the committed `logs/training_live_studionet.txt` in each domain
repo is the durable proof of on-chain interaction if an address stops resolving.

## Source

| Repository | Purpose | Link |
|---|---|---|
| Umbrella (this repo) | Spec, index, vendored contracts | https://github.com/luch91-org/genlayer-RL-agent-autonomy |
| Crisis Negotiator | Disaster-response dispatch | https://github.com/luch91-org/genlayer-rl-crisis-negotiator |
| Protocol Immunologist | DAO treasury defense | https://github.com/luch91-org/genlayer-rl-protocol-immunologist |
| Scientific Heretic | Hypothesis generation | https://github.com/luch91-org/genlayer-rl-scientific-heretic |
| Diplomatic Interpreter | Cross-community mediation | https://github.com/luch91-org/genlayer-rl-diplomatic-interpreter |
| Demo Suite (source) | Manifest-driven dashboard | https://github.com/luch91-org/genlayer-rl-demo-suite |
| Live dashboard | Hosted, interactive | https://luch91-org.github.io/genlayer-rl-demo-suite/ |

Trained-policy releases (each carries `q_table.json`):
[crisis](https://github.com/luch91-org/genlayer-rl-crisis-negotiator/releases/tag/v0.1.0-alpha) |
[immunologist](https://github.com/luch91-org/genlayer-rl-protocol-immunologist/releases/tag/v0.1.0-alpha) |
[heretic](https://github.com/luch91-org/genlayer-rl-scientific-heretic/releases/tag/v0.1.0-alpha) |
[interpreter](https://github.com/luch91-org/genlayer-rl-diplomatic-interpreter/releases/tag/v0.1.0-alpha)

## Review guide (five minutes)

1. Open the live dashboard: https://luch91-org.github.io/genlayer-rl-demo-suite/
2. Learning curve tab: watch the agent reward climb past the random and greedy baselines.
3. Episode player: step a recorded rollout and watch the on-chain judge score each action.
4. On-chain receipt tab: see the contract address, tx hash, and validator consensus
   (agree, disagree, idle, timeout), with a "Show the judge's prompt" reveal on Science
   Ideas and Community Mediator.
5. Verify interaction is real: open `logs/training_live_studionet.txt` in any domain repo
   for a run made against `env=genlayer`.

### Flagship walkthrough A: Crisis Response

- Use case: an agent dispatches drones, ambulances, and supply kits across three
  emergency zones, learning to save critical zones without wasting capacity.
- Contract and reward: [`contracts/crisis_negotiator.py`](contracts/crisis_negotiator.py)
  holds zone state and applies each action. The LEADER validator calls an LLM to score
  the dispatch 0 to 10; validators agree within 1.5 points via the comparative
  equivalence principle. The agent never sees the rubric.
- Agent loop: epsilon-greedy tabular Q-learning with optimistic init and save/resume.
  `MockEnv` is the free default; `GenLayerEnv` runs the identical policy on-chain via
  genlayer-py 0.18.0 (`create_client`, `read_contract`, `write_contract`).
- Result: across 500 mock episodes the rolling per-step reward climbs from ~3.3 to ~8.1.
- Live proof: a real studionet run at about 39 seconds per step, the contract scoring
  each dispatch. Log committed.
- Repo: https://github.com/luch91-org/genlayer-rl-crisis-negotiator

### Flagship walkthrough B: Community Mediator (Diplomatic Interpreter)

- Use case: an agent drafts compromise statements between two communities, learning to
  lower polarization and raise the odds both sides accept.
- Contract and reward:
  [`contracts/diplomatic_interpreter.py`](contracts/diplomatic_interpreter.py) scores a
  proposed statement 0 to 10 on fairness and fit to the current polarization level. The
  right move is state-dependent: high polarization needs a detailed concrete plan; once
  settled a concise consolidation fits best.
- Result: 500 mock episodes climb from ~3.5 to ~8.8 per step.
- Live proof (the strongest on-chain result in the suite): a full trained-agent episode
  of 5 on-chain LLM-consensus steps, per-step average 7.60, with the dispute cooling
  monotonically from 0.80 to 0.23 polarization (a 57% drop) and no `NO_MAJORITY`. The
  state dependence is real on-chain: the concise consolidation scores about 6 while
  polarization is high (it reads as dismissive of live grievances) and about 8 once
  settled.
- Repo: https://github.com/luch91-org/genlayer-rl-diplomatic-interpreter

## Engineering log / live-run findings

Learning results (per-step reward, 500 mock episodes; all four converge into the
"strong" band):

| Domain | Start | Converged | Live on-chain run |
|---|---|---|---|
| Crisis Response | ~3.3 | ~8.1 | real dispatch scoring, ~39 s/step |
| Treasury Defense | ~4.0 | ~8.0 | ~706 s multi-episode, rewarded "paused during a red alert", 10 states |
| Science Ideas | ~3.7 | ~8.8 | 4 on-chain steps, per-step average 8.00 |
| Community Mediator | ~3.5 | ~8.8 | 5 on-chain steps, avg 7.60, polarization 0.80 to 0.23, no NO_MAJORITY |

Findings that only live on-chain runs surfaced:

- Consensus tolerance is real (Science Ideas). The `test` action was originally
  LLM-scored. On the shared testnet that vaguer prompt spread validator scores past the
  equivalence tolerance and intermittently returned `NO_MAJORITY`, so the transaction
  never landed. Making `test` deterministic (its payoff fixed by the already-agreed
  merit) is both more spec-faithful and consensus-robust. Live testing caught what
  offline testing structurally could not.
- One concrete number per reward. A reward prompt that folds several fuzzy facets into
  one number keeps validators inside tolerance; a vaguer multi-facet prompt does not.
  Every reward converged on a single 0-to-10 output.
- GenVM storage constraints, confirmed the hard way. Storage fields cannot be bare
  `dict` (use `TreeMap`), and floats are not calldata-encodable, so scores are integers
  scaled by 100. Documented inline in each contract with the failing tx that proved it.
- State-dependence holds on-chain (Community Mediator). The same statement scored
  differently at different polarization levels in the live run, matching the mock
  environment.

## Other links

- Demo GIF (instrument panel replaying a trained episode):
  https://raw.githubusercontent.com/luch91-org/genlayer-rl-demo-suite/main/docs/instrument-panel.gif
- Per-domain tutorials: `docs/tutorial.md` in each domain repo.
- Learning curves: `docs/learning_curve.png` in each domain repo.
- Org profile and index: https://github.com/luch91-org
- Tech stack: GenLayer Intelligent Contracts (Python, GenVM),
  `gl.eq_principle.prompt_comparative`; off-chain transport via genlayer-py 0.18.0
  (Python >= 3.12); tabular Q-learning; Next.js static-export dashboard on GitHub Pages.
- License: MIT (all domain repos).
