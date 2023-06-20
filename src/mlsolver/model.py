""" Three wise men puzzle

Module contains data model for three wise men puzzle as Kripke strukture and agents announcements as modal logic
formulas
"""

from kripke import KripkeStructure, World
from formula import Atom, And, Not, Or, Box_a, Box_star


class WiseMenWithHat:
    """
    Class models the Kripke structure of the "Three wise men example.
    """

    knowledge_base = []

    def __init__(self):
        worlds = [
            World('RWW', {'1:R': True, '2:W': True, '3:W': True}),
            World('RRW', {'1:R': True, '2:R': True, '3:W': True}),
            World('RRR', {'1:R': True, '2:R': True, '3:R': True}),
            World('WRR', {'1:W': True, '2:R': True, '3:R': True}),

            World('WWR', {'1:W': True, '2:W': True, '3:R': True}),
            World('RWR', {'1:R': True, '2:W': True, '3:R': True}),
            World('WRW', {'1:W': True, '2:R': True, '3:W': True}),
            World('WWW', {'1:W': True, '2:W': True, '3:W': True}),
        ]

        relations = {
            '1': {('RWW', 'WWW'), ('RRW', 'WRW'), ('RWR', 'WWR'), ('WRR', 'RRR')},
            '2': {('RWR', 'RRR'), ('RWW', 'RRW'), ('WRR', 'WWR'), ('WWW', 'WRW')},
            '3': {('WWR', 'WWW'), ('RRR', 'RRW'), ('RWW', 'RWR'), ('WRW', 'WRR')}
        }

        relations.update(add_reflexive_edges(worlds, relations))
        relations.update(add_symmetric_edges(relations))

        self.ks = KripkeStructure(worlds, relations)

        # Wise man ONE does not know whether he wears a red hat or not
        self.knowledge_base.append(And(Not(Box_a('1', Atom('1:R'))), Not(Box_a('1', Not(Atom('1:R'))))))

        # This announcement implies that either second or third wise man wears a red hat.
        self.knowledge_base.append(Box_star(Or(Atom('2:R'), Atom('3:R'))))

        # Wise man TWO does not know whether he wears a red hat or not
        self.knowledge_base.append(And(Not(Box_a('2', Atom('2:R'))), Not(Box_a('2', Not(Atom('2:R'))))))

        # This announcement implies that third men has be the one, who wears a red hat
        self.knowledge_base.append(Box_a('3', Atom('3:R')))
        

class Mafia:
    """
    Class models a game of Mafia.
    """

    knowledge_base = []

    def __init__(self, roles = {"mafiosi": 2, "villagers": 3, "informants": 1}):
        # Each world contains one role for each player, so the amount of worlds is role_count^player_count.
        world_count = len(roles.keys()) ** sum(roles.values()) 
        print(f"The number of worlds in this Kripke model will be at most {world_count}.")
        
        worlds = self.generate_worlds(roles)

        relations = {
            '1': {('RWW', 'WWW'), ('RRW', 'WRW'), ('RWR', 'WWR'), ('WRR', 'RRR')},
            '2': {('RWR', 'RRR'), ('RWW', 'RRW'), ('WRR', 'WWR'), ('WWW', 'WRW')},
            '3': {('WWR', 'WWW'), ('RRR', 'RRW'), ('RWW', 'RWR'), ('WRW', 'WRR')}
        }

        relations.update(add_reflexive_edges(worlds, relations))
        relations.update(add_symmetric_edges(relations))

        self.ks = KripkeStructure(worlds, relations)

        # Wise man ONE does not know whether he wears a red hat or not
        self.knowledge_base.append(And(Not(Box_a('1', Atom('1:R'))), Not(Box_a('1', Not(Atom('1:R'))))))

        # This announcement implies that either second or third wise man wears a red hat.
        self.knowledge_base.append(Box_star(Or(Atom('2:R'), Atom('3:R'))))

        # Wise man TWO does not know whether he wears a red hat or not
        self.knowledge_base.append(And(Not(Box_a('2', Atom('2:R'))), Not(Box_a('2', Not(Atom('2:R'))))))

        # This announcement implies that third men has be the one, who wears a red hat
        self.knowledge_base.append(Box_a('3', Atom('3:R')))
        
    def generate_worlds(self, roles):
        worldLists = {}
        worldSize = sum(roles.values())
        for role in roles:
            worldLists[role] = self.add_players(role, roles[role], worldSize)
            worldSize -= roles[role]
        tempWorlds = []
        # Combine the worlds from add_players with only 1 player into actual worlds.
        print(worldLists)
        modelWorlds = combine_worlds(worldLists)
        
    
    def combine_worlds(self, worldLists):
        return worldLists
    
    def add_players(self, role, numPlayers, worldSize):
        print(f"Adding {numPlayers} {role}.")
        # The places where players with this role are added.
        places = [itr for itr in range(numPlayers)]
        # The "worlds" with only players with this role added.
        worlds = []
        while(True):
            # Add a world with the initial positions of the roles.
            world = [None for itr in range(worldSize)]
            for place in places:
                print(f"worldSize: {worldSize}. place: {place}.")
                print(f"places: {places}.")
                world[place] = role
            worlds.append(world)
            # Get positions where the players with this role should be added next.
            added = False
            for itr in range(1, numPlayers + 1):
                places[-itr] += 1
                if places[-itr] == worldSize:
                    continue
                additional = 1
                mustContinue = False
                for itr2 in range(itr - 1, 0, -1):
                    places[-itr2] = places[-itr] + additional
                    if places[-itr2] == worldSize:
                        mustContinue = True
                    additional += 1
                if mustContinue:
                    continue
                added = True
                break
            # If all position have been searched, we are done here.
            if not added:
                break
        return worlds



def add_symmetric_edges(relations):
    """Routine adds symmetric edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for r in agents_relations:
            x, y = r[1], r[0]
            result_agents.add((x, y))
        result[agent] = result_agents
    return result


def add_reflexive_edges(worlds, relations):
    """Routine adds reflexive edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for world in worlds:
            result_agents.add((world.name, world.name))
            result[agent] = result_agents
    return result

if __name__ == '__main__':
    mafia = Mafia()