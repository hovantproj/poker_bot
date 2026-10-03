from pprint import pformat
from macpoker import Bot

# RUN THIS: macpoker play test.py house:random --deals 

class Tikitesty(Bot):
    def log(self, hook_name, payload):
        with open("all_in.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- {hook_name} ---\n")
            log_file.write(pformat(payload, sort_dicts=False) + "\n")

    def on_hand_start(self, info):
        self.log("on_hand_start", info)

    def on_action(self, event):
        self.log("on_action", event)

    def act(self, state):
        if state.to_call == 0:
            return state.check()
        return state.call()