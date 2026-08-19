from pathlib import Path


CONTRACTS = {
    "crisis_negotiator.py": "CrisisNegotiator",
    "protocol_immunologist.py": "ProtocolImmunologist",
    "scientific_heretic.py": "ScientificHeretic",
    "diplomatic_interpreter.py": "DiplomaticInterpreter",
}


def test_all_domains_include_contract_and_consensus_reward_path():
    for filename, class_name in CONTRACTS.items():
        source = (Path("contracts") / filename).read_text(encoding="utf-8")
        assert f"class {class_name}(gl.Contract)" in source
        assert "@gl.public.view" in source
        assert "def get_state" in source
        assert "def get_problem_definition" in source
        assert "def get_step_count" in source
        assert "def is_terminal" in source
        assert "def take_action" in source
        assert "action must be 0, 1, or 2" in source
        assert "episode is complete" in source
        assert "gl.nondet.exec_prompt" in source
        assert "gl.eq_principle.prompt_comparative" in source
        assert "self.last_reward" in source


def test_contracts_do_not_use_strict_equality_for_subjective_scores():
    for filename in CONTRACTS:
        source = (Path("contracts") / filename).read_text(encoding="utf-8")
        assert "strict_eq" not in source
