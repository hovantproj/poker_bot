from collections import Counter, defaultdict

SOCIAL_THRESH = 10  # Needs this many past actions before considering
ACTIONS = {"fold", "check", "call", "raise"}
HISTORY_ADJUSTMENT = 0.15 # How much it reacts to new unusual actions

# Checking is weak, calling moderate and raising strong
BASE_CONFIDENCE = {"check": 0.25, "call": 0.3, "raise": 0.65}
AGGRESSION = {"fold": 0.0, "check": 0.0, "call": 0.5, "raise": 1.0}

class SocialBehaviour:
    def __init__(self, social_thresh=SOCIAL_THRESH):
        if social_thresh < 1:
            raise ValueError("Social thresh needs to be at least 1 monkey")

        self.social_thresh = social_thresh
        self.my_id = None

        # Each key is (player ID, street), e.g. (1, "flop").
        self.history = defaultdict(Counter)

        # Formatted liek {player_id: {"last_action": None, "confidence": 0.5}}
        self.current = {}
        self._starting_chips = {}

    def on_hand_start(self, info):
        players = info["players"]
        self.my_id = players[info["seat"]]
        self._starting_chips = dict(zip(players, info["stacks"])) # Stacks are [200, 200] for example idk why they call it that
        self.current = {
            player: {"last_action": None, "confidence": 0.5}
            for player in players
            if player != self.my_id
        }

    def on_action(self, event):
        if self.my_id is None:
            return
        
        # Gets the playerid from seat
        who = event["players"][event["seat"]]
        if who not in self.current:
            return 

        action = event["action"]
        if action not in ACTIONS:
            return  # Unrecognised action, proly wont happen

        counts = self.history[(who, event["street"])]

        if action == "fold":
            counts[action] += 1
            del self.current[who] # Remove them
            return

        confidence = BASE_CONFIDENCE[action]

        if action in {"call", "raise"}:
            amount = max(0, event["amount"]) # Considers amount
            pot_fraction = min(1.0, amount / max(event["pot"], 1))
            chips_fraction = min(1.0, amount / max(self._starting_chips[who], 1))
            pot_weight = 0.20 if action == "raise" else 0.10
            confidence += pot_weight * pot_fraction + 0.15 * chips_fraction

        total = sum(counts.values())
        if total >= self.social_thresh:
            usual_aggression = sum(AGGRESSION[previous_action] * count for previous_action, count in counts.items()) / total

            # If theyre usually passive but they make aggressive play it adds and if theyre usually aggressive but theyre suddenly passive
            confidence += HISTORY_ADJUSTMENT * (AGGRESSION[action] - usual_aggression)

        confidence = max(0.0, min(1.0, confidence))
        current = self.current[who]

        current["last_action"] = action
        current["confidence"] = confidence
        counts[action] += 1  # Add this action AFTER comparing it with history.

    def get_opponent_confidences(self):
        """
        Can call this from main btw if need be, does exactly what it says
        """
        return {
            player: current["confidence"]
            for player, current in self.current.items()
        }

    def get_table_confidence(self):
        """
        Return the highest active opponent score
        """
        return max(
            (current["confidence"] for current in self.current.values()),
            default=0.0,
        )
