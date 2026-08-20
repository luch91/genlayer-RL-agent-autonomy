# Decisions Log

This log records architectural decisions and future milestones for the GenLayer
RL agent autonomy project. Milestones are planned work; they are not claims that
the functionality is already implemented.

## Decision 001 — Fixed on-chain environment objective

The contract owns the problem definition, valid action space, state transitions,
reward function, and terminal condition. The agent controls only the action being
judged. The Q-table remains off-chain, while its updates consume rewards returned
by accepted contract transactions.

Status: adopted.

## Milestone roadmap

### Phase 1 — Auditable live loop

- [ ] Fully reproducible live training: deploy, train one episode, record outputs,
  and produce the resulting Q-table with one documented command.
- [ ] Receipt-backed training logs: record transaction hashes, accepted rewards,
  states, actions, consensus status, and Q-value updates for every step.
- [ ] Deterministic replay: reconstruct an episode from contract reads and accepted
  transaction records.

### Phase 2 — Environment and policy integrity

- [ ] Contract-level guarantees: test invalid actions, post-terminal actions, and
  objective changes are rejected.
- [ ] Reward integrity and anti-wireheading: prevent the agent from modifying or
  supplying the reward, objective, state rules, or terminal conditions.
- [ ] Multi-episode lifecycle: add a controlled reset or new-episode mechanism
  without allowing the agent to alter the objective.
- [ ] On-chain policy commitments: publish a verifiable hash for each Q-table or
  policy version.

### Phase 3 — Reliability and operational evidence

- [ ] Gas and latency benchmark: measure deployment cost, per-action cost,
  consensus latency, and cost per episode.
- [ ] Training checkpoints and recovery: resume safely after RPC failures,
  rejected transactions, timeouts, or partial episodes.
- [ ] Reward-noise analysis: measure validator disagreement, reward variance, and
  learning stability across repeated actions.
- [ ] Security and adversarial testing: cover malformed actions, replayed
  transactions, stale states, malicious callers, and reward manipulation.

### Phase 4 — Evaluation and expansion

- [ ] Policy evaluation: compare learned, random, greedy, and hand-designed
  policies in identical environments.
- [ ] Domain expansion: add richer state/action spaces or another domain while
  preserving the shared contract and SDK interface.
- [ ] Public benchmark release: publish datasets, logs, evaluation scripts,
  contract versions, and baseline results.

### Phase 5 — Submission-quality release

- [ ] Versioned contracts and tagged releases.
- [ ] Live verification report with real addresses and receipts only.
- [ ] Architecture diagram and beginner-runnable documentation.
- [ ] End-to-end demo showing: contract state → agent action → accepted
  transaction → on-chain reward → Q-table update → next action.

## Working rule

Milestones will be revisited and implemented phase by phase. Before claiming a
milestone complete, add tests, documentation, and verifiable evidence appropriate
to that milestone. Never fabricate live addresses, transaction hashes, receipts,
validator votes, or training results.
