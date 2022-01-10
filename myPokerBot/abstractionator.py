import resource
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from itertools import combinations, product, permutations
import pyximport
import time
import random
import eval7
import abc
import numpy as np
import math


def calc_strength(hand, iters, opp, comm):
    """ 
        Using MC with iterations to evalute hand strength 

        Args: 
        hole - our hole cards 
        iters - number of times we run MC 
        """

    #opp and comm are the number of cards yet to be revealed 

    startTime = time.time()

    deck = eval7.Deck()  # deck of cards
    
    for card in hand:  # removing our hole cards from the deck
        deck.cards.remove(card)

    score = 0
    community = []
    #adds the community cards to the opponents hand as well

    if comm < 5:
        for i in range(5- comm):
            community.append(hand[2 + i])
    

    for _ in range(iters):  # MC the probability of winning
        deck.shuffle()

        # number of cards in community + opponent

        draw = deck.peek(opp + comm)

        # look at the next seven cards in an arbitrary deck

        opphand = draw[:opp]
        communityReveal= draw[comm:]

        #simulates the reveal of the remaining cards

        our_hand = hand + communityReveal
        opp_hand = opphand + community + communityReveal

        our_hand_value = eval7.evaluate(our_hand)
        opp_hand_value = eval7.evaluate(opp_hand)

        if our_hand_value > opp_hand_value:
            score += 2
        elif our_hand_value == opp_hand_value:
            score += 1
        else:
            score += 0

    hand_strength = score / (2 * iters)  # win probability

    print("--- %s seconds ---" % (time.time() - startTime))

    return hand_strength


# use equity distrubution and earths movers distance to group cards together for flopandturn


def computeEquityDistribution(preflop, flop=None, turn=None):

    #the inputs are just the arrays of cards in eval7 format for each round

    deck = eval7.Deck()

    hand = preflop

    if flop is not None:

        hand += flop

    if turn is not None:

        hand += turn

    for card in hand:
        deck.cards.remove(card)

    # for each increment of 1% equity, we add the number of hands in the current state that produces that equity

    equityDistribution = np.zeros(100)

    opp = 2
    comm = 7 - len(hand)
    # of community cards yet to be revealed/oppcards

    # we can go back and change the numbers if we need to

    for _ in range(100):  

       equity = calc_strength(hand, 50, opp, comm)

       equityDistribution[math.floor(equity * 100) - 1] += 1

    for equity in equityDistribution:

        equity /= 100
    
    return equityDistribution 



class PreflopAbstraction:

    # 169 strategically distinct hands. 13 pairs, 13 choose 2 same suit hands, 13 choose 2 different suit hands

    def __init__(self, hole):
        self.hole = hole
        self.hash = self.computeAbstraction()

    def computeAbstraction(self):

        # suits d = 1, h = 2, c = 0, s = 3

        hand = []

        for card in self.hole:
            hand.append(card)

        if hand[0].rank == hand[1].rank:  # pairs

            return hash(frozenset(tuple(hand)))

        if hand[0].suit == hand[1].suit:

            return hash(frozenset(tuple(hand)))

        else:

            return hash(frozenset(tuple([hand[0].rank, hand[1].rank])))

        # our hole cards in eval7 friendly format


class flopTurnAbstraction:
    # base class for flop and turn abstractions for the sake of efficiency

    def __init__(self, street, buckets=5000, equityBins=50):
        pass


"""
deck = eval7.Deck()

hand = [eval7.Card("Ks"), eval7.Card("5d")]

dnah = [eval7.Card("5d"), eval7.Card("Ks")]

abstractor = PreflopAbstraction(hand)
bstractor = PreflopAbstraction(dnah)


print(abstractor.hash)
print(bstractor.hash)
"""

deck = eval7.Deck()

hand = [eval7.Card("Ks"), eval7.Card("Kd"), eval7.Card("Kc"), eval7.Card("Kh"), ]


print(computeEquityDistribution([eval7.Card("Ks"), eval7.Card("Kd")]), )


