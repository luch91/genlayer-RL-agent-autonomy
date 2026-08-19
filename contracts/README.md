# Deployed Intelligent Contracts

This folder vendors the four Intelligent Contracts of the suite. Each file is the
source deployed on the GenLayer Studio network (`studionet`). The files are mirrored
here so this one repository holds every deployed contract and its off-chain agent.

Each contract stores the environment state and the action space, and each reward is
an LLM peer-review call scored 0 to 10. Validators reach consensus on that score
with `gl.eq_principle.prompt_comparative` at a 20-point tolerance on the 0-100
judge scale. None uses `strict_eq`,
because a subjective score does not come back byte-identical across independent LLM
calls. The contract stores the resulting integer reward on the 0-10 scale, because
the Q-learning interface uses discrete rewards.

| Contract file | Domain | Deployed address (studionet) | Explorer | Canonical source |
|---|---|---|---|---|
| `crisis_negotiator.py` | Crisis Response | `0x6DF8D7adDc796C9AA3Af4f42478C2D819B569381` | [address](https://explorer-studio.genlayer.com/address/0x6DF8D7adDc796C9AA3Af4f42478C2D819B569381) | [source](https://github.com/luch91/genlayer-RL-agent-autonomy) |
| `protocol_immunologist.py` | Treasury Defense | `0x71D85CdF6FB3A268AB4B7Fafbba1F643c145Ef26` | [address](https://explorer-studio.genlayer.com/address/0x71D85CdF6FB3A268AB4B7Fafbba1F643c145Ef26) | [source](https://github.com/luch91/genlayer-RL-agent-autonomy) |
| `scientific_heretic.py` | Science Ideas | `0xB831B9D4FFEC63B71985F87CEd3aCDCAF5965be8` | [address](https://explorer-studio.genlayer.com/address/0xB831B9D4FFEC63B71985F87CEd3aCDCAF5965be8) | [source](https://github.com/luch91/genlayer-RL-agent-autonomy) |
| `diplomatic_interpreter.py` | Community Mediator | `0x7c87A683c2506EF8772aC314DcfEF7B4AF7c092D` | [address](https://explorer-studio.genlayer.com/address/0x7c87A683c2506EF8772aC314DcfEF7B4AF7c092D) | [source](https://github.com/luch91/genlayer-RL-agent-autonomy) |

## Deploy or run

The off-chain agent, the deploy script, and the tests live in each domain repository.
To deploy a fresh copy or run the trained agent, clone the domain repo and follow its
`docs/tutorial.md`. Studio is a shared sandbox that can be reset. If an address stops
resolving, redeploy with `python -m agent.deploy --chain studionet` and use the new
address.

## Explorer host

Links use `explorer-studio.genlayer.com`, the working GenLayer Studio explorer. The
older `explorer-studionet.genlayerlabs.com` host in some manifests returns 503.
