"""Optional GenLayer direct-mode contract tests.

These run when the official genlayer-test package is installed under Python
3.12. The normal unit suite remains runnable without a GenLayer VM.
"""

import sys

import pytest

if sys.platform == "win32":
    pytest.skip("genlayer-test direct loader currently cannot close temporary stdin files on Windows", allow_module_level=True)

try:
    import gltest  # noqa: F401
except Exception as exc:  # pragma: no cover - depends on the local SDK install
    pytest.skip(f"GenLayer direct test SDK unavailable: {exc}", allow_module_level=True)


@pytest.mark.parametrize(
    "contract_path",
    [
        "contracts/crisis_negotiator.py",
        "contracts/protocol_immunologist.py",
        "contracts/scientific_heretic.py",
        "contracts/diplomatic_interpreter.py",
    ],
)
def test_contract_reads_state_and_returns_consensus_reward(direct_vm, direct_deploy, contract_path):
    direct_vm.mock_llm(r".*", '{"score": 80}')
    contract = direct_deploy(contract_path)
    assert contract.get_state() == 0
    assert contract.take_action(1) == 8
    assert contract.get_last_reward() == 8
    assert contract.get_state() == 2
