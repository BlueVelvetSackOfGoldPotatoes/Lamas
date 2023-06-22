import random

from enum import Enum


class Roles(Enum):
    VILLAGER = 0
    MAFIOSO = 1
    DOCTOR = 2
    INFORMANT = 3


class Player:
    def __init__(self, name="Player"):
        self.role = None
        self.alivePlayers = []
        self.deadPlayers = []
        self.playerBeliefs = []  # List of tuples (player, list of beliefs)
        self.name = name

    def print_state(self):
        print(f"Name: {self.name}")
        print(f"Own role: {self.role}")
        print("Player beliefs:")
        for belief in self.playerBeliefs:
            print(f"{belief[0].name}: {belief[1]}, " + ("dead" if belief[0] not in self.alivePlayers else "alive"))
        print("")

    def initializeBeliefs(self):
        for player in self.alivePlayers:
            if player == self:
                self.playerBeliefs.append((player, [self.role.name]))
            else:
                self.playerBeliefs.append((player, [role.name for role in Roles]))

    def vote(self):
        candidates = [belief[0] for belief in self.playerBeliefs if
                      (belief[0] in self.alivePlayers and "MAFIOSO" in belief[1])]
        # Vote for a random possible mafioso
        return random.choice(candidates)

    def die(self):
        for player in self.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    belief[1].clear()
                    belief[1].append(self.role.name)

    def updateKnowledge(self):
        for player in self.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    if 'MAFIOSO' in belief[1]:
                        belief[1].remove('MAFIOSO')


class Mafioso(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.MAFIOSO

    def initializeBeliefs(self):
        super().initializeBeliefs()
        # Mafiosi know who the other mafiosi are
        for belief in self.playerBeliefs:
            if belief[0].role == Roles.MAFIOSO:
                for role in Roles:
                    if role != Roles.MAFIOSO and role.name in belief[1]:
                        belief[1].remove(role.name)
            else:
                belief[1].remove(Roles.MAFIOSO.name)

    def vote(self):
        candidates = [belief[0] for belief in self.playerBeliefs if
                      (belief[0] in self.alivePlayers and "MAFIOSO" not in belief[1])]
        # Vote for a random villager who is not in the mafia
        return random.choice(candidates)


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
        super().initializeBeliefs()
        # Informants know who one of the mafiosi is
        if target is None:
            mafiosi = [pl for pl in self.alivePlayers if isinstance(pl, Mafioso)]
            if not mafiosi:
                print("No mafiosi for the informant to know about!")
                return
            target = random.choice(mafiosi)
        targetBelief = [belief for belief in self.playerBeliefs if belief[0] == target][0]
        targetBelief[1].clear()
        targetBelief[1].append(Roles.MAFIOSO.name)


class Doctor(Villager):
    def __init__(self):
        super().__init__()
        self.role = Roles.DOCTOR

    def initializeBeliefs(self):
        super().initializeBeliefs()
        # Doctors know who the other Doctors are
        for belief in self.playerBeliefs:
            if belief[0].role == Roles.DOCTOR:
                for role in Roles:
                    if role != Roles.DOCTOR and role.name in belief[1]:
                        belief[1].remove(role.name)
            else:
                belief[1].remove(Roles.DOCTOR.name)

    def changeDoctorsKnowledge(self, villager):
        # After saving a player from the night phase, update the knowledge that he is innocent
        for belief in self.playerBeliefs:
            if belief[0] == villager:
                if 'MAFIOSO' in belief[1]:
                    belief[1].remove('MAFIOSO')

    def revealDoctor(self):
        for player in self.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    for role in Roles:
                        if role != Roles.DOCTOR and role.name in belief[1]:
                            belief[1].remove(role.name)