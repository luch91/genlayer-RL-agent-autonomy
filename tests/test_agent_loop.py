from agent.domains import get_domain
from agent.env import GenLayerEnv, MockEnvironment
from agent.q_learning import QLearningAgent


def test_q_update_consumes_reward_and_changes_table():
    agent = QLearningAgent((0, 1, 2), alpha=0.5, gamma=0.0, epsilon=0.0)
    assert agent.update(0, 1, 8.0, 1, True) == 4.0
    assert agent.q["0"]["1"] == 4.0


def test_q_table_can_be_saved_and_resumed(tmp_path):
    path = tmp_path / "q_table.json"
    agent = QLearningAgent((0, 1, 2), epsilon=0.0)
    agent.update(0, 2, 7.0, 1, True)
    agent.save(path)
    resumed = QLearningAgent((0, 1, 2))
    resumed.load(path)
    assert resumed.q == agent.q
    assert resumed.choose_action(0) == 2


def test_mock_training_runs_end_to_end():
    env = MockEnvironment(get_domain("crisis-negotiator"), max_steps=3)
    agent = QLearningAgent(env.domain.actions, seed=1)
    rewards = agent.train(env, episodes=12)
    assert len(rewards) == 12
    assert agent.q
    assert max(rewards) >= 9.0


class FakeClient:
    def __init__(self):
        self.calls = []
        self.state = 0
        self.reward = 0

    def read_contract(self, **kwargs):
        self.calls.append(("read", kwargs))
        method = kwargs["function_name"]
        return self.state if method == "get_state" else self.reward

    def write_contract(self, **kwargs):
        self.calls.append(("write", kwargs))
        self.state = (self.state + kwargs["args"][0] + 1) % 5
        self.reward = 9
        return "0xtest"

    def wait_for_transaction_receipt(self, **kwargs):
        self.calls.append(("wait", kwargs))
        return {"tx_execution_result_name": "FINISHED_WITH_RETURN"}


def test_genlayer_adapter_reads_writes_and_consumes_reward():
    client = FakeClient()
    env = GenLayerEnv(client, account="alice", address="0xabc", domain=get_domain("crisis-negotiator"))
    assert env.reset() == 0
    state, reward, done, info = env.step(2)
    assert state == 3
    assert reward == 9.0
    assert done is False
    assert info["transaction_hash"] == "0xtest"
    assert [call[0] for call in client.calls] == ["read", "write", "wait", "read", "read"]
    write = client.calls[1][1]
    assert write["function_name"] == "take_action"
    assert write["args"] == [2]


def test_all_domains_have_an_executable_mock_path():
    for name in ("crisis-negotiator", "protocol-immunologist", "scientific-heretic", "diplomatic-interpreter"):
        domain = get_domain(name)
        agent = QLearningAgent(domain.actions, seed=2)
        rewards = agent.train(MockEnvironment(domain, max_steps=2), episodes=2)
        assert len(rewards) == 2
