from Deck import Deck
from Player import Player, RandomPlayer, SoftRandomPlayer, TightPlayer, AgressivePlayer
from Combos import Combo
from utils import print_debug


class PokerEnv:

    def __init__(self, players, stack, small_blind):
        self.state = 'ZERO'
        self.initial_stack = stack
        self.agent = Player('Fabio')
        players.append(self.agent)
        self.all_players = players
        self.players = self.players_in_hand()
        self.small_blind = small_blind
        self.big_blind = self.small_blind * 2
        self.sb_idx = None
        self.bb_idx = None
        self.table = []
        self.dealer = 0
        self.pot = 0
        self.halt = False
        self.highest_bet = self.big_blind
        self.deck = None
        self.possibleActions = ['CHECK', 'BET', 'CALL', 'FOLD']
        self.idx = 0
        self.agent_prev_stack = self.agent.stack
        self.action =  None
        self.reset_env()
        self.debug = True
        if self.debug:
            for p in self.players:
                p.debug = True
        self._set_state('START')

    def _set_state(self, state):
        self.state = state
        self.highest_bet = 0

        for player in self.players:
            player.on_table = 0
            if not player.folded:
                player.has_played = False

        print_debug('State -> '+ state, self.debug)

    def reset(self):
        self.reset_env()
        obs, reward, done, info = self.play()
        return obs

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

        if self.state == 'START':

            # Init game
            self.deck = Deck()
            self.deck.shuffle()
            self._set_state('PREFLOP')

            # BLINDS
            self.sb_idx = (self.dealer + 1) % len(self.players)
            self.bb_idx = (self.dealer + 2) % len(self.players)
            UTG = (self.dealer + 3) % len(self.players)

            self.pot = 0
            self.pot += self.players[self.sb_idx].call(self.small_blind)
            self.pot += self.players[self.bb_idx].call(self.big_blind)

            self._deal_cards()
            self.highest_bet = max([p.on_table for p in self.players])
            self.idx = UTG
        
        # PRE FLOP
        if self.state == 'PREFLOP':

            keepGoing = self.betting_round()

            if keepGoing == 'END_PHASE':
                self._deal_flop()
                self.idx = self.sb_idx
                self._set_state('FLOP')
                return True

            elif keepGoing == 'RESOLVE_WINNER':
                self._set_state('WRAP_UP')
                return True

            elif keepGoing == 'WAIT_FOR_AGENT':
                self.halt = True
                return False

            else:
                return True

        #FLOP
        if self.state == 'FLOP':

            keepGoing = self.betting_round()

            if keepGoing == 'END_PHASE':
                self._deal_turn()
                self.idx = self.sb_idx
                self._set_state('TURN')
                return True

            elif keepGoing == 'RESOLVE_WINNER':
                self._set_state('WRAP_UP')
                return True

            elif keepGoing == 'WAIT_FOR_AGENT':
                self.halt = True
                return False

            else:
                return True

        #TURN
        if self.state == 'TURN':

            keepGoing = self.betting_round()

            if keepGoing == 'END_PHASE':
                self._deal_river()
                self.idx = self.sb_idx
                self._set_state('RIVER')
                return True

            elif keepGoing == 'RESOLVE_WINNER':
                self._set_state('WRAP_UP')
                return True

            elif keepGoing == 'WAIT_FOR_AGENT':
                self.halt = True
                return False

            else:
                return True

        #RIVER
        if self.state == 'RIVER':

            keepGoing = self.betting_round()

            if keepGoing in ['END_PHASE', 'RESOLVE_WINNER']:

                self._set_state('WRAP_UP')
                return True

            elif keepGoing == 'WAIT_FOR_AGENT':
                self.halt = True
                return False

            else:
                return True
        # END ROUND
        if self.state == 'WRAP_UP':

            self._resolve_winners()

            self._set_state('START')
            return False
        
    def _get_game_state(self, player):

        return {
            'table' : self.table,
            'hand' : player.hand,
            'pot' : self.pot,
            'curr_bet' : self.highest_bet,
            'big_blind' : self.big_blind,
            'stacks' : [p.stack for p in self.players],
            'on_pots' : [p.on_pot for p in self.players],
            'folded' : [p.folded for p in self.players],
        }
    
    def _resolve_winners(self):

        while(self.pot):
            print(f'POT = {self.pot} -- ON_POTS = {[p.on_pot for p in self.players]}')
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

    def step(self, action):
        self.action = action
        self.halt = False
        return self.play()

    def play(self):

        while(len(self.players) > 1):
            keepGoing = True

            while(keepGoing):
                keepGoing = self._play_hand()

            if self.halt:
                reward = self.agent.stack + self.agent.on_pot - self.agent_prev_stack
                self.agent_prev_stack = self.agent.stack + self.agent.on_pot
                return self._get_game_state(self.agent), reward, False, None

            self.table = []
            self.dealer = (self.dealer + 1) % len(self.players)

            for player in self.players:
                player.soft_reset()
                print_debug(player, self.debug)

            self.players = self.players_in_hand()

        print_debug('End of game! ~~  ', self.debug)
        reward = self.agent.stack - self.agent_prev_stack
        if self.players[0] == self.agent:
            reward += 300
        else:
            reward -= 200
        return self._get_game_state(self.agent), reward, True, None

    def _accept_player_move(self, player, action):

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

    def betting_round(self):

        player = self.players[self.idx]
     
        othersCanCall = sum([p.stack for p in self.players if p.id != player.id]) > 0

        if not player.folded and player.stack > 0 and (othersCanCall or player.on_table < self.highest_bet):

            if player == self.agent and self.action == None:
                print('AGENT TIME TO ACT')
                return 'WAIT_FOR_AGENT'
            
            elif player == self.agent:
                action = self.action
                self.action = None
                
            else:
                action = player.act(self._get_game_state(player))          
            self._accept_player_move(player, action)
            player.has_played = True

        else:

            player.has_played = True

        self.idx = (self.idx + 1) % len(self.players)
        everyoneHasPlayed = all([p.folded or p.has_played or p.stack == 0 for p in self.players])
        playersNotFolderNotAllIn = list(filter(lambda p: (not p.folded and p.stack > 0), self.players))
        betStillToResolve = len(playersNotFolderNotAllIn) and self.highest_bet > min([ p.on_table for p in playersNotFolderNotAllIn])
        moreThanOnePlayerLeft = len([p for p in self.players if not p.folded]) > 1
        
        if moreThanOnePlayerLeft and (not everyoneHasPlayed or betStillToResolve):
            return True
        elif len([p for p in self.players if not p.folded]) == 1:
            return 'RESOLVE_WINNER'
        else:
            return 'END_PHASE'


if __name__ == '__main__':

    players = [ RandomPlayer(), AgressivePlayer(), SoftRandomPlayer(), TightPlayer()]
    players = [ AgressivePlayer('Agressif'), SoftRandomPlayer('RandomBoy'), TightPlayer('Jonny Apertadinho')]
    env = PokerEnv(players, 100, 2)
    obs = env.reset()
    done = False
    while(not done):
        action = env.agent.act(obs)
        print(action)
        obs, reward, done, info = env.step(action)
        print(obs, reward, done, info)