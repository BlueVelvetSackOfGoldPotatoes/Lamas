import os

import networkx as nx
from matplotlib import pyplot as plt

class KripkeModel:
    def __init__(self, game):
        self.game = game
        self.G = None

    def build_model(self):
        self.G = nx.DiGraph()
        for player in self.game.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] in self.game.alivePlayers:
                    for role in belief[1]:
                        self.G.add_edge(player.name, f"{belief[0].name}_{role}")