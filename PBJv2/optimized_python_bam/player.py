'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random 
import eval7


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

    # def check_pair(self, my_cards):
    #     ranks = {}
        
    #     for card in my_cards:
    #         card_rank  = card[0]
    #         card_suit = card[1]


    #         if card_rank in ranks:
    #             ranks[card_rank].append(card)
    #         else:
    #             ranks[card_rank] = [card]

    #     pairs = [] #keeps track of the pairs that we have 
    #     singles = [] #other 

    #     for rank in ranks:
    #         cards = ranks[rank]

    #         if len(cards) == 1: #single card, can't be in a pair
    #             singles.append(cards[0])
            
    #         elif len(cards) == 2 or len(cards) == 4: #a single pair or two pairs can be made here, add them all
    #             pairs += cards
            
    #         else: #len(cards) == 3  A single pair plus an extra can be made here
    #             pairs.append(cards[0])
    #             pairs.append(cards[1])
    #             singles.append(cards[2])

    #     if len(pairs) > 0: #we found a pair! update our state to say that this is a strong round
    #         self.strong_hole = True
        
    #     # allocation = pairs + singles 
        
    #     return 0 
        
    def calc_strength(self, hole, iters, community = []):
        ''' 
        Using MC with iterations to evalute hand strength 

        Args: 
        hole - our hole cards
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
            deck.cards.remove(card)
        
        #may need to fix this later 
        
        totalDiff = 0 

        for _ in range(iters): # MC the probability of winning
            deck.shuffle()

            _COMM = 5 - len(community)
            _OPP = 2 

            draw = deck.peek(_COMM + _OPP)
            
            opp_hole = draw[:_OPP]
            facedown_community = draw[_OPP:] 
            
            if community == []:
                our_hand = hole_cards  + facedown_community
                opp_hand = opp_hole  + facedown_community
            else: 

                our_hand = hole_cards + community_cards + facedown_community
                opp_hand = opp_hole + community_cards + facedown_community


            our_hand_value = eval7.evaluate(our_hand)
            opp_hand_value = eval7.evaluate(opp_hand)

            diff = (our_hand_value - opp_hand_value)/135000000
            # diff = our_hand_value - opp_hand_value

            # elif diff == 0:
            #     probWin = 1

            # else: #losing hand
            #     probWin = 0

            # print('diff: ', diff)

            # print(diff)
            
            # score += probWin
            totalDiff += diff

            # if our_hand_value >= opp_hand_value:
            #     # print(our_hand_value, opp_hand_value, our_hand_value-opp_hand_value)
            #     # print((our_hand_value - opp_hand_value)/our_hand_value)
            #     score = score + 1 + (our_hand_value - opp_hand_value)/135000000 #based on how much better our hand is
            #     print(1 + (our_hand_value - opp_hand_value)/135000000)

            # if our_hand_value == opp_hand_value:
            #     score += 1            

            # else: 
            #     score += 0 

            # if our_hand_value > opp_hand_value:
            #     score += 2 

            # if our_hand_value == opp_hand_value:
            #     score += 1            

            # else: 
            #     score += 0        

        # hand_strength = score/(2*iters) # win probability


        avgDiff = totalDiff/iters

        # print("avgDiff: ", avgDiff)

        
        if avgDiff <= 0:
            probWin = 0

        else:
            probWin = avgDiff /0.05 #scale accordingly
            if avgDiff > 0.05:
                probWin = 1

        print(avgDiff, probWin)


        # if avgDiff > 0 and avgDiff < 0.1:
        #     print('avgDiff:' , avgDiff)
        # elif avgDiff > 0.1 and avgDiff < 0.3: #45/500
        #     print('----------avgDiff:' , avgDiff)
        # elif avgDiff > 0.3: #only 16/500 chance of happening
        #     print('*******************avgDiff:' , avgDiff)       

        # if avgDiff <= 0:
        #     probWin = 0

        # else: #need to figure out what these thresholds should be: what's considered a good hand?
        #     probWin = 0.5 #stay conservative with "OK" hand
        #     if avgDiff > 0.1: #decent hand
        #         probWin = 0.8
        #     if avgDiff > 0.3: #really good hand, likely will win
        #         probWin = 1

        return probWin
    

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
        if street <3: # pre-flop 
            raise_amount = int(my_pip + continue_cost + 0.4*(pot_total + continue_cost)) # initially 0.4
        else: # post-flop
            raise_amount = int(my_pip + continue_cost + 0.75*(pot_total + continue_cost)) # initially 0.75

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
        if street <3: # pre-flop
            strength = self.calc_strength(my_cards, _MONTE_CARLO_ITERS)
        else: # post-flop
            strength = self.calc_strength(my_cards, _MONTE_CARLO_ITERS, board_cards)

        # print(continue_cost/pot_total)
        # print(my_stack)

        if continue_cost > 0: 
            _SCARY = 0

            # Calculate _SCARY as a factor of pot_total only if continue_cost is large relative to opp's stack
            if continue_cost > 0.02 *opp_stack:

                if continue_cost/pot_total > 0.1:
                    _SCARY = 0.1
                if continue_cost/pot_total > 0.3: 
                    _SCARY = 0.2
                if continue_cost/pot_total > 0.5: 
                    _SCARY = 0.35

            strength = max(0, strength - _SCARY)
            pot_odds = continue_cost/(pot_total + continue_cost)

            # print('0.02*opp_stack', 0.02*opp_stack)
            # print('continue_cost: ', continue_cost)
            # print('continue cost/pot_total: ', continue_cost/pot_total)
            # print('adjustedStrength: ', strength)
            # print('pot_odds: ', pot_odds)

            if strength >= pot_odds: # nonnegative EV decision

                if street <3: # pre-flop
                    strengthThreshold = 0.6 # higher threshold: pre-flop, only raise if have really good hand
                else: # post-flop
                    strengthThreshold = 0.5
    
                if strength > strengthThreshold and random.random() < strength: 
                    my_action = temp_action
                    # print('raise amount: ', raise_amount)
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
