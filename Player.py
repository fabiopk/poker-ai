import random
import names
from Deck import suit_to_repr
from Combos import Combo
from starting_hands import rank_hand
from utils import print_debug

class Player:

    def __init__(self, name = None):
        
        self.id = names.get_first_name() if name == None else name
        self.stack = 0
        self.hand = []
        self.table = []
        self.combo = None
        self.folded = False
        self.has_played = False
        self.on_pot = 0
        self.on_table = 0
        self.is_agent = False
        self.debug = False

    def classify_hand(self):
        c1, c2 = self.hand
        if c1 < c2:
            c2, c1 = self.hand

        is_suited = c1.suit == c2.suit

        return f"{c1.get_number()}{c2.get_number()}{'s' if is_suited else 'o'}"
    
    def set_table(self, table):
        self.table = table

    def set_cards(self, cards):
        self.hand = cards

    def get_combo(self):
        self.combo = Combo(self.hand + self.table)
        return self.combo
        
    def __repr__(self):
        return f"Player: {self.id}({self.stack}) -- Hand:{self.hand}"

    def soft_reset(self):
        self.has_played = False
        self.folded = self.stack <= 0
        self.hand = []
        self.table = []
        self.on_pot = 0
        self.on_table = 0
    
    def call(self, amount):

        to_pot = min(self.stack, amount - self.on_table)
        self.stack -= to_pot
        self.on_pot += to_pot
        self.on_table += to_pot
        return to_pot

    def act(self, gameState):

        print_debug(f'Its {self.id} time to play.', self.debug)
        print_debug(f'Hand = {self.hand} ,On Pot/T+Stack = {self.on_pot}/{self.stack + self.on_table} -> {int(100 * self.on_pot/(self.stack + self.on_pot))}%', self.debug)
        print_debug(f"Table: {gameState['table']} -- Curr Bet: {self.on_table}/{gameState['curr_bet']} -- Pot: {gameState['pot']}", self.debug)

        choice = ''
        possible_options = []

        if gameState['curr_bet'] > self.on_table and self.stack > 0:
            possible_options.append('CALL')
            possible_options.append('FOLD')

        if gameState['curr_bet'] == self.on_table:
            possible_options.append('CHECK')
        
        if gameState['curr_bet'] < self.stack:
            possible_options.append('BET')

        minimumBet = max(gameState['big_blind'], gameState['curr_bet'] * 2)

        return self.make_choice(gameState, possible_options)

    def make_choice(self, gameState, possible_options):

        choice = 'NOT_INITIALIZED'
        simple_commands = {'k' : 'CHECK', 'b' : 'BET', 'f' : 'FOLD', 'c' : 'CALL'}

        while(choice not in possible_options):
            choice = input()
            choice = simple_commands[choice] if choice in simple_commands else choice

        amount = 0

        if choice == 'BET':
            amount = int(input())
            if amount > (self.stack + self.on_table):
                raise(Exception('You cannot bet more than you have.'))

        return {
            'type'  : choice,
            'amount' : amount
        }

class RandomPlayer(Player):

    def make_choice(self, gameState, possible_options):

        choice = random.choice(possible_options)
        if choice == 'BET':
            amount = random.randint(gameState['curr_bet'] + 1, self.stack + self.on_pot)
        elif choice == 'CALL':
            amount = gameState['curr_bet'] - self.on_table
        else:
            amount = 0

        print_debug(str(choice) + '\t' + str(amount), self.debug)
        return {
            'type'  : choice,
            'amount' : amount
        }

class SoftRandomPlayer(Player):

    def make_choice(self, gameState, possible_options):

        my_hand = self.classify_hand()
        percentile = rank_hand(my_hand)

        if random.random() < percentile:
            choice = 'BET' if 'BET' in possible_options else 'CALL'
        else:
            choice = 'FOLD' if 'FOLD' in possible_options else 'CHECK'

        if choice == 'BET':
            amount = random.randint(gameState['curr_bet'] + 1, self.stack + self.on_pot)
        elif choice == 'CALL':
            amount = gameState['curr_bet'] - self.on_table
        else:
            amount = 0

        print_debug(str(choice) + '\t' + str(amount), self.debug)
        return {
            'type'  : choice,
            'amount' : amount
        }

class TightPlayer(Player):

    def make_choice(self, gameState, possible_options):

        my_hand = self.classify_hand()
        percentile = rank_hand(my_hand)

        if percentile > 0.85: 
            choice = 'BET' if 'BET' in possible_options else 'CALL'
        else:
            choice = 'FOLD' if 'FOLD' in possible_options else 'CHECK'

        if choice == 'BET':
            amount = random.randint(gameState['curr_bet'] + 1, self.stack + self.on_pot)
        elif choice == 'CALL':
            amount = gameState['curr_bet'] - self.on_table
        else:
            amount = 0

        print_debug(str(choice) + '\t' + str(amount), self.debug)
        return {
            'type'  : choice,
            'amount' : amount
        }

class AgressivePlayer(Player):

    def make_choice(self, gameState, possible_options):

        my_hand = self.classify_hand()
        percentile = rank_hand(my_hand)

        if percentile > 0.5: 
            choice = 'BET' if 'BET' in possible_options else 'CALL'
        else:
            choice = 'FOLD' if 'FOLD' in possible_options else 'CHECK'

        if choice == 'BET':
            amount = random.randint(gameState['curr_bet'] + 1, self.stack + self.on_pot)
        elif choice == 'CALL':
            amount = gameState['curr_bet'] - self.on_table
        else:
            amount = 0

        print_debug(str(choice) + '\t' + str(amount), self.debug)
        return {
            'type'  : choice,
            'amount' : amount
        }

