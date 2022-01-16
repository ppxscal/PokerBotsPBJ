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
import pandas as pd

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

        #make sure this df isn't too big!! Loading data all at once might be slow if you did more computations!
        calculated_df = pd.read_csv('hole_strengths.csv') #the values we computed offline, this df is slow to search through though
        holes = calculated_df.Holes #the columns of our spreadsheet
        strengths = calculated_df.Strengths
        self.starting_strengths = dict(zip(holes, strengths)) #convert to a dictionary, O(1) lookup time!
    

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
        if street <3: #preflop 
            raise_amount = int(my_pip + continue_cost + 0.4*(pot_total + continue_cost))
        else: #postflop
            raise_amount = int(my_pip + continue_cost + 0.75*(pot_total + continue_cost))

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
        key = self.hole_list_to_key(my_cards)
        strength = self.starting_strengths[key]

        if continue_cost > 0: 
            _SCARY = 0
            if continue_cost > 6:
                _SCARY = 0.1
            if continue_cost > 15: 
                _SCARY = .2
            if continue_cost > 50: 
                _SCARY = 0.35

            strength = max(0, strength - _SCARY)
            pot_odds = continue_cost/(pot_total + continue_cost)

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
        

    def hole_list_to_key(self, hole):
            '''
            Converts a hole card list into a key that we can use to query our 
            strength dictionary
            hole: list - A list of two card strings in the engine's format (Kd, As, Th, 7d, etc.)
            '''
            card_1 = hole[0] #get all of our relevant info
            card_2 = hole[1]

            rank_1, suit_1 = card_1[0], card_1[1] #card info
            rank_2, suit_2 = card_2[0], card_2[1]

            numeric_1, numeric_2 = self.rank_to_numeric(rank_1), self.rank_to_numeric(rank_2) #make numeric

            suited = suit_1 == suit_2 #off-suit or not
            suit_string = 's' if suited else 'o'

            if numeric_1 >= numeric_2: #keep our hole cards in rank order
                return rank_1 + rank_2 + suit_string
            else:
                return rank_2 + rank_1 + suit_string
    
    def rank_to_numeric(self, rank):
        '''
        Method that converts our given rank as a string
        into an integer ranking
        rank: str - one of 'A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2'
        '''
        if rank.isnumeric(): #2-9, we can just use the int version of this string
            return int(rank)
        elif rank == 'T': #10 is T, so we need to specify it here
            return 10
        elif rank == 'J': #Face cards for the rest of them
            return 11
        elif rank == 'Q':
            return 12
        elif rank == 'K':
            return 13
        else: #Ace (A) is the only one left, give it the highest rank
            return 14

if __name__ == '__main__':
    run_bot(Player(), parse_args())
