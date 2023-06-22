import random

from enum import Enum
from mlsolver.formula import *

# random.seed(42)


class Roles(Enum):
    VILLAGER = 0
    MAFIOSO = 1
    DOCTOR = 2
    INFORMANT = 3


class Player:
    def __init__(self, name="Player"):
        self.role = None
        self.alivePlayers = []
        self.players = []
        self.deadPlayers = []
        self.playerBeliefs = []  # List of tuples (player, list of beliefs)
        self.name = name
        self.kripke_model = None  # Will be set by MafiaGame
        self.player_id = None # Will be set by MafiaGame
        self.cached_roles = None  # Will be set by KripkeModel
        self.model = None # Will be set by MafiaGame
        self.currentWorld = None # Will be set by MafiaGame

    def print_state(self):
        print(f"Name: {self.name}")
        print(f"Own role: {self.role}")
        print("Player beliefs:")
        for belief in self.playerBeliefs:
            print(f"{belief[0].name}: {belief[1]}, " + ("dead" if belief[0] not in self.alivePlayers else "alive"))
        print("")
        
    def convertLetterToRole(self, letter):
        for role in Roles:
            if role.name[0] == letter:
                return role
        return None

    def initializeBeliefs(self, model, currentWorld):
        for player in self.alivePlayers:
            self.players.append(player)
        self.readKripkeModel()
        
    def vote(self):
        # Use the Kripke model to inform the voting strategy
        candidates = [belief[0] for belief in self.playerBeliefs if
                      (belief[0] in self.alivePlayers and "MAFIOSO" in self.kripke_model.get_possible_roles(belief[0]))]
        if not candidates:
            # Fall back to random voting if there are no candidates whom the Kripke model thinks could be a mafioso
            candidates = [player for player in self.alivePlayers if player != self]
        # Vote for a random candidate
        return random.choice(candidates)

    def die(self):
        roleLetter = self.role.name[0]
        for player in self.alivePlayers:
            newRelations = set()
            for relation in self.model.ks.relations[str(player.player_id)]:
                if relation[1][self.player_id] == roleLetter:
                    newRelations.add(relation)
            self.model.ks.relations[str(player.player_id)] = newRelations
            player.readKripkeModel()
            '''
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    belief[1].clear()
                    belief[1].append(self.role.name)
            '''

    def updateBeliefs(self, deceased):
        for belief in self.playerBeliefs:
            if belief[0] == deceased:
                belief[1].clear()
                belief[1].append(deceased.role.name)

            elif deceased.role == Roles.MAFIOSO:
                if 'MAFIOSO' in belief[1]:
                    belief[1].remove('MAFIOSO')
                    
    
    def readKripkeModel(self):
        num_players = len(self.currentWorld)
        self.playerBeliefs = []
        for player in self.players:
            self.playerBeliefs.append((player, []))
        for relation in self.model.ks.relations[str(self.player_id)]:
            if self.currentWorld == relation[0]:
                for num, role in enumerate(relation[1]):
                    actualRole = self.convertLetterToRole(role)
                    if actualRole.name not in self.playerBeliefs[num][1]:
                        self.playerBeliefs[num][1].append(actualRole.name)


class Villager(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.VILLAGER

    def suspectMafioso(self, player, candidate):
        player.accusations[candidate.name] += 1


class Informant(Villager):
    def __init__(self):
        super().__init__()
        self.role = Roles.INFORMANT

    def initializeBeliefs(self, model, currentWorld, target=None):
        # Informants know who one of the mafiosi is
        if target is None:
            mafiosi = [pl for pl in self.alivePlayers if isinstance(pl, Mafioso)]
            if not mafiosi:
                print("No mafiosi for the informant to know about!")
                super().initializeBeliefs(model, currentWorld)
                return
            target = random.choice(mafiosi)
        newRelations = set()
        for relation in model.ks.relations[str(self.player_id)]:
            if relation[1][target.player_id] == 'M':
                newRelations.add(relation)
        model.ks.relations[str(self.player_id)] = newRelations
        super().initializeBeliefs(model, currentWorld)


class Mafioso(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.MAFIOSO

    def initializeBeliefs(self, model, currentWorld):
        # Mafiosi know who the other mafiosi are.
        # Therfore, update this mafioso's accessibility relations.
        #mafiaFormula = Implies("phi is in the mafia", "this player knows that phi is in the mafia")
        newRelations = set()
        for relation in model.ks.relations[str(self.player_id)]:
            #print(relation)
            add = True
            for location in range(len(relation[0])):
                if relation[0][location] == 'M' and relation[1][location] != 'M':
                    add = False
            if add:
                newRelations.add(relation)
        model.ks.relations[str(self.player_id)] = newRelations
        super().initializeBeliefs(model, currentWorld)


    def vote(self):
        candidates = [belief[0] for belief in self.playerBeliefs if
                      (belief[0] in self.alivePlayers and "MAFIOSO" not in belief[1])]
        # Vote for a random villager who is not in the mafia
        return random.choice(candidates)
    
    def updateBeliefs(self, deceased):
        # Mafioso don't need to update their beliefs about other mafioso's roles
        if deceased.role == Roles.MAFIOSO:
            return

        super().updateBeliefs(deceased)


class Doctor(Villager):
    def __init__(self):
        super().__init__()
        self.role = Roles.DOCTOR

    def protect(self):
        candidates = [player for player in self.alivePlayers if player != self]
        protected = random.choice(candidates)
        return protected
