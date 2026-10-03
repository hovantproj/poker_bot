from macpoker import Bot
import evcalc

try:
    from social_behaviour import SocialBehaviour
except (ImportError, AttributeError):
    SocialBehaviour = None


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

    def act(self, state):
        if state.to_call == 0:
            return state.check()

        pot_odds = state.to_call / (state.pot + state.to_call)

        equity = 0.0
        try:
            ev_result = evcalc.calc_ev(state.hole, state.board)
            if isinstance(ev_result, (int, float)):
                equity = float(ev_result)
        except Exception:
            equity = 0.0

        if self.social and hasattr(self.social, "get_total_penalty"):
            penalty = self.social.get_total_penalty()
            equity *= (1.0-0.5*penalty)

        if equity > pot_odds + 0.25 and state.can_raise:
            return state.raise_to(state.min_raise_to)

        if equity >= pot_odds:
            return state.call()

        return state.fold()

bot = pokabot()
