import random

from enum import Enum

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
        self.deadPlayers = []
        self.playerBeliefs = []  # List of tuples (player, list of beliefs)
        self.name = name
        self.kripke_model = None  # Will be set by MafiaGame
        self.cached_roles = None  # Will be set by KripkeModel

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
        # Use the Kripke model to inform the voting strategy
        candidates = [player for player in self.alivePlayers if 'MAFIOSO' in self.kripke_model.get_believed_roles(player)]
        if not candidates:
            # Fall back to random voting if there are no candidates whom the Kripke model believes could be a mafioso
            candidates = [player for player in self.alivePlayers if player != self]
        # Vote for a random candidate
        return random.choice(candidates)

    def update_beliefs(self, deceased):
        # The deceased player's role is revealed
        for belief in self.playerBeliefs:
            if belief[0] == deceased:
                belief[1].clear()
                belief[1].append(deceased.role.name)
        # Update the Kripke model with this new information
        self.kripke_model.update_model(deceased, deceased.role)

    def die(self):
        for player in self.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    belief[1].clear()
                    belief[1].append(self.role.name)

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
        """Vote to eliminate a player."""
        # Get the roles each player is believed to be
        believed_roles = {player: self.kripke_model.get_believed_roles(player) for player in self.alivePlayers}
        # Vote for the player most likely to be a mafioso
        most_suspected = max(believed_roles, key=lambda player: believed_roles[player].count('MAFIOSO'))
        return most_suspected

    def updateBeliefs(self, deceased):
        """Update beliefs based on the deceased player's role."""
        if deceased.role == Roles.MAFIOSO:
            return

        # Get the possible roles the deceased could have been
        possible_roles = self.kripke_model.get_possible_roles(deceased)
        # Update beliefs accordingly
        for player in self.alivePlayers:
            if player != self:
                if 'MAFIOSO' in possible_roles:
                    player.playerBeliefs.append((deceased, ['MAFIOSO']))
                else:
                    player.playerBeliefs.append((deceased, ['VILLAGER', 'DOCTOR', 'INFORMANT']))

class Doctor(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.DOCTOR

    def protect(self):
        candidates = [player for player in self.alivePlayers if player != self]
        protected = random.choice(candidates)
        return protected

    def suspectMafioso(self, player, candidate):
        player.accusations[candidate.name] += 1
