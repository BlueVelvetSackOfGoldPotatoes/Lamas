import os

import networkx as nx
from matplotlib import pyplot as plt


class KripkeModel:
    def __init__(self, game):
        self.game = game
        self.G = nx.DiGraph()

    def build_model(self):
        for player in self.game.players:
            for belief in player.playerBeliefs:
                for role in belief[1]:
                    self.G.add_edge(player.name, f"{belief[0].name}_{role}")

    def draw_model(self, iter):
        pos = nx.spring_layout(self.G)
        plt.figure(figsize=(8, 6))
        nx.draw_networkx(self.G, pos, arrows=True, with_labels=True, node_size=1000, alpha=0.3, font_weight='bold')
        plt.title("Kripke Model")

        output_dir = "./model_graphs/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        plt.savefig("./model_graphs/kripke_" + str(iter) + ".png")