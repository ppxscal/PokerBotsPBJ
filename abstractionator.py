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
import pickle

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
    # adds the community cards to the opponents hand as well

    if comm < 5:
        for i in range(5 - comm):
            community.append(hand[2 + i])

    for _ in range(iters):  # MC the probability of winning
        deck.shuffle()

        # number of cards in community + opponent

        draw = deck.peek(opp + comm + 4)

        # we add 4 cards to implement swap

        # look at the next seven cards in an arbitrary deck

        opphand = draw[:opp]
        communityReveal = draw[opp:opp+comm]
        '''
        Deck objects provide sample, shuffle, deal and peek methods. 
        The deck code is currently implemented in pure python and works well for 
        quick lightweight simulations, but is too slow for full range vs. 
        range equity calculations. Ideally this code will be rewritten in Cython.
        '''        
        if (5<= comm <= 6):
            swap = random.random()
            if ((0 < swap < .1) and comm == 5):
                swapHand = draw[opp+comm:]
                hand[0] = swapHand[0]
                hand[1] = swapHand[1]
                opphand[0] = swapHand[2]
                opphand[1] = swapHand[3]

            elif((0 < swap < .05) and comm == 6):
                swapHand = draw[opp+comm:]
                hand[0] = swapHand[0]
                hand[1] = swapHand[1]
                opphand[0] = swapHand[2]
                opphand[1] = swapHand[3]


        # simulates the reveal of the remaining cards
        # flop 10% chance of each players hole cards switched from one from the deck
        #turn 5% chance

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

    return hand_strength


# use equity distrubution and earths movers distance to group cards together for flopandturn


def computeEquityDistribution(iterations, numHands, preflop, flop=None, turn=None):

    # the inputs are just the arrays of cards in eval7 format for each round

    startTime = time.time()

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

    for _ in range(iterations):

        # I suspect that combinatorically evaluating all possible hands may produce more accurate results - TODO
        # too much computation

        equity = calc_strength(hand, numHands, opp, comm)

        equityDistribution[math.floor(equity * 100) - 1] += 1

    equityDistribution /= iterations

    #print("--- %s seconds ---" % (time.time() - startTime))

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


class riverAbstraction:
    """
    we can compare hands at all states using equity distribution I would argue that seperate classes arent really needed
    all we need to do from here is create a lookup table - where the program given a hand, would find the closest equity dis
    tribution via earth mover's distance. We can assign each unique distribution an index, for which the cfr algorithm will 
    distinguish between hands. Example: at a node, we have a equity distribution index that represents a hands clostest expected outcome. 
    from there we find a node with the same index and action history, for which we will choose the next action of least regret. We can work
    on the details later.

    The lookup table must distinguish between game states. For example if we're at the flop round, we access the lookup tabe
    to find equity distributions for that specific round. We find the closest one, and return the index of that distribution. However, we need to make sure
    that the distribution is detailed enough to be accurate, but not too detailed such that the program spends too much time looking up 
    equity distributions. 

    Ive calculated that it would take 15 years to make the lookup table. It is a largely from calculating all possible hands stemming from the flop round.

    I can try reducing the time the algorithm takes




    pass
    """


"""
deck = eval7.Deck()

hand = [eval7.Card("Ks"), eval7.Card("5d")]

dnah = [eval7.Card("5d"), eval7.Card("Ks")]

abstractor = PreflopAbstraction(hand)
bstractor = PreflopAbstraction(dnah)


print(abstractor.hash)
print(bstractor.hash)
"""

#with these parameters it should take a little more than 24 hours to create the lookup table for all
#possible hands

# It takes about a day sing an abstraction for all possible hands after the flop. Must use a precomputed strategy preflop. 

'''
ed = computeEquityDistribution(
        300,
        100,
        [eval7.Card("Ks"), eval7.Card("7d")],
        [eval7.Card("8h"), eval7.Card("9c"), eval7.Card("8s")],
    )

print(
    ed
)
'''

'''
def makeLookupTable(startingHands, hands, handDepth, hole, flop, turn=False, river=False):

    #rank suit
    #start with after_flop make sure to implement the swtiching today.


    #toStringDeck = [x.__str__() for x in deck]

    # we are trying to make an equity distribution for every possible hand after the flop

    #TODO edit equitydistribution method to include river round possibility

    #For every combination of hand after flop, add the equity distribution for that hand to the lookup table. We can worry about trimming it after we have to code to make
    #the table in the first place

    lookupTable = defaultdict(list)

    t0 = time.time()

    for i in range(0,startingHands):

        #if i == 6:
            #print(hole + flop)
            #print(hash(frozenset(hole + flop)))

        deck = eval7.Deck()
        deck.shuffle()

        hole = deck.deal(2)
        flop = deck.deal(3)

        lookupTable[hash(frozenset(hole + flop))].append(computeEquityDistribution(
        300,
        100,
        hole,
        flop,))

        print("Dataset Construction - Fraction Complete : " + str(i/startingHands) + "th" + "  Time Elapsed: "+ str(time.time() - t0)+"s")


    return lookupTable
'''

#dic = makeLookupTable(200000, 300, 100, True, True)

#with open('flopLookup.pickle', 'wb') as handle:
#    pickle.dump(dic, handle, protocol=pickle.HIGHEST_PROTOCOL)



'''
with open('flopLookup.pickle', 'rb') as handle:
    a = pickle.load(handle)

for i in a.values():
    print(i[0])
    plt.plot(i[0])
    plt.show()


[Card("9c"), Card("Jc"), Card("Ad"), Card("7h"), Card("2c"), Card("Ad"), Card("7h"), Card("2c")]
3678833318650297864



print(hash(frozenset([Card("9c"), Card("Jc"), Card("Ad"), Card("7h"), Card("2c"), Card("Ad"), Card("7h"), Card("2c")])))
'''

# i suspect it would makes greater sense to only apply the earth mover's distance to the 
# turn and river rounds. The flop just creates too much uncertainty and too many conditions to check



