import pickle
from matplotlib import pyplot as plt
from scipy import stats, optimize, interpolate
import eval7
import abstractionator 
import random
import time



'''
for i in a.values():
    print(i[0])
    plt.plot(i[0])
    plt.show()


avgDis = 0

deck = eval7.Deck()

deck.shuffle()

hand = deck.peek(5)

print(hand)


time0 = time.time()

ed0 = abstractionator.computeEquityDistribution(300, 100, hand[:2], hand[2:])

traverse = 0

for i in a.values():

    avgDis  +=  stats.wasserstein_distance(ed0, i[0])

    traverse += 1

    if traverse == 100:
        break

#print(avgDis / 100)

print(time.time()- time0)


'''
def normalize(dictionary):
    total = sum(dictionary.values())
    for key in dictionary:
        dictionary[key] /= total
    return dictionary

#.5 sec for 100 compaisons

#maybe cython will help TODO

#apparently eval7 is already cythonized

with open('flopLookup.pickle', 'rb') as handle:
    a = pickle.load(handle)

deck = eval7.Deck()

deck.shuffle()

hand = deck.peek(5)

#tuesday - infoset
#wednesday - node
#thursday - trainer
#friday - extra time for overnight runs
#saturday - get a working product

#Infosets differ by actions taken, because its a better version of abstraction
class Infoset:
    def __init__(self, history):
        #history can be a string of moves clfr check call fold raise
        #it could also contain an indication of the starting player
        #remember the object has to be doubly describtive for both players.
        #street is evaluated on this side
        self.history = history
        self.hand = hand

    #sample game encoding - I changed my mind and its in the form of a list
    #p1 is the dealer

    def whoseTurn(self):
        #cannot be called when the game hasnt started yet
        
        if ((len(self.history) - 1 )%2 == 1):
            return 1
        else:
            return 2

    def legalActions(self):
        
        if 'fold' in self.history:

            return ('x')
        
        else:
            
            return ('check', 'fold', 'raise', 'call', 'bet')
    
    #so infoset is how we perform nodelookups. Node extensions are just move, and each
    #object contains info regarding regrets and respective actions .

    # [dealer, p1preflop, p2preflop, p1flop, p2flop, p1turn, p2turn, p1river, p2river]
    

#nvm this we can just equate the history strings!

#Heres an idea - let's do the abstraction like this - lets group them by one of the 
#10 kinds of different hands, and a strength index that describes the strength of a specific
#hand element in a grouping category. That way well have at most 10 * (strength indices) different #
# kind of hands which is a lot better than what we were previously trying to do. 

#for now I guess I can just keep working on the cfr architecutre


#I guess for classes we should keep things as primitive data types for the sake of speed
#Think of it like cythonizing modules, which we defenitely could if we could. 

# [dealer, p1preflop, p2preflop, p1flop, p2flop, p1turn, p2turn, p1river, p2river]
 

class Node:
    def __init__(self, infoset):
        self.infoset = infoset
        self.regrets = {}
        # regrets with keys the moves
        for action in self.infoset.legalActions():
            self.regrets[action]=0
        self.weighted_strategy_sum = self.regrets.copy()
        #todo regrets and strategy
    
    def currentStrategy(self):
        actions = self.infoset.legalActions()
        strategy = {}
        if (sum(self.regrets.values()) == 0):
            for action in actions:
                strategy[action] = 1
        else:
            for action in actions:
                regret = self.regrets[action]
                if regret < 0 :
                    strategy[action] = 0
                
        strategy = normalize(strategy)

        return strategy

    def cumulativeStrategy(self):
        pass
        #dcfr TODO

    def addRegret(self, regrets):
        #regret is a dictionary containing
        #a dict uses 4.12x the memory of a list
        for regret in regrets.keys():
            self.regrets[regret] += regrets[regret]


#history = [dealer, p1flop, p2flop, p1turn, p2turn, p1river, p2river]

#last action by player

'''
Round #1, A (0), B (0)
A posts the blind of 1
B posts the blind of 2
A dealt [3c 2h] 
B dealt [Js Qh]
A calls  
B raises to 4 * 
A calls * 
Flop [3d 6h 5d], A (4), B (4)
A's hand: [3c 2h]
B's hand: [4s 6s]
B bets 6 *
A calls * 
Turn [3d 6h 5d Td], A (10), B (10)
A's hand: [3c 2h]
B's hand: [4s 6s]
B bets 15 * 
A folds * 
A awarded -10
B awarded 10
'''
#issue is the descriptivity of the infoset we can see how we can change this regarding the time the algorithm takes

Infoset1 = Infoset((0, 'call', 'bet', 'raise', 'bet', 'fold', None))

a = time.time()
node1 = Node(Infoset1)
print(node1.currentStrategy())

print(time.time() - a )



