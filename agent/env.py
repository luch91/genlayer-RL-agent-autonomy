"""Environment implementations.

Both environments expose the same read -> write -> reward interface.  The mock
is deterministic and is used for tests and local training; GenLayerEnv uses the
official genlayer-py read_contract/write_contract methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from agent.domains import Domain


class Environment(Protocol):
    def reset(self, state: int | None = None) -> int: ...
    def observe(self) -> int: ...
    def step(self, action: int) -> tuple[int, float, bool, dict[str, Any]]: ...


@dataclass
class MockEnvironment:
    domain: Domain
    max_steps: int = 8
    state: int = 0
    steps: int = 0

    def reset(self, state: int | None = None) -> int:
        self.state = 0 if state is None else state
        self.steps = 0
        return self.state

    def observe(self) -> int:
        return self.state

    def step(self, action: int) -> tuple[int, float, bool, dict[str, Any]]:
        if action not in self.domain.actions:
            raise ValueError(f"invalid action {action}")
        # A small state-dependent landscape makes the policy learnable while
        # keeping the mock independent of the LLM contract.
        target = self.state % len(self.domain.actions)
        reward = 10.0 if action == target else 3.0
        self.state = (self.state + action + 1) % len(self.domain.states)
        self.steps += 1
        done = self.steps >= self.max_steps
        return self.state, reward, done, {"source": "mock", "action": action}


class GenLayerEnv:
    """Live adapter: read state, submit action, wait, then read consensus reward."""

    def __init__(self, client: Any, account: Any, address: str, domain: Domain):
        self.client = client
        self.account = account
        self.address = address
        self.domain = domain

    def reset(self, state: int | None = None) -> int:
        # Chain environments cannot be reset implicitly.  The optional state is
        # accepted for interface compatibility; deployment initializes state.
        del state
        return self.observe()

    def observe(self) -> int:
        value = self.client.read_contract(
            address=self.address,
            function_name=self.domain.state_method,
            args=[],
        )
        return int(value)

    def step(self, action: int) -> tuple[int, float, bool, dict[str, Any]]:
        if action not in self.domain.actions:
            raise ValueError(f"invalid action {action}")
        tx_hash = self.client.write_contract(
            account=self.account,
            transaction={},
            address=self.address,
            function_name=self.domain.contract_method,
            args=[action],
            value=0,
        )
        receipt = self.client.wait_for_transaction_receipt(transaction_hash=tx_hash)
        execution = receipt.get("tx_execution_result_name") if isinstance(receipt, dict) else None
        if execution and execution != "FINISHED_WITH_RETURN":
            raise RuntimeError(f"GenLayer transaction failed: {execution}")
        reward = self.client.read_contract(
            address=self.address,
            function_name=self.domain.reward_method,
            args=[],
        )
        next_state = self.observe()
        return next_state, float(reward), False, {
            "source": "genlayer",
            "transaction_hash": tx_hash,
            "receipt": receipt,
        }
