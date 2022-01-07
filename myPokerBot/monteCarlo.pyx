import eval7
import cython
import time


cpdef double calc_strength(hole, int iters):
    """ 
        Using MC with iterations to evalute hand strength 

        Args: 
        hole - our hole cards 
        iters - number of times we run MC 
        """

    cdef double startTime = time.time()

    deck = eval7.Deck()  # deck of cards
    hole_cards = [
        eval7.Card(card) for card in hole
    ]  # our hole cards in eval7 friendly format

    
    for card in hole_cards:  # removing our hole cards from the deck
        deck.cards.remove(card)

    cdef int score = 0

    for _ in range(iters):  # MC the probability of winning
        deck.shuffle()

        _OPP = 2
        _COMM = 5

        # number of cards in community + opponent

        draw = deck.peek(_OPP + _COMM)

        # look at the next seven cards in an arbitrary deck

        opp_hole = draw[:_OPP]
        community = draw[_OPP:]

        # baisically finding random 7 cards and simulating the outcome

        our_hand = hole_cards + community
        opp_hand = opp_hole + community

        our_hand_value = eval7.evaluate(our_hand)
        opp_hand_value = eval7.evaluate(opp_hand)

        if our_hand_value > opp_hand_value:
            score += 2
        elif our_hand_value == opp_hand_value:
            score += 1
        else:
            score += 0

    cdef double hand_strength = score / (2 * iters)  # win probability

    print("--- %s seconds ---" % (time.time() - startTime))

   

    return hand_strength
