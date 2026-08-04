# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""ScientificHeretic Intelligent Contract.

Hypothesis generation. The agent either PROPOSES a hypothesis (free text)
or TESTS the most recent untested one.

PROPOSE is the LLM-judged action: an LLM peer reviewer scores the hypothesis
0-10 on falsifiability, novelty (relative to what has already been proposed
this session), and plausibility, and validators reach consensus on that
score via a comparative equivalence principle (never strict_eq for a
subjective judgment). This concrete three-part rubric keeps validators'
scores tightly clustered, so consensus is stable.

TEST is fully DETERMINISTIC -- no LLM call. Its payoff is entirely
determined by the hypothesis's already-consensus-agreed merit score: a
falsifiable, high-merit hypothesis that gets tested is "validated" and earns
a worthwhile-experiment reward plus a validation bonus; a low-merit one
wastes effort. This mirrors the domain spec exactly ("Reward prompt scores
falsifiability, novelty, and plausibility. Correct later validation grants a
bonus") and, just as importantly, keeps consensus robust: a vaguer "was this
experiment worthwhile?" LLM prompt made validators disagree beyond tolerance
on a live shared testnet and intermittently return NO_MAJORITY. A
deterministic test transition every validator computes identically has no
such failure mode. Nature's "answer" to an experiment must not be a fresh
coin flip, or validators would never agree on the post-state.

This file is deliberately SELF-CONTAINED (single-file deployment; no sibling
imports). Off-chain, contracts/logic.py execs this source with a stubbed
`genlayer` module so pytest exercises the deployed code itself.

GenVM constraints baked in (confirmed on live studionet deploys in sibling
repos, 2026-07):
  - Storage uses GenVM types only: u256 / str / DynArray[...] -- never bare
    dict/list, and booleans-in-arrays are stored as u256 0/1 (DynArray[bool]
    is avoided for portability).
  - Floats are neither storable nor calldata-encodable; scores are integers
    scaled x100 on-chain (7.5 -> 750). Floats exist only inside the JSON
    string exchanged through the equivalence principle.
  - gl.eq_principle.prompt_comparative(fn, principle=...) and
    gl.nondet.exec_prompt(prompt, response_format="json") (returns a parsed
    dict) are the current API forms.
"""

import json

from genlayer import *

# --- pure deterministic helpers (exec'd off-chain by contracts/logic.py) ----

# A hypothesis is "validated" when it is tested AND its already-agreed merit
# score is at least this threshold AND it was judged falsifiable.
VALIDATION_SCORE_THRESHOLD_X100 = 600
VALIDATION_BONUS = 2.0

# Deterministic rewards for the (non-LLM) test action.
TEST_REWARD_WORTHWHILE = 7.0  # testing a falsifiable, high-merit hypothesis
TEST_REWARD_WEAK = 3.0  # testing a low-merit or unfalsifiable hypothesis
TEST_REWARD_NO_TARGET = 1.0  # tried to test with nothing untested pending

REWARD_EQUIVALENCE_PRINCIPLE = (
    "The two evaluations agree if their numeric scores are within 1.5 points "
    "of each other, any boolean verdicts (such as falsifiability) match, and "
    "they express the same overall judgment. Wording may differ."
)


def clamp_score(value: float) -> float:
    return max(0.0, min(10.0, float(value)))


def score_to_x100(score: float) -> int:
    """Floats are not calldata-encodable and not GenVM-storable, so scores
    live on-chain as integers scaled x100 (7.5 -> 750)."""
    return int(round(float(score) * 100))


def build_propose_prompt(text: str, existing_json: str, round_number: int) -> str:
    return (
        "You are a peer reviewer evaluating a newly proposed scientific hypothesis.\n"
        f"Already-proposed hypotheses this session: {existing_json}\n"
        f"Newly proposed hypothesis: {text}\n"
        f"Round: {round_number}\n\n"
        "Score it 0-10 on three merits weighted equally: falsifiability (can it "
        "be empirically refuted?), novelty (is it new relative to the "
        "already-proposed list, and not a textbook-trivial fact?), and "
        "plausibility (is it scientifically reasonable, not absurd?). A vague or "
        "untestable claim scores low; a restatement of an existing or textbook "
        "fact scores low on novelty; an absurd claim scores low on plausibility.\n"
        'Return ONLY JSON: {"score": <number 0-10>, "falsifiable": <true|false>, '
        '"reason": "<short reason>"}'
    )


def parse_propose_output(raw) -> tuple:
    """Parse an LLM propose-score response into (score, falsifiable, reason).

    Accepts either an already-parsed dict (gl.nondet.exec_prompt output) or a
    JSON string; clamps the score to [0, 10]; defaults a missing falsifiable
    flag to False (conservative: an un-flagged hypothesis will not validate)."""
    data = json.loads(raw) if isinstance(raw, str) else raw
    score = clamp_score(data["score"])
    falsifiable = bool(data.get("falsifiable", False))
    reason = str(data.get("reason", ""))
    return score, falsifiable, reason


def normalize_propose(score: float, falsifiable: bool, reason: str) -> str:
    return json.dumps(
        {"score": float(score), "falsifiable": bool(falsifiable), "reason": str(reason)},
        sort_keys=True,
    )


def is_validated(falsifiable: bool, score_x100: int) -> bool:
    """Deterministic: a falsifiable, high-merit hypothesis validates when
    tested. Reads only already-agreed stored state, so it is identical on
    every validator."""
    return bool(falsifiable) and int(score_x100) >= VALIDATION_SCORE_THRESHOLD_X100


# --- the contract itself -----------------------------------------------------


class ScientificHeretic(gl.Contract):
    # Parallel arrays instead of an array-of-structs: simplest storage shape
    # that stays within GenVM's supported types. Booleans are u256 0/1.
    hypothesis_texts: DynArray[str]
    hypothesis_score_x100: DynArray[u256]
    hypothesis_falsifiable: DynArray[u256]
    hypothesis_tested: DynArray[u256]
    hypothesis_validated: DynArray[u256]
    round: u256
    total_score_x100: u256
    last_reward_x100: u256
    last_reason: str

    def __init__(self):
        self.round = u256(0)
        self.total_score_x100 = u256(0)
        self.last_reward_x100 = u256(0)
        self.last_reason = ""

    @gl.public.view
    def get_state(self) -> dict:
        return {
            "hypothesis_texts": [str(t) for t in self.hypothesis_texts],
            "hypothesis_score_x100": [int(s) for s in self.hypothesis_score_x100],
            "hypothesis_falsifiable": [int(f) for f in self.hypothesis_falsifiable],
            "hypothesis_tested": [int(t) for t in self.hypothesis_tested],
            "hypothesis_validated": [int(v) for v in self.hypothesis_validated],
            "num_hypotheses": len(self.hypothesis_texts),
            "round": int(self.round),
            "total_score_x100": int(self.total_score_x100),
            "last_reward_x100": int(self.last_reward_x100),
            "last_reason": self.last_reason,
        }

    def _last_untested_index(self) -> int:
        idx = -1
        for i in range(len(self.hypothesis_tested)):
            if int(self.hypothesis_tested[i]) == 0:
                idx = i  # keep overwriting -> ends on the MOST RECENT untested
        return idx

    @gl.public.write
    def take_action(self, action: dict) -> dict:
        self.round = u256(int(self.round) + 1)
        round_after = int(self.round)
        a_type = action.get("type")

        if a_type == "propose":
            # The only LLM-judged path: an eq_principle consensus call.
            reward, reason = self._do_propose(str(action.get("text", "")), round_after)
        elif a_type == "test":
            reward, reason = self._do_test()  # deterministic, no LLM call
        else:
            # Unrecognized action: a wasted round, scored deterministically.
            reward, reason = TEST_REWARD_NO_TARGET, "unrecognized action"

        reward_x100 = score_to_x100(reward)
        self.total_score_x100 = u256(int(self.total_score_x100) + reward_x100)
        self.last_reward_x100 = u256(reward_x100)
        self.last_reason = reason
        return {"reward_x100": reward_x100, "reason": reason, "round": round_after}

    def _do_propose(self, text: str, round_after: int) -> tuple:
        # Snapshot into LOCALS (self is not accessible inside the nondet block).
        existing_snap = json.dumps([str(t) for t in self.hypothesis_texts], sort_keys=True)
        text_snap = text
        round_snap = round_after

        def score_block() -> str:
            prompt = build_propose_prompt(text_snap, existing_snap, round_snap)
            out = gl.nondet.exec_prompt(prompt, response_format="json")
            score, falsifiable, reason = parse_propose_output(out)
            return normalize_propose(score, falsifiable, reason)

        raw = gl.eq_principle.prompt_comparative(
            score_block, principle=REWARD_EQUIVALENCE_PRINCIPLE
        )
        score, falsifiable, reason = parse_propose_output(raw)

        self.hypothesis_texts.append(text)
        self.hypothesis_score_x100.append(u256(score_to_x100(score)))
        self.hypothesis_falsifiable.append(u256(1 if falsifiable else 0))
        self.hypothesis_tested.append(u256(0))
        self.hypothesis_validated.append(u256(0))
        return score, reason

    def _do_test(self) -> tuple:
        """Deterministic -- no LLM call. Tests the most recent untested
        hypothesis; the reward is fixed by that hypothesis's already-agreed
        merit, so every validator computes the identical result and reward."""
        idx = self._last_untested_index()
        if idx == -1:
            return TEST_REWARD_NO_TARGET, "tried to test with no untested hypothesis"

        falsifiable = int(self.hypothesis_falsifiable[idx]) == 1
        h_score_x100 = int(self.hypothesis_score_x100[idx])
        validated = is_validated(falsifiable, h_score_x100)

        self.hypothesis_tested[idx] = u256(1)
        if validated:
            self.hypothesis_validated[idx] = u256(1)
            reward = clamp_score(TEST_REWARD_WORTHWHILE + VALIDATION_BONUS)
            return reward, "[validated] tested a falsifiable, high-merit hypothesis"
        return TEST_REWARD_WEAK, "tested a low-merit or unfalsifiable hypothesis"

    @gl.public.view
    def get_score(self) -> int:
        """Total accumulated score, scaled x100 (divide by 100 off-chain)."""
        return int(self.total_score_x100)
