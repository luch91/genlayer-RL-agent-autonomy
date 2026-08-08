"""CLI entry point for mock and live training."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent.domains import get_domain
from agent.env import GenLayerEnv, MockEnvironment
from agent.q_learning import QLearningAgent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="crisis-negotiator")
    parser.add_argument("--env", choices=("mock", "genlayer"), default="mock")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--address")
    parser.add_argument("--q-table", default="q_table.json")
    parser.add_argument("--resume", help="load an existing Q-table before training")
    args = parser.parse_args()
    domain = get_domain(args.domain)
    if args.env == "mock":
        env = MockEnvironment(domain)
    else:
        if not args.address:
            parser.error("--address is required with --env genlayer")
        from genlayer_py import create_account, create_client
        from genlayer_py.chains import studionet
        env = GenLayerEnv(create_client(chain=studionet), create_account(), args.address, domain)
    agent = QLearningAgent(domain.actions)
    if args.resume:
        agent.load(args.resume)
    rewards = agent.train(env, args.episodes)
    agent.save(Path(args.q_table))
    print(f"{domain.name}: episodes={len(rewards)} final_reward={rewards[-1]:.2f} q_table={args.q_table}")


if __name__ == "__main__":
    main()
