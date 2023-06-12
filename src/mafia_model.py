import random

from mafia_players import Mafioso, Roles, Villager


class MafiaGame:
    def __init__(self, villagers=10, mafiosi=3):
        self.players = []
        for itr in range(mafiosi):
            self.players.append(Mafioso())
            self.players[-1].name = "Mafioso " + str(itr)
        for itr in range(villagers):
            self.players.append(Villager())
            self.players[-1].name = "Villager " + str(itr)
        self.alivePlayers = self.players
        self.deadPlayers = []
        for player in self.players:
            player.alivePlayers = self.alivePlayers
            player.initializeBeliefs()
            player.accusations = {player.name: 0 for player in self.players if player.role.name == 'MAFIOSO'}

    def voteVillager(self,  mafia_strategy='random', votes=None):
        # Night phase
        candidates = None

        if mafia_strategy == 'enemy':
            # Choose a villager who voted against mafia in the latest day phase
            candidates = [cand for cand, vote in votes.items() if cand in self.alivePlayers and vote == 1]
        elif mafia_strategy == 'allied':
            # Choose a villager who supported mafia in the latest day phase
            candidates = [cand for cand, vote in votes.items() if cand in self.alivePlayers and cand.role.name == "VILLAGER" and vote == 0]

        if mafia_strategy == 'random' or not candidates:
            # Choose randomly a villager to kill
            candidates = [cand for cand in self.alivePlayers if cand.role.name == "VILLAGER"]

        villager = random.choice(candidates)

        return villager

    def kill(self, player):
        self.alivePlayers.remove(player)
        self.deadPlayers.append(player)
        player.die()

    def checkWin(self):
        mafiosoCount = 0
        villagerCount = 0
        for player in self.alivePlayers:
            if player.role == Roles.MAFIOSO:
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