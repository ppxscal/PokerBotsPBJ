
'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import math
import random 
import eval7
import numpy as np
import time

#look into storing opponent moves and try to predict the strength of their hand based off their actions in the past
#think of a fast way to do this
#preplop logic to increase time




class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''

        self.myDelta = 0
        self.prevStrength = 0.5
        self.raisePreFlopVar = 0.4
        self.raisePostFlopVar = 0.7
        self.opp_prev_cards = []
        self.prev_end_round = 5
        self.scaryOffset = 0
        self.pastGames = {}
        self.gameNumber = 0


    def computeEquityDistribution(self, iterations, depth, hole, communityCards):

        # the inputs are just the arrays of cards in eval7 format for each round

        # for each increment of 1% equity, we add the number of hands in the current state that produces that equity

        time0 = time.time()

        equityDistribution = np.zeros(100)

        #only implemented so far for the flop round

        deck = eval7.Deck()
        dummyDeck = deck
        deck.shuffle()
        hand = hole + communityCards
        
        for _ in range(iterations):

            sim = deck.peek(7 - len(hand))
            sim1 = []
            for i in sim:
                sim1.append(i.__str__())

            fullHand = communityCards + sim1

            #print(communityCards + sim1)

            equity = self.calc_strength(hole, depth, communityCards)

            equityDistribution[math.floor(equity * 100) - 1] += 1

            deck = dummyDeck
            deck.shuffle()

        equityDistribution /= iterations

        print(time.time() - time0)

        return equityDistribution
        
    def calc_strength(self, hole, iters, community = []):
        ''' 
        Using MC with iterations to evalute hand strength 

        Args: 
        hole - our hole carsd 
        iters - number of times we run MC 
        community - community cards
        '''

        deck = eval7.Deck() # deck of cards
        hole_cards = [eval7.Card(card) for card in hole] # our hole cards in eval7 friendly format

        if community != []:
            community_cards = [eval7.Card(card) for card in community]
            for card in community_cards: #removing the current community cards from the deck
                deck.cards.remove(card)

        for card in hole_cards: #removing our hole cards from the deck
            #print(deck.cards)
            #print(card)
            deck.cards.remove(card)
        
        #may need to fix this later 
        
        
        score = 0 

        for _ in range(iters): # MC the probability of winning
            deck.shuffle()

            _COMM = 5 - len(community)
            _OPP = 2 

            draw = deck.peek(_COMM + _OPP + 4)  
            my_hole = hole_cards
            opp_hole = draw[:_OPP]
            alt_community = draw[_OPP:_OPP + _COMM]
            swap = draw[-4:]

            randA = random.random()
            randB = random.random()

            if _COMM == 2 and randA <= .1:
                my_hole = swap[:2]
            
            if _COMM == 2 and randB <= .1:
                opp_hole = swap[2:]
            
            if _COMM == 1 and randA <= .05:
                my_hole = swap[:2]
            
            if _COMM == 1 and randA <= .05:
                opp_hole = swap[2:]
                
            
            if community == []:
                our_hand = hole_cards  + alt_community
                opp_hand = opp_hole  + alt_community

            else: 

                our_hand = hole_cards + community_cards + alt_community
                opp_hand = opp_hole + community_cards + alt_community


            our_hand_value = eval7.evaluate(our_hand)
            opp_hand_value = eval7.evaluate(opp_hand)

            if our_hand_value > opp_hand_value:
                score += 2 

            if our_hand_value == opp_hand_value:
                score += 1 


        hand_strength = score/(2*iters) # win probability 

        return hand_strength
    

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''

        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind

        self.round_num = round_num


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''


        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed

        self.myDelta = my_delta
        self.my_previous_cards = my_cards
        self.opp_prev_cards = opp_cards
        self.prev_end_round = street
        self.gameNumber += 1
        # print(my_delta)
        # print('DELTA: ', self.myDelta)

        if my_delta <= 0: # we lost last turn, reduce risk by raising less each time
            # if self.prevStrength > 0.5 and self.opp_prev_cards == []: #if we had a strong hand and opp folded, we raised too much
            # if self.opp_prev_cards == []:
            

            if street < 3:                 
                self.raisePreFlopVar = max([0.4, self.raisePreFlopVar - 0.05])
                # print('update pre down')
            else:
                self.raisePostFlopVar = max([0.4, self.raisePostFlopVar - 0.05])
                # print('update post down')

            # self.scaryOffset = min([0.8, self.scaryOffset + 0.01]) #if we lost, we should play more conservatively

        else: # we won last turn, increase risk by raising more each time

       
            if street < 3:                 
                self.raisePreFlopVar = min([0.8, self.raisePreFlopVar + 0.05])
                # print('update pre up')
            else:
                self.raisePostFlopVar = min([0.8, self.raisePostFlopVar + 0.05])
                # print('update post up')

            # self.scaryOffset =  max([0, self.scaryOffset - 0.01])

        # print("preflopvar, postflopvar, scaryoffset", self.raisePreFlopVar, self.raisePostFlopVar, self.scaryOffset)
        print(self.pastGames)
    

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''

        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        net_upper_raise_bound = round_state.raise_bounds()
        stacks = [my_stack, opp_stack] #keep track of our stacks

        my_action = None

        min_raise, max_raise = round_state.raise_bounds()
        pot_total = my_contribution + opp_contribution

        # raise logic 
        if street <3: #preflop 
            raise_amount = int(my_pip + continue_cost + self.raisePreFlopVar*(pot_total + continue_cost))
        else: #postflop
            raise_amount = int(my_pip + continue_cost + self.raisePostFlopVar*(pot_total + continue_cost))

        # ensure raises are legal
        raise_amount = max([min_raise, raise_amount])
        raise_amount = min([max_raise, raise_amount])

        if (RaiseAction in legal_actions and (raise_amount <= my_stack)):
            temp_action = RaiseAction(raise_amount)
        elif (CallAction in legal_actions and (continue_cost <= my_stack)):
            temp_action = CallAction()
        elif CheckAction in legal_actions:
            temp_action = CheckAction()
        else:
            temp_action = FoldAction() 

        _MONTE_CARLO_ITERS = 100
        
        #running monte carlo simulation when we have community cards vs when we don't 
        if street < 3:
            strength = self.calc_strength(my_cards, _MONTE_CARLO_ITERS)
        else:
            strength = self.calc_strength(my_cards, _MONTE_CARLO_ITERS, board_cards)

        if street == 3:
            #print(my_cards)
            #a = self.computeEquityDistribution(35, 10, my_cards, board_cards)
            #print(a)
            #self.pastGames[self.gameNumber] = a
            pass
        
        self.prevStrength = strength

        if continue_cost > 0: 
            _SCARY = 0
            ratio = 0 


            if street <3: # if opponent raised early, they are probably more confident
                if continue_cost > 1: #continue cost == 1 is blind
                    if continue_cost/pot_total > 0.1:
                        _SCARY = 0.1
                        ratio = 0.08
                    if continue_cost/pot_total > 0.3: 
                        _SCARY = 0.2
                        ratio = 0.12
                    if continue_cost/pot_total > 0.5: 
                        _SCARY = 0.3
                        ratio = 0.16           
            else: #post flop
                if continue_cost/pot_total > 0.1:
                    _SCARY = 0.1
                    ratio = 0.1
                if continue_cost/pot_total > 0.3: 
                    _SCARY = 0.2
                    ratio = 0.15
                if continue_cost/pot_total > 0.5: 
                    _SCARY = 0.35
                    ratio = 0.25

            # if street < 3:
            #     if continue_cost > 1:
            #         if continue_cost > 0.1*pot_total:
            #             _SCARY = 0.1
            #             ratio = 0.08
            #         if continue_cost > 0.3*pot_total:
            #             _SCARY = 0.2
            #             ratio = 0.12
            #         if continue_cost > 0.5*pot_total:
            #             _SCARY = 0.3
            #             ratio = 0.16

            # elif street < 4:
            #     if continue_cost > 0.1*pot_total:
            #         _SCARY = 0.1
            #         ratio = 0.1
            #     if continue_cost > 0.3*pot_total:
            #         _SCARY = 0.2
            #         ratio = 0.15
            #     if continue_cost > 0.5*pot_total:
            #         _SCARY = 0.35
            #         ratio = 0.2

            # else:
            #     if continue_cost > 0.1*pot_total:
            #         _SCARY = 0.1
            #         ratio = 0.12
            #     if continue_cost > 0.3*pot_total:
            #         _SCARY = 0.2
            #         ratio = 0.18
            #     if continue_cost > 0.5*pot_total:
            #         _SCARY = 0.4
            #         ratio = 0.24


            _SCARY += self.scaryOffset      #this var is adjusted in the handle_round_over function


            # might want to incorporate implied pot odds by adding the amount_expected_to_win to the demoninator

            next_bet = (pot_total + continue_cost)*ratio # assuming that the opponent will always bet ratio of the pot

            strength = max(0, strength - _SCARY)
            pot_odds = continue_cost/(pot_total + continue_cost + next_bet)


            if strength >= pot_odds: # nonnegative EV decision
                if strength > 0.5 and random.random() < strength: 
                    my_action = temp_action
                else: 
                    my_action = CallAction()
            
            else: #negative EV
                my_action = FoldAction()
                
        else: # continue cost is 0  
            if random.random() < strength: 
                my_action = temp_action
            else: 
                my_action = CheckAction()
            

        return my_action
        


if __name__ == '__main__':
    run_bot(Player(), parse_args())

