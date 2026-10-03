from macpoker import Bot
from collections import defaultdict, Counter

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
            bot_id: {"last_action": None, "penalty": 0.0} # Gauge their penalty based on their past behaviour
            for bot_id in self.bots_still_in
        }

    def on_action(self, event):
        who = event["players"][event["seat"]]
        action = event["action"] # Current action taken

        if who == self.my_id:
            return

        counts = self.logs[who]
        total = sum(counts.values())

        penalty = 0.0 # How uncharacteristic it is for them to act aggressively

        if total >= self.social_thresh and action in AGGRESSIVE:
            fold_rate = counts["fold"] / total

            aggressive_count = sum(counts[a] for a in AGGRESSIVE) # SUm of aggressive actions taken
            aggression_rate = aggressive_count / total # Noramlisation

            action_weight = { # TODO: Arbitrary rn, refine with testing
                "bet": 0.3,
                "raise": 0.5,
                "all_in": 0.8
            }[action]

            penalty = action_weight * (0.5 * fold_rate + 0.5 * (1 - aggression_rate))

        previous_penalty = self.current[who]["penalty"]
        
        self.current[who]["last_action"] = action
        self.current[who]["penalty"] = max(previous_penalty, penalty)

        counts[action] += 1

        if action == "fold":
            self.bots_still_in.discard(who)
            self.current[who]["penalty"] = 0.0

    def get_total_penalty(self):
        """
        returns total penalty (how confident opponents are)
        """
        
        penalties = [
            self.current[bot_id]["penalty"]
            for bot_id in self.bots_still_in
        ]

        if not penalties:
            return 0.0

        strongest = max(penalties)
        others = sum(penalties) - strongest

        return min(1.0, strongest + 0.25 * others) # Full penalty from strongest and a bit from others