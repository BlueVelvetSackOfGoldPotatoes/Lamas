import random

from mafia_players import Mafioso, Roles, Villager, Doctor, Informant


class MafiaGame:
    def __init__(self, villagers=10, mafiosi=3, doctors=1, informants=1):
        self.players = []
        self.addPlayers(mafiosi, Mafioso)
        self.addPlayers(villagers, Villager)
        self.addPlayers(doctors, Doctor)
        self.addPlayers(informants, Informant)
        self.alivePlayers = self.players
        self.deadPlayers = []
        for player in self.players:
            player.alivePlayers = self.alivePlayers
            player.initializeBeliefs()
            player.accusations = {player.name: 0 for player in self.players if player.role.name == 'MAFIOSO'}

    def addPlayers(self, count, Role):
        for itr in range(count):
            self.players.append(Role())
            self.players[-1].name = f"{self.players[-1].role.name.capitalize()} {itr}"

    def voteVillager(self,  mafia_strategy='random', votes=None):
        # Night phase strategies
        candidates = None
        if mafia_strategy == 'enemy':
            # Choose a villager who voted against mafia in the latest day phase
            candidates = [cand for cand, vote in votes.items() if cand in self.alivePlayers and vote == 1]
        elif mafia_strategy == 'allied':
            # Choose a villager who supported mafia in the latest day phase
            candidates = [cand for cand, vote in votes.items() if cand in self.alivePlayers and
                          cand.role.name in ["VILLAGER", "DOCTOR", "INFORMANT"] and
                          vote == 0]

        if mafia_strategy == 'random' or not candidates:
            # Choose randomly a villager to kill
            candidates = [cand for cand in self.alivePlayers if cand.role.name in ["VILLAGER", "DOCTOR", "INFORMANT"]]

        villager = random.choice(candidates)

        return villager

    def protectPlayer(self):
        """ This function is called only if at least one Doctor is alive. """
        # Choose one player to protect during the night phase
        candidates = [player for player in self.alivePlayers]
        protected = random.choice(candidates)
        return protected

    def kill(self, player):
        self.alivePlayers.remove(player)
        self.deadPlayers.append(player)
        player.die()

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