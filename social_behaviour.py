# -- // SOCIAL BEHAVIOUR STUFF // --
SOCIAL_THRESH = 10 # How many actions to gather before making decisions based on other bots

ACTIONS = {"fold", "check", "call", "bet", "raise", "all_in"} # Set of all actions
AGGRESSIVE = {"bet", "raise", "all_in"} # Set of aggressive actions

class SocialBehaviour:
    def __init__(self, social_thresh=SOCIAL_THRESH):
        self.my_id = None
        self.social_thresh = social_thresh
        self.logs = defaultdict(Counter) # Will store "bot1": Counter({"fold": 2, "raise": 1}) for example
        self.bots_still_in = set() # All the bots still in the game
        self.current = {} # Will store each bots last action and penalty

    def on_hand_start(self, info):
        self.my_id = info["players"][info["seat"]]
        self.bots_still_in = set(info["players"]) - {self.my_id}
        self.current = {
            bot_id: {"last_action": None, "confidence": 0.0}
            for bot_id in self.bots_still_in
        }