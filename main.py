from macpoker import Bot
import evcalc

from social_behaviour import SocialBehaviour

class pokabot(Bot):
    def __init__(self):
        super().__init__()
        self.social = SocialBehaviour() if SocialBehaviour else None

    def on_hand_start(self, info):
        if self.social and hasattr(self.social, "on_hand_start"):
            self.social.on_hand_start(info)

    def on_action(self, event):
        if self.social and hasattr(self.social, "on_action"):
            self.social.on_action(event)

    def get_hand_strength(self, hole, board):
        """
        Convert evcalc 10 element list into a score value from 0.0 to 1.0, be sure to refer to evcalc for the brains behind it
        """

        try:
            result = evcalc.calc_ev(hole, board)

            if result is None:
                return 0.0

        except Exception: # Just in case any bugs in evcalc
            return 0.0

        # Sums up each probability
        category_score = float(sum(result))

        #  Normalisation
        strength = (10.0 - category_score) / 9.0

        # Keep result between 0 and 1
        return max(0.0, min(1.0, strength))

    def act(self, state):
        # Check at every opportunity (coz we passive)
        if state.to_call == 0:
            return state.check()

        # Compare cost and pot odds
        pot_odds = state.to_call / (state.pot + state.to_call)

        hand_strength = self.get_hand_strength(
            state.hole,
            state.board
        )

        # Adjust according to opponent confidence
        if self.social and hasattr(self.social, "get_table_confidence"):
            table_confidence = self.social.get_table_confidence()

            # More confident opponents means bad so big penalty
            hand_strength *= (1.0 - 0.30 * table_confidence)

        # Very strong advantage, we raise
        if hand_strength > pot_odds + 0.25 and state.can_raise:
            return state.raise_to(state.min_raise_to)

        # Call
        if hand_strength >= pot_odds:
            return state.call()

        # Otherwise fold
        return state.fold()

bot = pokabot()
