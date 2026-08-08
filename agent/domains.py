"""Domain definitions shared by the four runnable agents."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Domain:
    name: str
    contract_method: str = "take_action"
    state_method: str = "get_state"
    reward_method: str = "get_last_reward"
    actions: tuple[int, ...] = (0, 1, 2)
    states: tuple[int, ...] = (0, 1, 2, 3, 4)


DOMAINS = {
    "crisis-negotiator": Domain("crisis-negotiator"),
    "protocol-immunologist": Domain("protocol-immunologist"),
    "scientific-heretic": Domain("scientific-heretic"),
    "diplomatic-interpreter": Domain("diplomatic-interpreter"),
}


def get_domain(name: str) -> Domain:
    try:
        return DOMAINS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown domain {name!r}; choose from {sorted(DOMAINS)}") from exc
