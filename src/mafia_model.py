import random
from kripke_model import KripkeModel
from mafia_players import Mafioso, Roles, Villager, Doctor, Informant
from mlsolver.model import Mafia
import numpy as np

class MafiaGame:
    def __init__(self, villagers=1, mafiosi=1, doctors=0, informants=0):
        self.kripke_model = KripkeModel(self)
        self.model = Mafia({"mafiosi": mafiosi, "villagers": villagers, "informants": informants, "doctors": doctors})
        self.players = []
        
        self.addPlayers(mafiosi, Mafioso)
        self.addPlayers(villagers, Villager)
        self.addPlayers(doctors, Doctor)
        self.addPlayers(informants, Informant)
        
        self.alivePlayers = self.players
        self.deadPlayers = []
        self.protectedPLayers = []
        self.revealedMafioso = False
        self.currentWorld = ""
        for player in self.players:
            self.currentWorld += player.role.name[0]
        self.currentWorld = self.currentWorld.upper()
        print("Actual world: " + self.currentWorld)
        
        for num, player in enumerate(self.players):
            player.player_id = num
            player.model = self.model
            player.currentWorld = self.currentWorld
        for player in self.players:
            player.alivePlayers = self.alivePlayers
            player.initializeBeliefs()
            player.accusations = {player.name: 0 for player in self.players if player.role.name == 'MAFIOSO'}

    def addPlayers(self, count, Role):
        for itr in range(count):
            player = Role()
            player.name = f"{player.role.name.capitalize()} {itr}"
            player.kripke_model = self.kripke_model
            self.players.append(player)

    def voteVillager(self,  mafia_strategy='random', votes=None):
        # Night phase strategies
        candidates = self.get_voting_priority(['DOCTOR'])
        if not candidates:
            candidates = self.get_voting_priority(['VILLAGER', 'DOCTOR', 'INFORMANT'])
        if not candidates:
            candidates = self.apply_mafia_strategy(mafia_strategy, votes)

        villager = random.choice(candidates)

        return villager

    def get_voting_priority(self, role):
        priority_players = []
        for player in self.alivePlayers:
            if player.role.name == 'VILLAGER':
                # Revealed special roles have a higher priority to be killed
                for belief in player.playerBeliefs:
                    if belief[0] in self.alivePlayers and belief[1] == role:
                        priority_players.append(belief[0])

        return priority_players

    def apply_mafia_strategy(self, mafia_strategy, votes):
        candidates = None

        if mafia_strategy == 'enemy':
            # Choose a villager who voted against mafia in the latest day phase
            candidates = [cand for cand, vote in votes.items() if cand in self.alivePlayers and vote == 1]
        elif mafia_strategy == 'allied':
            # Choose a villager who supported mafia in the latest day phase
            candidates = [cand for cand, vote in votes.items() if cand in self.alivePlayers and
                          isinstance(cand, Villager) and vote == 0]

        if mafia_strategy == 'random' or not candidates:
            # Choose randomly a villager to kill
            candidates = [cand for cand in self.alivePlayers if isinstance(cand, Villager)]

        return candidates

    def choose_protected_player(self):
        # Choose one player to protect during the night phase
        candidates = [player for player in self.alivePlayers]
        protected = random.choice(candidates)
        return protected
    
    def protectedID_is_known(self, protected):
        """ This function is called only if at least one Doctor is alive. """
        for player in self.alivePlayers:
            if player.role.name == 'VILLAGER' and player != protected:
                for belief in player.playerBeliefs:
                    if belief[0] == protected:
                        if 'MAFIOSO' not in belief[1]:
                            return True
                        else:
                            return False
    def savePlayer(self, protected):
        """ This function is called only if at least one Doctor is alive. """
        if protected not in self.protectedPLayers:
            self.protectedPLayers.append(protected)
        # Update the knowledge of Doctors about this player
        for player in self.alivePlayers:
            if isinstance(player, Doctor):
                player.changeDoctorsKnowledge(protected)

    def apply_doctors_strategy(self, doctors_strategy='deterministic', num_protectedPLayers=1):
        """ This function is called only if at least one Doctor is alive. """
        if doctors_strategy == 'deterministic' and len(self.protectedPLayers) == num_protectedPLayers:
            # Make a public announcement
            self.make_public_announcement()
        elif doctors_strategy == 'random' and len(self.protectedPLayers) > 0:
            # Reveal the Doctor(s) knowledge with a certain probability
            if np.random.rand() > 0.5:
                # Make a public announcement
                self.make_public_announcement()

    def make_public_announcement(self):
        print("A Doctor will make a public announcement about the saved players!\n")
        for player in self.protectedPLayers:
            print(f"Public Announcement of Doctor(s): {player.name} is an innocent saved by the Doctor(s)!\n")
            player.updateKnowledge()
        # Reveal the identity of one alive Doctor
        candidate_doctors = [cand for cand in self.alivePlayers if isinstance(cand, Doctor)]
        protected_doctors = [doctor for doctor in candidate_doctors if doctor in self.protectedPLayers]
        if protected_doctors:
            if len(protected_doctors) == 1:
                doctor = protected_doctors[0]
            elif len(protected_doctors) > 1:
                doctor = random.choice(protected_doctors)
        else:
            doctor = random.choice(candidate_doctors)
        doctor.revealPlayerID()
        print(f"The identity of {doctor.name} is now revealed!\n")
        # Empty the protected players list
        self.protectedPLayers = []

    def kill(self, player):
        self.alivePlayers.remove(player)
        self.deadPlayers.append(player)
        self.protectedPLayers.remove(player) if player in self.protectedPLayers else None
        player.die()
        
    def apply_informant_strategy(self, informant_strategy='random'):
        known_mafioso, informant = self.find_mafioso()
        alive_mafiosi = [cand for cand in self.alivePlayers if isinstance(cand, Mafioso)]
        if known_mafioso in alive_mafiosi:
            if len(alive_mafiosi) == 1 or informant_strategy == 'deterministic':
                print(f"Public announcement of Informant: The player {known_mafioso.name} is a Mafioso!\n")
                known_mafioso.revealPlayerID()
                informant.revealPlayerID()
                self.revealedMafioso = True
            elif informant_strategy == 'random':
                # Reveal the identity of one mafia member with a certain probability
                if np.random.rand() > 0.5:
                    print(f"Public announcement of Informant: The player {known_mafioso.name} is a Mafioso!\n")
                    known_mafioso.revealPlayerID()
                    informant.revealPlayerID()
                    self.revealedMafioso = True

    def find_mafioso(self):
        for player in self.alivePlayers:
            if isinstance(player, Informant):
                for belief in player.playerBeliefs:
                    if isinstance(belief[0], Mafioso) and belief[1] == ['MAFIOSO']:
                        return belief[0], player

        return None, None

    def checkWin(self):
        mafiosoCount = 0
        villagerCount = 0
        for player in self.alivePlayers:
            if isinstance(player, Mafioso):
                mafiosoCount += 1
            else:
                villagerCount += 1
        if mafiosoCount == 0:
            print("Villagers win!")
            return "Villagers"
        elif villagerCount == 0:
            print("Mafiosi win!")
            return "Mafiosi"
        return False
