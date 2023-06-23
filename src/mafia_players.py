import random

from enum import Enum
from mlsolver.formula import *


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

    def initializeBeliefs(self):
        for player in self.alivePlayers:
            self.players.append(player)
        self.readKripkeModel()
        
    def vote(self):
        suspected_mafioso = [belief[0] for belief in self.playerBeliefs if
                             (belief[0] in self.alivePlayers and ["MAFIOSO"] == belief[1])]
        if suspected_mafioso:
            return suspected_mafioso[0]

        candidates = [belief[0] for belief in self.playerBeliefs if
                      (belief[0] in self.alivePlayers and "MAFIOSO" in belief[1])]
        # Vote for a random possible mafioso
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
            
    def updateKnowledge(self):
        for player in self.alivePlayers:
            player.updateRelations(lambda relation: relation[1][self.player_id] != 'M')

    def revealPlayerID(self):
        for player in self.alivePlayers:
            player.updateRelations(lambda relation: relation[1][self.player_id] == self.role.name[0])
            
    def updateRelations(self, func):
        newRelations = set()
        for relation in self.model.ks.relations[str(self.player_id)]:
            if func(relation):
                newRelations.add(relation)
        self.model.ks.relations[str(self.player_id)] = newRelations
        self.readKripkeModel()
        
    def mafiaMembersKnown(self, relation):
        for location in range(len(relation[0])):
            if relation[0][location] == 'M' and relation[1][location] != 'M':
                return False
        return True
        
    def doctorsKnown(self, relation):
        for location in range(len(relation[0])):
            if relation[0][location] == 'D' and relation[1][location] != 'D':
                return False
        return True
    
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
        self.accusations = None

    def suspectMafioso(self, candidate):
        self.accusations[candidate.name] += 1


class Informant(Villager):
    def __init__(self):
        super().__init__()
        self.role = Roles.INFORMANT

    def initializeBeliefs(self, target=None):
        # Informants know who one of the mafiosi is
        if target is None:
            mafiosi = [pl for pl in self.alivePlayers if isinstance(pl, Mafioso)]
            if not mafiosi:
                print("No mafiosi for the informant to know about!")
                super().initializeBeliefs(model, currentWorld)
                return
            target = random.choice(mafiosi)
        super().initializeBeliefs()
        self.updateRelations(lambda relation: relation[1][target.player_id] == 'M')


class Mafioso(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.MAFIOSO

    def initializeBeliefs(self):
        # Mafiosi know who the other mafiosi are.
        # Therfore, update this mafioso's accessibility relations.
        super().initializeBeliefs()
        self.updateRelations(self.mafiaMembersKnown)

    def vote(self):
        candidates = [belief[0] for belief in self.playerBeliefs if
                      (belief[0] in self.alivePlayers and "MAFIOSO" not in belief[1])]
        # Vote for a random villager who is not in the mafia
        return random.choice(candidates)


class Doctor(Villager):
    def __init__(self):
        super().__init__()
        self.role = Roles.DOCTOR

    def initializeBeliefs(self):
        # Doctors know who the other Doctors are
        super().initializeBeliefs()
        self.updateRelations(self.doctorsKnown)

    def changeDoctorsKnowledge(self, villager):
        # After saving a player from the night phase, update the knowledge that he is innocent
        self.updateRelations(lambda relation: relation[1][villager.player_id] != 'M')
