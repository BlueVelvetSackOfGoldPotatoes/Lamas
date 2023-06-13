import os

import networkx as nx
from matplotlib import pyplot as plt

from mafia_players import Roles

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

class KripkeModel:
    def __init__(self, game):
        self.states = []
        self.propositions = []
        self.relations = []
        self.transitions = []
        self.game = game
        self.G = nx.DiGraph()

    def add_state(self, name):
        state = State(name)
        self.states.append(state)
        return state

    def add_proposition(self, text):
        proposition = Proposition(text)
        self.propositions.append(proposition)
        return proposition

    def add_relation(self, state1, state2, proposition):
        relation = Relation(state1, state2, proposition)
        self.relations.append(relation)
        return relation

    def add_transition(self, state1, state2, action):
        transition = Transition(state1, action, state2)
        self.transitions.append(transition)
        return transition

    def build_model(self):        
        # Add nodes for each state in the model
        for state in self.states:
            self.G.add_node(state.name, color='blue')

        # Add nodes for each proposition in the model
        for prop in self.propositions:
            self.G.add_node(prop.name, color='red')

        # Add edges for each relation in the model
        for relation in self.relations:
            self.G.add_edge(relation.state.name, relation.proposition.name)

        # Define transitions and relations based on the current state of the game
        for transition in self.transitions:
            for relation in transition.relations:
                self.G.add_edge(relation.state.name, relation.proposition.name)
                    
    def update_model(self, player, role):
        # Update the model based on new information
        for proposition in self.propositions:
            if proposition.name == f'{player.name}_is_{role.name}':
                # When we discover a player's role, this becomes a belief for all the players
                for state in self.states:
                    # So, we need to update every player's belief set
                    if state.name != player.name:
                        # Update other players' beliefs about the role of this player
                        self.relations.append(Relation(state, proposition))

                # Update the graph
                self.G.add_node(proposition.name, color='red')
                for state in self.states:
                    if state.name != player.name:
                        self.G.add_edge(state.name, proposition.name)

    def get_believed_roles(self, player):
        # Get all roles believed possible for a given player
        believed_roles = []
        for relation in self.relations:
            if relation.state.name == player.name:
                believed_roles.append(relation.proposition.name.split('_is_')[1])

        return believed_roles

    def get_possible_roles(self, player):
        if hasattr(player, 'cached_roles') and player.cached_roles is not None:
            return player.cached_roles

        player.cached_roles = []
        for relation in self.relations:
            if relation.state.name == player.name:
                possible_role = relation.proposition.name.split('_is_')[1]
                player.cached_roles.append(possible_role)

        return player.cached_roles if player.cached_roles else []

    def draw_model(self, iter):        
        pos = nx.spring_layout(self.G, scale=2)
        plt.figure(figsize=(8, 6))
        color_map = [self.G.nodes[node]['color'] for node in self.G.nodes]

        nx.draw_networkx(self.G, pos, node_color=color_map)

        # Draw node labels
        node_labels = {node: "\n".join(node.split("\n")[:2]) for node in self.G.nodes}
        nx.draw_networkx_labels(self.G, pos, labels=node_labels, font_size=8)

        plt.title("Kripke Model")

        output_dir = "./model_graphs/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        plt.savefig("./model_graphs/kripke_" + str(iter) + ".png", bbox_inches='tight') 
        
        
        # pos = nx.spring_layout(self.G)
        # plt.figure(figsize=(8, 6))
        # nx.draw_networkx(self.G, pos, arrows=True, with_labels=True, node_size=1000, alpha=0.3, font_weight='bold')
        # plt.title("Kripke Model")

        # output_dir = "./model_graphs/"
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
        # plt.savefig("./model_graphs/kripke_" + str(iter) + ".png")