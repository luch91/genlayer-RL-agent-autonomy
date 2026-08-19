"""Domain definitions shared by the four runnable agents."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Domain:
    name: str
    contract_method: str = "take_action"
    state_method: str = "get_state"
    reward_method: str = "get_last_reward"
    problem_method: str = "get_problem_definition"
    step_method: str = "get_step_count"
    terminal_method: str = "is_terminal"
    actions: tuple[int, ...] = (0, 1, 2)
    states: tuple[int, ...] = (0, 1, 2, 3, 4)
    max_steps: int = 8
    problem_definition: str = ""


DOMAINS = {
    "crisis-negotiator": Domain(
        "crisis-negotiator",
        problem_definition=(
            "Crisis response: state is a 0-4 urgency bucket; actions 0, 1, 2 are "
            "dispatch choices; the contract scores efficient life-saving allocation "
            "on a 0-10 scale and advances state by (state + action + 1) mod 5; "
            "the episode ends after 8 accepted actions."
        ),
    ),
    "protocol-immunologist": Domain(
        "protocol-immunologist",
        problem_definition=(
            "DAO treasury defense: state is a 0-4 threat-regime bucket; actions 0, 1, 2 "
            "are defensive choices; the contract scores protection with restraint on a "
            "0-10 scale and advances state by (state + action + 1) mod 5; the episode "
            "ends after 8 accepted actions."
        ),
    ),
    "scientific-heretic": Domain(
        "scientific-heretic",
        problem_definition=(
            "Scientific research: state is a 0-4 research bucket; actions 0, 1, 2 are "
            "research choices; the contract scores novelty, plausibility, and "
            "falsifiability on a 0-10 scale and advances state by (state + action + 1) "
            "mod 5; the episode ends after 8 accepted actions."
        ),
    ),
    "diplomatic-interpreter": Domain(
        "diplomatic-interpreter",
        problem_definition=(
            "Community mediation: state is a 0-4 polarization bucket; actions 0, 1, 2 "
            "are mediation choices; the contract scores acceptable compromise and lower "
            "polarization on a 0-10 scale and advances state by (state + action + 1) "
            "mod 5; the episode ends after 8 accepted actions."
        ),
    ),
}


def get_domain(name: str) -> Domain:
    try:
        return DOMAINS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown domain {name!r}; choose from {sorted(DOMAINS)}") from exc
