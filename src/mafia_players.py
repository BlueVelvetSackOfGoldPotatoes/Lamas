import random

from enum import Enum

# random.seed(42)


class Roles(Enum):
    VILLAGER = 0
    MAFIOSO = 1


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
                    for role in Roles:
                        if role.name in belief[1] and role != self.role:
                            belief[1].remove(role.name)

    def updateKnowledge(self):
        for player in self.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    if 'MAFIOSO' in belief[1]:
                        belief[1].remove('MAFIOSO')


class Villager(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.VILLAGER

    def suspectMafioso(self, player, candidate):
        player.accusations[candidate.name] += 1


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
