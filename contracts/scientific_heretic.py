# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class ScientificHeretic(gl.Contract):
    state: u8
    last_reward: u8
    step_count: u32

    def __init__(self):
        self.state = 0
        self.last_reward = 0
        self.step_count = 0

    @gl.public.view
    def get_state(self) -> int:
        return self.state

    @gl.public.view
    def get_last_reward(self) -> int:
        return self.last_reward

    @gl.public.write
    def take_action(self, action: int) -> int:
        old_state = self.state
        prompt = f"""Score this scientific-research action from 0 to 100.
Research state bucket: {old_state}. Action: {action}.
Reward hypotheses that are novel, plausible, and falsifiable; reward testing a strong idea.
Return JSON only: {{\"score\": integer}}."""

        def score():
            answer = gl.nondet.exec_prompt(prompt, response_format="json")
            return int(answer["score"])

        score = gl.eq_principle.prompt_comparative(score, "Scores may differ by at most 20 points")
        reward = max(0, min(10, int(score) // 10))
        self.state = (old_state + action + 1) % 5
        self.last_reward = reward
        self.step_count += 1
        return reward
