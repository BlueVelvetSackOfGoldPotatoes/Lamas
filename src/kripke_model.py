import os

import networkx as nx
from matplotlib import pyplot as plt

class KripkeModel:
    def __init__(self, game):
        self.game = game
        self.states = []
        self.propositions = []
        self.relations = []
        self.transitions = []
        self.G = nx.DiGraph()

    def build_model(self):
        # Clear the previous state of the model
        self.G.clear()
        
        # Add nodes for each player's beliefs
        for player in self.game.alivePlayers:
            for belief in player.playerBeliefs:
                # If the player believe that someone could be a mafioso
                if "MAFIOSO" in belief[1]:
                    # Each belief will be represented as a node in the graph
                    node_label = f"{player.name} believes {belief[0].name} is MAFIOSO"
                    self.G.add_node(node_label)
        
        # Add edges between nodes to represent the players' relationships and suspicions
        # An edge between two nodes means that the player's belief in the first node could lead to the belief in the second node...
        for node1 in self.G.nodes:
            for node2 in self.G.nodes:
                if node1 != node2:
                    # If two nodes represent beliefs of the same player
                    if node1.split()[0] == node2.split()[0]:
                        self.G.add_edge(node1, node2)

    def get_possible_roles(self, player):
        if hasattr(player, 'cached_roles') and player.cached_roles is not None:
            return player.cached_roles

        player.cached_roles = []
        for belief in player.playerBeliefs:
            for role in belief[1]:
                if self.G.has_edge(player.name, f"{belief[0].name}_{role}"):
                    player.cached_roles.append(role)

        return player.cached_roles if player.cached_roles else []

    def draw_model(self, iter):
        pos = nx.spring_layout(self.G, seed=42)
        plt.figure(figsize=(8, 6))

        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos, node_size=1000, alpha=0.5)

        # Draw edges
        nx.draw_networkx_edges(self.G, pos, width=1.0, alpha=0.5, edge_color='gray')

        # Draw node labels
        node_labels = {node: "\n".join(node.split("\n")[:2]) for node in self.G.nodes}
        nx.draw_networkx_labels(self.G, pos, labels=node_labels, font_size=8)

        plt.title("Kripke Model")

        output_dir = "./model_graphs/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        plt.savefig("./model_graphs/kripke_" + str(iter) + ".png", bbox_inches='tight')

class State:
    def __init__(self, player_role_assignments, knowledge_mappings):
        self.player_role_assignments = player_role_assignments
        self.knowledge_mappings = knowledge_mappings

class Proposition:
    def __init__(self, role_propositions, knowledge_propositions, alive_propositions):
        self.role_propositions = role_propositions
        self.knowledge_propositions = knowledge_propositions
        self.alive_propositions = alive_propositions

class Relation:
    def __init__(self, role_relations, knowledge_relations, alive_relations):
        self.role_relations = role_relations
        self.knowledge_relations = knowledge_relations
        self.alive_relations = alive_relations

class Transition:
    def __init__(self, from_state, to_state):
        self.from_state = from_state
        self.to_state = to_state