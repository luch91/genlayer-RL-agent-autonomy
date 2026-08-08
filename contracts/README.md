# Deployed Intelligent Contracts

This folder vendors the four Intelligent Contracts of the suite. Each file is the
exact source deployed on the GenLayer Studio network (`studionet`). The files are
mirrored here so this one repository holds every deployed contract. The canonical
home of each contract, together with its off-chain agent and tests, is the domain
repository listed below.

Each contract stores the environment state and the action space, and each reward is
an LLM peer-review call scored 0 to 10. Validators reach consensus on that score
with `gl.eq_principle.prompt_comparative` at tolerance 1.5. None uses `strict_eq`,
because a subjective score does not come back byte-identical across independent LLM
calls. Scores are stored as integers scaled by 100, because GenVM calldata cannot
encode floats.

| Contract file | Domain | Deployed address (studionet) | Explorer | Canonical source |
|---|---|---|---|---|
| `crisis_negotiator.py` | Crisis Response | `0xE0CBc71F7a3e87523F4A3833d4DdBE8a47595220` | [address](https://explorer-studio.genlayer.com/address/0xE0CBc71F7a3e87523F4A3833d4DdBE8a47595220) | [crisis-negotiator](https://github.com/luch91-org/genlayer-rl-crisis-negotiator) |
| `protocol_immunologist.py` | Treasury Defense | `0x4213C3915a314B7A4ef926895A08638F54aE55dd` | [address](https://explorer-studio.genlayer.com/address/0x4213C3915a314B7A4ef926895A08638F54aE55dd) | [protocol-immunologist](https://github.com/luch91-org/genlayer-rl-protocol-immunologist) |
| `scientific_heretic.py` | Science Ideas | `0xDd169FA2FA5D258f1CCBc8CAe61eA652733435F6` | [address](https://explorer-studio.genlayer.com/address/0xDd169FA2FA5D258f1CCBc8CAe61eA652733435F6) | [scientific-heretic](https://github.com/luch91-org/genlayer-rl-scientific-heretic) |
| `diplomatic_interpreter.py` | Community Mediator | `0xA5cf174b2fDC77058C181435040121711312EE15` | [address](https://explorer-studio.genlayer.com/address/0xA5cf174b2fDC77058C181435040121711312EE15) | [diplomatic-interpreter](https://github.com/luch91-org/genlayer-rl-diplomatic-interpreter) |

## Deploy or run

The off-chain agent, the deploy script, and the tests live in each domain repository.
To deploy a fresh copy or run the trained agent, clone the domain repo and follow its
`docs/tutorial.md`. Studio is a shared sandbox that can be reset. If an address stops
resolving, redeploy with `python -m agent.deploy --chain studionet` and use the new
address.

## Explorer host

Links use `explorer-studio.genlayer.com`, the working GenLayer Studio explorer. The
older `explorer-studionet.genlayerlabs.com` host in some manifests returns 503.
