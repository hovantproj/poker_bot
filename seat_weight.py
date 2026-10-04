position_layouts = {
    2: {0: "BTN", 1: "BB"},
    3: {0: "BTN", 1: "SB", 2: "BB"},
    4: {0: "BTN", 1: "SB", 2: "BB", 3: "UTG"},
    5: {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "CO"},
    6: {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "MP", 5: "CO"},
    7: {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "MP1", 5: "MP2", 6: "CO"},
    8: {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "UTG1", 5: "MP1", 6: "MP2", 7: "CO"},
    9: {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "UTG1", 5: "UTG2", 6: "MP1", 7: "MP2", 8: "CO"},
}

POSITION_WEIGHTS = {
    "BTN": 1.10,
    "CO":  1.05,
    "MP":  1.00,
    "MP1": 1.00,
    "MP2": 1.01,
    "UTG": 0.93,
    "UTG1": 0.94,
    "UTG2": 0.95,
    "BB":  0.94,
    "SB":  0.93,
}

def seat_weight(state):
    num_seats = state.num_players
    button = state.button
    my_seat = state.seat
    folded = state.folded
    is_preflop = (state.street == "preflop")

    active_seats_from_btn = [
        (button + i) % num_seats
        for i in range(num_seats)
        if not folded[(button + i) % num_seats]
    ]

    active_count = len(active_seats_from_btn)

    if active_count <= 1 or my_seat not in active_seats_from_btn:
        return 1

    if active_count == 2:
        is_btn = (my_seat == active_seats_from_btn[0])

        if is_preflop:
            return 1.05 if is_btn else 1.10
        else:
            return 1.15 if is_btn else 0.85


    active_idx = active_seats_from_btn.index(my_seat)

    layout = position_layouts.get(active_count, position_layouts[6])
    mapped_pos = layout.get(active_idx, "MP")
    weight = POSITION_WEIGHTS.get(mapped_pos, 1.0)

    sb_nominal_seat = (button + 1) % num_seats
    bb_nominal_seat = (button + 2) % num_seats

    if is_preflop:
        if my_seat == bb_nominal_seat:
            weight += 0.04
        elif my_seat == sb_nominal_seat:
            weight += 0.02

    else:
        if my_seat in (sb_nominal_seat, bb_nominal_seat):
            weight -= 0.03
    
    weight = max(0.90, min(1.10, weight))
    return round(weight, 3)