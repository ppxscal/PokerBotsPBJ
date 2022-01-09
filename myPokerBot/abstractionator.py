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


# use equity distrubution and earths movers distance to group cards together


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

            return hash(tuple(hand))

        else:

            return hash(frozenset(tuple([hand[0].rank, hand[1].rank])))

        # our hole cards in eval7 friendly format


deck = eval7.Deck()

hand = [eval7.Card("4s"), eval7.Card("4c")]

dnah = [eval7.Card("4c"), eval7.Card("4s")]

abstractor = PreflopAbstraction(hand)
bstractor = PreflopAbstraction(dnah)

print(abstractor.hash)
print(bstractor.hash)
