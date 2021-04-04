from Deck import Deck
from Player import Player, RandomPlayer
import random

class PokerGame:

    def __init__(self, num_players, initial_stack = 100, small_blind = 2):
        
        # Set Variables
        self.state = 'ZERO'
        self.all_players = [RandomPlayer(initial_stack) for p in range(num_players - 1)]
        self.all_players.append(Player(initial_stack))
        self.players = self.players_in_hand()
        self.dealer = 0
        self.pot = 0
        self.small_blind = 2
        self.big_blind = self.small_blind * 2
        self.highest_bet = self.big_blind
        self.deck = None
        self.table = []
        self._set_state('START')
    
    def _set_state(self, state):
        self.state = state
        print('State -> ', state)

    def play(self):

        while(len(self.players) > 1):
            self._play_hand()
            self.table = []
            self.dealer = (self.dealer + 1) % len(self.players)

            for player in self.players:
                player.soft_reset()
                print(player)

            self.players = self.players_in_hand()

        print('\nEnd of game! ~~  ')
        for p in self.all_players:
            print(p)
    
    def players_in_hand(self):
        return list(filter(lambda p: p.stack or p.on_pot, self.all_players))

    def _play_hand(self):

        # Init game
        self.deck = Deck()
        self.deck.shuffle()

        # BLINDS
        SMALL_BLIND = (self.dealer + 1) % len(self.players)
        BIG_BLIND = (self.dealer + 2) % len(self.players)
        UTG = (self.dealer + 3) % len(self.players)

        self.pot = 0
        self.pot += self.players[BIG_BLIND].call(self.big_blind)
        self.pot += self.players[SMALL_BLIND].call(self.small_blind)
        self.highest_bet = max([p.on_table for p in self.players])

        self._set_state('PREFLOP')

        # PRE FLOP BET
        self._deal_cards()
        keepGoing = self.betting_round(idx=UTG)

        #FLOP
        if keepGoing:
            self._set_state('FLOP')
            self._deal_flop()
            keepGoing = self.betting_round(idx=SMALL_BLIND)

        #TURN
        if keepGoing:
            self._set_state('TURN')
            self._deal_turn()
            keepGoing = self.betting_round(idx=SMALL_BLIND)

        #RIVER
        if keepGoing:
            self._set_state('RIVER')
            self._deal_river()
            self.betting_round(idx=SMALL_BLIND)

        self._select_winner()


    def _get_game_state(self):

        return {
            'table' : self.table,
            'pot' : self.pot,
            'curr_bet' : self.highest_bet,
            'big_blind' : self.big_blind,
            'stacks' : map(lambda p: p.stack, self.players)
        }

    def betting_round(self, idx=0):
          
        everyoneHasPlayed = False
        betStillToResolve = True
        moreThanOnePlayerLeft = True

        while(moreThanOnePlayerLeft and (not everyoneHasPlayed or betStillToResolve)):

            player = self.players[idx]

            if not player.folded and player.stack > 0 and (sum([p.stack for p in self.players if p.id != player.id]) > 0 or player.on_table < self.highest_bet):

                action = player.act(self._get_game_state())
                
                if action['type'] == 'CHECK':
                    if player.on_table < self.highest_bet:
                        raise('Player cannot check here!')
                    pass

                elif action['type'] == 'CALL':
                    self.pot += player.call(self.highest_bet)

                elif action['type'] == 'FOLD':
                    player.folded = True
                
                elif action['type'] == 'BET':
                    self.pot += player.call(action['amount'])
                    self.highest_bet = player.on_table

                player.has_played = True
            
            else:

                player.has_played = True

            idx += 1
            idx = idx % len(self.players)
            everyoneHasPlayed = all([p.folded or p.has_played or p.stack == 0 for p in self.players])
            playersNotFolderNotAllIn = list(filter(lambda p: (not p.folded and p.stack > 0), self.players))
            betStillToResolve = len(playersNotFolderNotAllIn) and self.highest_bet > min([ p.on_table for p in playersNotFolderNotAllIn])
            moreThanOnePlayerLeft = len([p for p in self.players if not p.folded]) > 1
        
        self.highest_bet = 0

        for player in self.players:
            player.on_table = 0
            if not player.folded:
                player.has_played = False

        return moreThanOnePlayerLeft

    def _select_winner(self):

        winner= random.choice([p for p in self.players if not p.folded])
        print(f'(random) Winner was {winner.id}!')
        amount_from_each_player = winner.on_pot

        for player in self.players:
            if player.on_pot <= amount_from_each_player:
                winner.stack += player.on_pot
                player.on_pot = 0
            else:
                winner.stack += amount_from_each_player
                player.on_pot -= amount_from_each_player
                player.stack += player.on_pot
                player.on_pot = 0
                


    def _deal_cards(self):

        for player in self.players:
            if player.stack:
                player.set_cards(self.deck.draw(2))
            else:
                player.folded = True
    

    def _deal_flop(self):
        self.table = self.deck.draw(3)

    def _deal_turn(self):
        self.table.append(self.deck.drawOne())

    def _deal_river(self):
        self.table.append(self.deck.drawOne())



if __name__ == '__main__':

    pg = PokerGame(3)
    pg.play()