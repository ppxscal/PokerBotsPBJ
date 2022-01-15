import pickle
from matplotlib import pyplot as plt
from scipy import stats, optimize, interpolate
import eval7
import abstractionator 
import random

with open('flopLookup.pickle', 'rb') as handle:
    a = pickle.load(handle)

'''
for i in a.values():
    print(i[0])
    plt.plot(i[0])
    plt.show()
'''


for i in range(100):

    deck = eval7.Deck()

    deck.shuffle()

    hand = deck.peek(5)

    print(hand)

    print(hash(frozenset(hand)))

    ed1 = abstractionator.computeEquityDistribution(300, 100, hand[:2], hand[2:])

    ed = abstractionator.computeEquityDistribution(
            300,
            100,
            [eval7.Card("Ks"), eval7.Card("7d")],
            [eval7.Card("8h"), eval7.Card("9c"), eval7.Card("8s")],
        )


    print(stats.wasserstein_distance(ed, ed1, u_weights=None, v_weights=None))



class Infoset:
    def __init__(self, hand, history=[]):
        self.history = history
        #street = find from history
        #playerTurn
        #self.equityDistribution find the closest out of randomly generated for now. 
        #we still need to trim the dataset. 



class Node:
    def __init__(self, infoset):
        self.infoset = infoset
        self.regrets = {}
        for action in self.infoset.legal_actions():
            self.regrets[action]=0
        self.weighted_strategy_sum = self.regrets.copy()