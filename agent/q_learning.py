"""Small, legible tabular Q-learning implementation."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from agent.env import Environment


class QLearningAgent:
    def __init__(self, actions: tuple[int, ...], alpha: float = 0.2, gamma: float = 0.9,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 min_epsilon: float = 0.05, seed: int | None = 7):
        self.actions = actions
        self.alpha, self.gamma = alpha, gamma
        self.epsilon, self.epsilon_decay, self.min_epsilon = epsilon, epsilon_decay, min_epsilon
        self.q: dict[str, dict[str, float]] = {}
        self.rng = random.Random(seed)

    def _row(self, state: int) -> dict[str, float]:
        return self.q.setdefault(str(state), {str(a): 0.0 for a in self.actions})

    def choose_action(self, state: int) -> int:
        row = self._row(state)
        if self.rng.random() < self.epsilon:
            return self.rng.choice(self.actions)
        best = max(float(row[str(a)]) for a in self.actions)
        return next(a for a in self.actions if float(row[str(a)]) == best)

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool) -> float:
        row = self._row(state)
        old = float(row[str(action)])
        future = 0.0 if done else max(float(v) for v in self._row(next_state).values())
        target = reward + self.gamma * future
        row[str(action)] = old + self.alpha * (target - old)
        return row[str(action)]

    def train(self, env: Environment, episodes: int = 100) -> list[float]:
        rewards: list[float] = []
        for _ in range(episodes):
            state = env.reset()
            total = 0.0
            done = False
            while not done:
                action = self.choose_action(state)
                next_state, reward, done, _ = env.step(action)
                self.update(state, action, reward, next_state, done)
                state = next_state
                total += reward
            rewards.append(total)
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        return rewards

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"q": self.q, "epsilon": self.epsilon}, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        data: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        self.q = data["q"]
        self.epsilon = float(data.get("epsilon", self.min_epsilon))
