from Player import Player
from model import DeepQNetwork

class QAgentPlayer(Player):

    def __init__(self, name = None):
        super().__init__(name)

    def  act(self, possibleActions):
        pass