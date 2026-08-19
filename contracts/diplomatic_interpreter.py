# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class DiplomaticInterpreter(gl.Contract):
    state: u8
    last_reward: u8
    last_action: u8
    step_count: u32

    def __init__(self):
        self.state = 0
        self.last_reward = 0
        self.last_action = 0
        self.step_count = 0

    @gl.public.view
    def get_problem_definition(self) -> str:
        return ("Community mediation: state is a 0-4 polarization bucket; actions 0, 1, 2 "
                "are mediation choices; the contract scores acceptable compromise and lower "
                "polarization on a 0-10 scale and advances state by (state + action + 1) "
                "mod 5; the episode ends after 8 accepted actions.")

    @gl.public.view
    def get_step_count(self) -> int:
        return self.step_count

    @gl.public.view
    def is_terminal(self) -> bool:
        return self.step_count >= 8

    @gl.public.view
    def get_state(self) -> int:
        return self.state

    @gl.public.view
    def get_last_reward(self) -> int:
        return self.last_reward

    @gl.public.write
    def take_action(self, action: int) -> int:
        if action < 0 or action > 2:
            raise ValueError("action must be 0, 1, or 2")
        if self.step_count >= 8:
            raise ValueError("episode is complete")
        old_state = self.state
        prompt = f"""Score this mediation draft from 0 to 100.
Polarization bucket: {old_state}. Action: {action}.
Reward a compromise that both communities can accept and that lowers polarization.
Return JSON only: {{\"score\": integer}}."""

        def score():
            answer = gl.nondet.exec_prompt(prompt, response_format="json")
            return int(answer["score"])

        score = gl.eq_principle.prompt_comparative(score, "Scores may differ by at most 20 points")
        reward = max(0, min(10, int(score) // 10))
        self.state = (old_state + action + 1) % 5
        self.last_reward = reward
        self.last_action = action
        self.step_count += 1
        return reward
