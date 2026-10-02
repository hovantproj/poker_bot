from macpoker import Bot
from collections import defaultdict

class MyBot(Bot):
    def __init__(self):
        self.raises = defaultdict(int) # List of all playerids at table

    def on_action(self, event):
        # Detects who is currently playing
        who = event["players"][event["seat"]]

        # Logs their actions
        elif event["action"] == "check":
            self.checks[who] += 1
        elif event["action"] == "raise":
            self.raises[who] += 1
        elif event["action"] == "fold":
            self.folds[who] += 1
        elif event["action"] == "all_in":
            self.all_in[who] += 1

    def act(self, state):
        if state.to_call == 0:
            return state.check()
        pot_odds = state.to_call / (state.pot + state.to_call)
        if pot_odds < 0.3:
            return state.call()
        return state.fold()