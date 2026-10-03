from macpoker import Bot
from collections import defaultdict, Counter

class MyBot(Bot):
    def act(self, state):
        if state.to_call == 0:
            return state.check()
        pot_odds = state.to_call / (state.pot + state.to_call)
        if pot_odds < 0.3:
            return state.call()
        return state.fold()


