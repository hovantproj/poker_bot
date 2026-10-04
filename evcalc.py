import numpy as np
from macpoker import Bot
from collections import defaultdict
import re
import math

# NOTE: some assumptions are made when doing the probabilities (i.e non-pedantic calculations)

# declaring global dicts and lists (for card management)
card_nums = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13
}

card_ratings = {
    'A': 13,
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

card_ratings_other = {
    'A': 13,
    '2': 1,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 5,
    '7': 6,
    '8': 7,
    '9': 8,
    '10': 9,
    '11': 10,
    '12': 11,
    '13': 12
}

cards = {
    's': [1,2,3,4,5,6,7,8,9,10,11,12,13],
    'h': [1,2,3,4,5,6,7,8,9,10,11,12,13],
    'd': [1,2,3,4,5,6,7,8,9,10,11,12,13],
    'c': [1,2,3,4,5,6,7,8,9,10,11,12,13]
}

hands = {
    'royal flush' : 0,
    'straight flush"' : 1,
    'four of a kind' : 2,
    'full house' : 3,
    'flush' : 4,
    'straight' : 5,
    'three of a kind' : 6,
    'two pair' : 7,
    'one pair' : 8,
    'high card' : 9
}

suites = ['s', 'h', 'd', 'c']

# defining useful functions
nPr = lambda n, r: math.factorial(n)/math.factorial(r)

def natural_sort_key(s):
    # Splits the string by numbers
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def calc_royalflush(current_cards_str, numCards):
    # royal flush: A-K-Q-J-T in the same suit 
    # check for each suite, if there's one close then yeah
    highest_suit = 0
    count = 0
    highest_count = 0

    for suite in suites:
        search = f'([AKQJT]{suite})'
        x = re.findall(search, current_cards_str)
        count = len(x)

        if count > 0:
            if highest_suit == 0:
                highest_suit = suite
                highest_count = count
            elif count == highest_count:
                highest_suit += suite
            elif count > highest_count:
                highest_suit = suite
                highest_count = count

    # number of cards left in pile and number of draws left
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    # if we have the royal flush already
    if highest_suit == 0:
        return 0
    elif highest_count == 5:
        return 1
    else:
        # if the number of cards to be revealed is lower than the amount of cards needed to form a royal flush 
        if drawsLeft < 5 - highest_count:
            return 0
        else:
            # actually calculating it
            pr_royalflush_dry = (1/numCardsLeft)**(5-highest_count) * len(highest_suit) * nPr(drawsLeft,5-highest_count)

            # account for the case where someone else already has it
            pr_royalflush = pr_royalflush_dry * (1 - ((4*len(highest_suit))/52))

            return pr_royalflush

def calc_straightflush(current_cards_num, numCards):

    # straight flush: 5 straight combinations in the same suit (higher wins)

    # sort array
    current_cards_num = sorted(current_cards_num, key=natural_sort_key)

    # look to find longest consecutive line of the same suit
    current_suit = 0
    current_rank = 0
    current_length = 0
    longest = 0
    longest_suit = ''
    reset = False
    weight = 0

    for card in current_cards_num:
        # case for first card in the list
        if current_suit == 0:
            current_suit = card[0]
            current_rank = int(card[1:])
            current_length += 1
        else:
            # check if the suit has changed
            if current_suit != card[0]:
                current_suit = card[0]
                current_rank = int(card[1:])
                current_length = 1
                continue
            
            if int(card[1:]) == current_rank + 1 :
                # consecutive cards detected, increment count
                current_length += 1
            else:
                # not consecutive, reset count
                reset = True
            
            # update current longest 
            if longest < current_length:
                longest_suit = current_suit
                longest = current_length
                weight = current_rank+1
            elif longest == current_length:
                longest_suit += current_suit
                longest = current_length

            if reset:
                current_length = 1

            # update current rank
            current_rank = int(card[1:])

    # calculate probability
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    # if we have the straight flush already
    if longest == 5:
        return 1, weight
    else:
        # if the number of cards to be revealed is lower than the amount of cards needed to form the hand 
        if drawsLeft < 5 - longest:
            return 0, 0
        else:
            # actually calculating it
            pr_straightflush_dry = (1/numCardsLeft)**(5-longest) * len(longest_suit) * nPr(drawsLeft,5-longest)

            # account for the case where someone else already has it
            pr_straightflush = pr_straightflush_dry * (1 - ((4*len(longest_suit))/52))

            # if there's no king/ace on the board, flush is 2x more likely
            factor = 1
            for suit in longest_suit:
                if (suit + '1') not in current_cards_num and (suit + '13') not in current_cards_num:
                    factor += 1

            return pr_straightflush * factor, weight

def calc_fourok(current_cards_str, numCards):
    # four of a kind: 4 of the same number (higher wins)

    highest = 0
    highest_rank = ''

    for rank in card_nums.keys():
        search = f'({rank}[shdc])'
        match = re.findall(search, current_cards_str)

        if len(match) > highest:
            highest = len(match)
            highest_rank = rank
        elif len(match) == highest:
            highest_rank += rank
    
    # finding probability
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    # if we have the four of a kind already
    if highest == 4:
        return 1, highest_rank
    else:
        # if the number of cards to be revealed is lower than the amount of cards needed to form the hand
        if drawsLeft < 4 - highest:
            return 0, 0
        else:
            # actually calculating it
            pr_fourok_dry = (1/numCardsLeft)**(4-highest) * len(highest_rank) * nPr(drawsLeft,4-highest)

            # account for the case where someone else already has it
            pr_fourok = pr_fourok_dry * (1 - ((4*len(highest_rank))/52))

            weight = 0
            if len(highest_rank) == 1:
                weight = highest_rank
            else:
                for rank in highest_rank:
                    if card_nums[rank] > weight:
                        weight = card_nums[rank]

            return pr_fourok, weight

def calc_fullhouse(current_cards_str, numCards):
    # full house: 3 of the same rank and 2 of the same rank (higher wins)
    
    highest = 0
    highest_rank = ''
    second_highest = 0
    second_highest_rank = ''

    for rank in card_nums.keys():
        search = f'({rank}[shdc])'
        match = re.findall(search, current_cards_str)

        if len(match) > highest:
            # need to update second highest rank before (current highest will be bumped down)
            second_highest = highest
            second_highest_rank = highest_rank

            # now update the highest
            highest = len(match)
            highest_rank = rank
            continue
        elif len(match) == highest and len(match) > second_highest and second_highest != '':
            highest_rank += rank
            continue
        elif second_highest == '':
            second_highest = 0

        if len(match) > second_highest:
            second_highest = len(match)
            second_highest_rank = rank
        elif len(match) == second_highest:
            second_highest_rank += rank

    # finding probability
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)
    
    # case 1: highest reaches 3, second reaches 2
    if highest >= 3:
        pr_highest3 = 1
    else:
        pr_highest3 = (1/numCardsLeft)**(3 - highest) * len(highest_rank) * nPr(drawsLeft, 3-highest)

    pr_second2 = (1/numCardsLeft)**(2 - second_highest) * len(second_highest_rank) * nPr(drawsLeft, 2-second_highest)
    pr_1 = pr_highest3*pr_second2
    
    # case 2: highest reaches (or stays) 2, second reaches 3
    if highest >= 2:
        pr_highest2 = 1
    else:
        pr_highest2 = (1/(numCardsLeft))**(2 - highest) * len(highest_rank) * nPr(drawsLeft, 2-highest)

    pr_second3 = (1/(numCardsLeft))**(3 - second_highest) * len(second_highest_rank) * nPr(drawsLeft, 3-second_highest)
    pr_2 = pr_highest2*pr_second3

    if len(highest_rank) == 2:
        ranks = highest_rank
    elif second_highest == 0:
        ranks = highest_rank
    else:
        ranks = highest_rank + second_highest_rank[0]

    return pr_1+pr_2, ranks

def calc_flush(current_cards_num, numCards):
    # flush: 5 of the same house (higher wins)

    current_cards_num = sorted(current_cards_num, key=natural_sort_key)
    current_cards_num = ' '.join(current_cards_num)
    current_largest = 0
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)
    strength_final = 0

    pr_flush = 0
    
    for suite in suites:
        search = f'({suite}[0-9]+)'
        match = re.findall(search, current_cards_num)

        if len(match) == 5:
            strength = 0
            for card in match:
                number = int(card[1:])

                if number == 1:
                    strength = 13
                else:
                    strength = (number - 1)

                if strength > strength_final:
                    strength_final = strength

            return 1, strength_final
        elif len(match) > current_largest:
            current_largest = len(match)

            # figure out strength of current hand
            strength = 0
            for card in match:
                number = int(card[1:])

                if number == 1:
                    strength += 13
                else:
                    strength += (number - 1)

            # figure out probability
            if drawsLeft < 5-len(match):
                # not enough draws to get a flush
                pass
            else:
                pr_flush = ((13-len(match))/numCardsLeft)**(5 - len(match)) * nPr(drawsLeft, 5-len(match))

    pr_flush *= (1 - ((4*(13-len(match)))/52))

    return pr_flush, strength

def calc_straight(current_cards_num, numCards):
    # straight: 5 consecutive cards (any suit) (higher wins)
    current_cards_num = sorted(current_cards_num, key=natural_sort_key)

    number_list = []

    for card in current_cards_num:
        number_list.append(int(card[1:]))

    number_list = np.array(number_list)

    number_list = np.unique(number_list)

    consequtive = 1
    highest_consequtive = 0
    rank = 0
    value = None
    
    for i in number_list:
        if value == None:
            value = i
        else:
            if i == value + 1:
                consequtive += 1
                value = i
            else:
                consequtive = 1

        if highest_consequtive <= consequtive:
            highest_consequtive = consequtive
            rank = i

    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    if 1 not in current_cards_num and 13 not in current_cards_num:
        pr_straight = (2*4/numCardsLeft)**(5 - highest_consequtive) * nPr(drawsLeft, 5-highest_consequtive)
    else:
        pr_straight = (4/numCardsLeft)**(5 - highest_consequtive) * nPr(drawsLeft, 5-highest_consequtive)

    # adjust in case someone was dealt the cards needed
    pr_straight *= (1 - ((4*2/52)))

    return pr_straight, rank

def calc_threeok(current_cards_str, numCards):
    # three of a kind: 3 of the same number (higher wins)
    
    highest = 0
    highest_rank = ''

    for rank in card_nums.keys():
        search = f'({rank}[shdc])'
        match = re.findall(search, current_cards_str)

        if len(match) > highest:
            highest = len(match)
            highest_rank = rank
        elif len(match) == highest:
            highest_rank += rank
    
    # finding probability
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    # if we have the three of a kind already
    if highest >= 3:
        return 1, highest_rank
    else:
        # if the number of cards to be revealed is lower than the amount of cards needed to form the hand
        if drawsLeft < 3 - highest:
            return 0, 0
        else:
            # actually calculating it
            pr_threeok_dry = (1/numCardsLeft)**(3-highest) * len(highest_rank) * nPr(drawsLeft,3-highest)

            # account for the case where someone else already has it
            pr_threeok = pr_threeok_dry * (1 - ((4*len(highest_rank))/52))

            weight = 0
            if len(highest_rank) == 1:
                weight = highest_rank
            else:
                for rank in highest_rank:
                    if card_nums[rank] == '1':
                        weight = 13
                        break
                    elif card_nums[rank] > weight:
                        weight = card_nums[rank]

            return pr_threeok, weight

def calc_twopair(current_cards_str, numCards):
    # two pair: 2 of the same number x2 (higher wins)
    highest = 0
    highest_rank = ''

    for rank in card_nums.keys():
        search = f'({rank}[shdc])'
        match = re.findall(search, current_cards_str)

        if len(match) > highest:
            highest = len(match)
            highest_rank = rank
        elif len(match) == highest:
            highest_rank += rank
    
    # finding probability
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    if (len(highest_rank) == 2 and highest == 2):
        return 1, highest_rank
    else:
        # actually calculating it
        pr_twopair_dry = (1/numCardsLeft)

        # account for the case where someone else already has it
        pr_twopair = pr_twopair_dry * (1 - ((4*len(highest_rank))/52))

        # need this to happen for 2 different pairs
        pr_twopair = pr_twopair**2

    return pr_twopair, highest_rank

def calc_onepair(current_cards_str, numCards):
    # two pair: 2 of the same number x2 (higher wins)
    strongest_rank = 0
    highest = 0
    highest_rank = ''

    for rank in card_nums.keys():
        search = f'({rank}[shdc])'
        match = re.findall(search, current_cards_str)

        for card in match:
            if card_ratings[card[0]] > strongest_rank:
                strongest_rank = card_ratings[card[0]]

        if len(match) > highest:
            highest = len(match)
            highest_rank = rank
        elif len(match) == highest:
            highest_rank += rank
    
    # finding probability
    numCardsLeft = 52 - numCards - 4*2
    drawsLeft = 5 - (numCards - 2)

    if highest >= 2: # Highest >= 2 as in there are 2 matches
        return 1, strongest_rank
    else:
        # actually calculating it
        pr_onepair_dry = (1/numCardsLeft)*5*drawsLeft

        # account for the case where someone else already has it
        pr_onepair = pr_onepair_dry * (1 - (4/52))

    return pr_onepair, strongest_rank

def calc_highcard(current_cards_str, numCards):
    strongest_rank = 0

    for rank in card_nums.keys():
        search = f'({rank}[shdc])'
        match = re.findall(search, current_cards_str)

        for card in match:
            if card_ratings[card[0]] > strongest_rank:
                strongest_rank = card_ratings[card[0]]
                
    return strongest_rank

def calc_ev(hand: list[str], board: list[str], known_hands=None):
    """
    Inputs:
    hand: current hand
    board: current board
    known_hands: any known cards that are in other player's hands (might not be applicable)

    Outputs:
    EV of each hand?
    """

    # {number}{suit}
    # A,2,3,4,5,6,7,8,9,T,J,Q,K
    # s,h,d,c

    # create array of currently known cards
    current_cards = hand + board
    current_cards = np.array(current_cards)
    length = len(current_cards)

    # make 2 different arrays, one that is easier to figure for flushes, the other for the rest
    current_cards_str = ' '.join(current_cards)
    current_cards_num = []
    for card in current_cards:
        current_cards_num.append(card[1] + str(card_nums[card[0]]))

    royalflush_pr = calc_royalflush(current_cards_str, length)

    straightflush_pr, highest_sf = calc_straightflush(current_cards_num, length)

    fourok_pr, highest_four = calc_fourok(current_cards_str, length)

    fullhouse_pr, ranks_fh = calc_fullhouse(current_cards_str, length)

    flush_pr, strength_flush = calc_flush(current_cards_num, length)

    straight_pr, highest_straight = calc_straight(current_cards_num, length)

    threeok_pr, highest_three = calc_threeok(current_cards_str, length)

    twopair_pr, highest_tp = calc_twopair(current_cards_str, length)

    onepair_pr, highest_op = calc_onepair(current_cards_str, length)

    # 'strength' is quantified as the highest rank in the hand if it's made
    probabilities = np.array([royalflush_pr, straightflush_pr, fourok_pr, fullhouse_pr, flush_pr, straight_pr, threeok_pr, twopair_pr, onepair_pr, 1])

    return probabilities

calc_ev(['Kc, Ks'], [])
