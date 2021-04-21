from Deck import Deck
from Player import Player, RandomPlayer, SoftRandomPlayer, TightPlayer, AgressivePlayer
from Combos import Combo
from utils import print_debug


class PokerEnv:

    def __init__(self, players, stack, small_blind):
        self.state = 'ZERO'
        self.initial_stack = stack
        self.all_players = players
        self.players = self.players_in_hand()
        self.small_blind = small_blind
        self.big_blind = self.small_blind * 2
        self.table = []
        self.dealer = 0
        self.pot = 0
        self.highest_bet = self.big_blind
        self.deck = None
        self.possibleActions = ['CHECK', 'BET', 'CALL', 'FOLD']
        self.reset_env()
        self.debug = False
        if self.debug:
            for p in self.players:
                p.debug = True
        self._set_state('START')

    def _set_state(self, state):
        self.state = state
        print_debug('State -> '+ state, self.debug)

    def reset_env(self):

        for p in self.all_players:
            p.stack = self.initial_stack
            p.soft_reset()

        self.players = self.players_in_hand()


    def isTerminalState(self):
        return len(self.players_in_hand()) == 1

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

        self._resolve_winners()
        
    def betting_round(self, idx=0):
          
        everyoneHasPlayed = False
        betStillToResolve = True
        moreThanOnePlayerLeft = True

        while(moreThanOnePlayerLeft and (not everyoneHasPlayed or betStillToResolve)):

            player = self.players[idx]
            othersCanCall = sum([p.stack for p in self.players if p.id != player.id]) > 0

            if not player.folded and player.stack > 0 and (othersCanCall or player.on_table < self.highest_bet):

                action = player.act(self._get_game_state(player))
                
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

            idx = (idx + 1) % len(self.players)
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

    def _get_game_state(self, player):

        return {
            'table' : self.table,
            'hand' : player.hand,
            'pot' : self.pot,
            'curr_bet' : self.highest_bet,
            'big_blind' : self.big_blind,
            'stacks' : map(lambda p: p.stack, self.players),
            'on_pots' : map(lambda p: p.on_pot, self.players),
            'stacks' : map(lambda p: p.stack, self.players),
            'folded' : map(lambda p: p.folded, self.players)
        }
    def _resolve_winners(self):

        while(self.pot):
            print(f'POT = {self.pot}')
            # Check minimum side bet
            min_side_bet = min([p.on_pot for p in self.players if (not p.folded) and p.on_pot > 0])
            candidates = [p for p in self.players_in_hand() if not p.folded and p.on_pot >= min_side_bet]

            # If only candidate to win, set as only winner 
            if len(candidates) == 1:
                winners = candidates

            else:
                # Showdown
                candidate_hands = [p.get_combo() for p in candidates]
                best_hand = max(candidate_hands)
                winners = [p for p in candidates if p.get_combo() == best_hand]
            

            side_pot = 0

            for p in self.players:
                amount_collected = min(p.on_pot, min_side_bet)
                p.on_pot -= amount_collected
                side_pot += amount_collected

            win_portion = side_pot // len(winners)
            extra_chips = side_pot % len(winners)

            print_debug('side_pot -> ' + str(side_pot), self.debug)
            print_debug('win_portion -> ' + str(win_portion), self.debug)
            print_debug('extra_chips -> ' + str(extra_chips), self.debug)

            print(f'~ ~ Winners ({len(winners)})')
            for w in winners:
                print(w.id, w.on_pot, w.stack, w.get_combo())

            for winner in winners:
                amount_received = win_portion
                if extra_chips > 0:
                    amount_received += 1
                    extra_chips -= 1
                print_debug(str(winner.id) + '\t' + str(amount_received), self.debug)
                winner.stack += amount_received
                self.pot -= amount_received                

    def _deal_cards(self):

        for player in self.players_in_hand():
            player.set_cards(self.deck.draw(2))    

    def _update_table_players(self):
        for p in self.players:
            p.table = self.table

    def _deal_flop(self):
        self.table = self.deck.draw(3)
        self._update_table_players()

    def _deal_turn(self):
        self.table.append(self.deck.drawOne())
        self._update_table_players()

    def _deal_river(self):
        self.table.append(self.deck.drawOne())
        self._update_table_players()

    def play(self):

        while(len(self.players) > 1):
            self._play_hand()
            self.table = []
            self.dealer = (self.dealer + 1) % len(self.players)

            for player in self.players:
                player.soft_reset()
                print_debug(player, self.debug)

            self.players = self.players_in_hand()

        print_debug('\nEnd of game! ~~  ', self.debug)
        return self.players[0].__class__.__name__
        for p in self.all_players:  
            print_debug(p, self.debug)

if __name__ == '__main__':

    players = [ RandomPlayer(), AgressivePlayer(), SoftRandomPlayer(), TightPlayer()]
    players = [ RandomPlayer('Fabio'), AgressivePlayer('Agressif'), SoftRandomPlayer('RandomBoy'), TightPlayer('Jonny Apertadinho')]
    pg = PokerEnv(players, 100, 2)
    total_chips = sum([p.stack for p in pg.players])
    pg.play()
    for i in range(1000):
        print(i)
        pg.reset_env()
        pg.play()
        end_chips = sum([p.stack for p in pg.players])
        assert(end_chips == total_chips)
