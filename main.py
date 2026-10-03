from macpoker import Bot
from collections import defaultdict, Counter
from math import isfinite

SOCIAL_THRESH = 10 # How many actions to gather before making decisions based on other bots

ACTIONS = {"fold", "check", "call", "bet", "raise", "all_in"} # Set of all actions
AGGRESSIVE = {"bet", "raise", "all_in"} # Set of aggressive actions

class MyBot(Bot):
    def act(self, state):
        if state.to_call == 0:
            return state.check()
        pot_odds = state.to_call / (state.pot + state.to_call)
        if pot_odds < 0.3:
            return state.call()
        return state.fold()


# class SocialBehaviour:
#     def __init__(self, social_thresh=SOCIAL_THRESH):
#         self.my_id = my_id
#         self.social_thresh = social_thresh
#         self.logs = defaultdict(Counter) # Will store "bot1": Counter({"fold": 2, "raise": 1}) for example
#         self.bots_still_in = set() # All the bots still in the game
#         self.my_seat = None
#         self.current = {} # Will store each bots last action and penalty

#     def on_hand_start(self, info):
#         """
#         Plan here is to figure out which seat is our bot so we dont count it when calculating penalty
#         """
#         self.my_seat = info["seat"] # TODO: Find out proper syntax for this figure out whats in info

#     def on_action(self, event):
#         who = event["players"][event["seat"]]
#         # Log

#     def log(self, who, action):
#         if who == self.