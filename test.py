from macpoker import Bot

class testbot(Bot):
    def act(self, state):
        print(f"\n[Hand {state.hand} | {state.street}]")
        print(f"Hole: {state.hole} | Board: {state.board}")
        print(f"Pot: {state.pot} | To Call: {state.to_call} | Stack: {state.my_stack}")
        print(f"Can Raise: {state.can_raise} (Min: {state.min_raise_to}, Max: {state.max_raise_to})")

        if state.to_call == 0:
            has_high_card = False

            for card in state.hole:
                rank = card[0]

                if rank == "A" or rank == "K":
                    has_high_card = True
                    break


            if has_high_card and state.can_raise:
                action = state.raise_to(state.min_raise_to)
                print(f"Raise to {state.min_raise_to}")
                return action


        pot_odds = state.to_call / (state.pot + state.to_call)

        printf("Pot Odds: {pot_odds:.2%}")

        if pot_odds < 0.3:
            action = state.call()
            print(f"Call {state.to_call} chips")
            return action

        action = state.fold()
        print(" FOLD")
        return action


bot = testbot()