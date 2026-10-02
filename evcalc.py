import numpy as np
from macpoker import Bot
from collections import defaultdict
import re

#TODO: made a simplification in the probability calculations, where I assume the cards are drawn without replacement
# TODO: to fix, we need to expand some of the denominators but it probably will cook the computing so this is good enough I think

# declaring global dicts and lists (for card management)
card_index = {
    'A': 0,
    '2': 1,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 5,
    '7': 6,
    '8': 7,
    '9': 8,
    'T': 9,
    'J': 10,
    'Q': 11,
    'K': 12
}

cards = {
    's': [1,2,3,4,5,6,7,8,9,10,11,12,13],
    'h': [1,2,3,4,5,6,7,8,9,10,11,12,13],
    'd': [1,2,3,4,5,6,7,8,9,10,11,12,13],
    'c': [1,2,3,4,5,6,7,8,9,10,11,12,13]
}

suites = ['s', 'h', 'd', 'c']

def calc_royalflush(current_cards_str, numCards):
    # royal flush: A-K-Q-J-T in the same suit 
    # check for each suite, if there's one close then yeah
    highest_suit = None
    count = 0
    highest_count = 0

    for suite in suites:
        search = f'([AKQJT]{suite})'
        x = re.findall(search, current_cards_str)
        count = len(x)

        if count > 0:
            if highest_suit == None:
                highest_suit = suite
                highest_count = count
            elif count == highest_count:
                highest_suit += suite
            elif count > highest_count:
                highest_suit = suite
                highest_count = count

    # number of cards left in pile
    numCardsLeft = 52 - numCards - 4*2

    # if we have the royal flush already
    if highest_count == 5:
        return 1
    else:
        # find probability of royal flush 
        pr_royalflush_dry = (1/numCardsLeft)**(5-highest_count) * len(highest_suit)

        # account for the case where someone else already has it
        pr_royalflush = pr_royalflush_dry * (1 - ((4*len(highest_suit))/52))

        return pr_royalflush

def calc_ev(hand: list[str], board: list[str], known_hands=None):
    """
    Inputs:
    hand: current hand
    board: current board
    known_hands: any known cards that are in other player's hands

    Outputs:
    EV of each hand?
    """

    # {number}{suit}
    # A,2,3,4,5,6,7,8,9,T,J,Q,K
    # s,h,d,c

    # create array of currently known cards
    current_cards = hand + board

    test = ['As', 'Kd', 'Qd', 'Jd', 'Td']
    current_cards_str = ' '.join(test)
    
    royalflush_pr = calc_royalflush(current_cards_str, len(test))

    #TODO: add the pr calculations into their separate functions
    # straight flush: 5 straight combinations in the same suit (higher wins)
    # four of a kind: 4 of the same number (higher wins)
    # full house: 3 of the same number and 2 (higher wins)
    # flush: 5 of the same house (higher wins)
    # straight: 5 consecutive cards (any suit) (higher wins)
    # three of a kind: 3 of the same number (higher wins)
    # two pair: 2 of the same number x2 (higher wins)
    # one pair: 2 of the same number x1 (higher wins)
    # high card: highest card in hand

calc_ev(['a'], ['aaaa'])