import random
import names

class Player:

    def __init__(self, stack):
        
        self.id = names.get_first_name()
        self.stack = stack
        self.hand = []
        self.folded = False
        self.has_played = False
        self.on_pot = 0
        self.on_table = 0
    
    def set_cards(self, cards):
        self.hand = cards

    def __repr__(self):
        return f"Player: {self.id}({self.stack}) -- Hand:{self.hand}"

    def soft_reset(self):
        self.has_played = False
        self.folded = self.stack <= 0
        self.hand = []
        self.on_pot = 0
        self.on_table = 0
    
    def call(self, amount):

        to_pot = min(self.stack, amount - self.on_table)
        self.stack -= to_pot
        self.on_pot += to_pot
        self.on_table += to_pot
        return to_pot

    def act(self, gameState):

        print('')
        print(f'Its {self.id} time to play.')
        print(f'Hand = {self.hand} ,On Pot/T+Stack = {self.on_pot}/{self.stack + self.on_table} -> {int(100 * self.on_pot/(self.stack + self.on_pot))}%')
        print(f"Table: {gameState['table']} -- Curr Bet: {self.on_table}/{gameState['curr_bet']} -- Pot: {gameState['pot']}")

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

        print(choice, amount)
        return {
            'type'  : choice,
            'amount' : amount
        }

