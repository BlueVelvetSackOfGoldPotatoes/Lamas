import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
import random

"""
Mafia Game Simulator:

This script simulates a version of the Mafia game, implementing logic and knowledge 
representation using a Kripke model. 

Main Components:

1. Kripke Model:
   The Kripke Model represents the possible worlds, including who the mafiosi might be, in the game.
   It's used to model the knowledge of each agent in the game and how it changes over time. 
   
2. Game:
   The Game class coordinates the overall flow of the game. It manages the day and night cycles, 
   the addition of agents, updating of the Kripke model, and the execution of actions that agents make.

3. Agents:
   Agents can be either Villagers or Mafiosi. They have their own knowledge base which is a subset of 
   the game's Kripke Model. Mafiosi are aware of their identity, but Villagers are not.
   
4. Knowledge Base:
   Each agent's Knowledge Base is updated according to the actions performed and witnessed during the 
   game's progression. The update rules simulate how real players might infer information based on what 
   they observe.

5. Actions:
   The main actions are:
   - Mafioso can 'kill' villagers during the night.
   - Villagers (including Mafiosi undercover) can 'vote' during the day to eliminate a suspected Mafioso.
   
6. Simulation:
   The simulation runs by cycling between 'day' and 'night' phases. During the night, the Mafioso 
   chooses a victim. During the day, the villagers (including the disguised mafiosi) vote to eliminate 
   a suspected mafioso. The game ends when all mafiosi are eliminated or the number of mafiosi equals 
   the number of villagers.

7. Visualization:
   At each cycle, a function is called to output the current knowledge network among agents, displaying 
   what each agent knows about the other's possible roles.
"""

class World:
    """
    A class to represent a possible world in the Kripke model.
    """
    def __init__(self, mafia):
        self.mafia = set(mafia) # set of agents that are mafia in this world 

    def __contains__(self, agent):
        return agent in self.mafia

class KripkeModel:
    """
    A class to represent the Kripke model for the Mafia game with two mafiosi.
    """
    def __init__(self, agents):
        self.worlds = {World(mafia) for mafia in combinations(agents, 2)}
        self.relations = {agent.name: {pair for pair in combinations(self.worlds, 2)
                                  if agent.name not in pair[0].mafia and agent.name not in pair[1].mafia}
                          for agent in agents}

    def get_possible_mafia(self, agent):
        """
        Returns the set of possible mafiosi according to agent's knowledge.
        """
        return {world.mafia for pair in self.relations[agent.name] for world in pair}

    def update_after_exile(self, agent):
        """
        Updates the Kripke model after an agent is exiled.
        """
        self.worlds = {world for world in self.worlds if agent.name not in world.mafia}
        self.relations = {agent.name: {pair for pair in self.relations[agent.name] if all(agent.name not in world.mafia for world in pair)}
                          for agent in self.relations}

    def update_after_night(self):
        """
        Updates the Kripke model after the night phase.
        """
        self.worlds = {world for world in self.worlds if len(world.mafia) > 0}
        self.relations = {agent: {pair for pair in self.relations[agent] if all(agent not in world.mafia for world in pair)}
                          for agent in self.relations}

    def update_after_kill(self, mafioso, target):
        """
        Updates the Kripke model after a mafioso kills a target.
        """
        self.worlds = {world for world in self.worlds if target.name not in world.mafia}
        self.relations = {agent: {pair for pair in self.relations[agent] if all(target.name not in world.mafia for world in pair)}
                          for agent in self.relations}

class Agent:
    def __init__(self, role, name):
        self.role = role
        self.name = name
        self.alive = True
        self.model = None
        self.possible_mafia = None

    def set_model(self,model):
        self.model = model

    def update_knowledge(self):
        self.possible_mafia = self.model.get_possible_mafia(self)

    def print_knowledge(self):
        print(f'{self.name} suspects the following pairs as mafiosi:')
        for mafia_pair in self.possible_mafia:
            print(f' - {mafia_pair}')
        print()

    def vote(self, suspected_mafioso):
        print(f'{self.name} votes to exile {suspected_mafioso}.')

    def kill(self, target):
        pass

    def survive(self):
        pass

class Mafioso(Agent):
    def __init__(self, name, all_mafioso):
        super().__init__('mafioso', name)
        self.possible_mafia = {frozenset({self.name, other}) for other in all_mafioso if other != self.name}

    def kill(self, target):
        print(f'{self.name} kills {target.name} during the night.')
        target.alive = False

    def get_type(self):
        return "mafia"

class Villager(Agent):
    def __init__(self, name):
        super().__init__('villager', name)
        
    def survive(self):
        print(f'{self.name} survives the night.')
    
    def get_type(self):
        return "villager"

class Game:
    def __init__(self, agents):
        self.agent_count = len(agents)
        self.agents = agents
        self.agent_names = [agent.name for agent in agents]
        self.kripke_model = KripkeModel(self.agents)
        self.turns = 0
        self.night = False

    def add_agent(self, agent):
        self.agents.append(agent)
        self.agent_names.append(agent.name)

    def run_game(self):
        while len([a for a in self.agents if a.alive]) > 1:
            for agent in self.agents:
                agent.set_model(self.kripke_model)
            self.turns += 1
            self.night = not self.night
            
            print(f"\nTurn {self.turns}, {'Night' if self.night else 'Day'}:")

            # Check if there's a single agent left
            if len([a for a in self.agents if a.alive]) == 1:
                print(f"{self.agents[0].name} is the sole survivor and wins the game!")
                break

            # Night turn
            if self.night:
                for mafioso in [a for a in self.agents if isinstance(a, Mafioso) and a.alive]:
                    # Randomly select a non-mafioso agent to be the target of the kill
                    possible_targets = [a for a in self.agents if not isinstance(a, Mafioso) and a.alive]
                    if possible_targets:
                        target = random.choice(possible_targets)
                        mafioso.kill(target)
                        self.kripke_model.update_after_kill(mafioso, target)
                self.kripke_model.update_after_night()

            # Day turn
            else:
                # Each agent votes to exile a suspected mafioso
                for agent in [a for a in self.agents if a.alive]:
                    suspected_mafioso = agent.suspect(self.agents)
                    agent.vote(suspected_mafioso)
                    if suspected_mafioso:
                        suspected_mafioso.alive = False
                        self.kripke_model.update_after_exile(suspected_mafioso)

            # Print out each agent's knowledge at the end of the turn
            for agent in self.agents:
                print(agent.name)
                print(agent.get_type())

                if agent.get_type() != "mafia":
                    agent.print_knowledge()
            
            self.draw_knowledge_graph()

    def draw_knowledge_graph(self):
        G = nx.DiGraph()
        for agent in self.agents:
            for world in self.kripke_model.worlds:
                if agent in world.agents:
                    for other_world in world.relation_worlds:
                        G.add_edge(world.name, other_world.name, label=agent.role)

        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.show()

def main():
    players = []

    # Generate villagers
    for i in range(8):
        villager = Villager(f'Villager_{i}')
        players.append(villager)

    # Generate mafiosi
    mafiosi_names = [f'Mafioso_{i}' for i in range(2)]
    for name in mafiosi_names:
        mafioso = Mafioso(name, mafiosi_names)
        players.append(mafioso)

    game = Game(players)
    game.run_game()
    
if __name__ == "__main__":
    main()

