import random
from kripke_model import KripkeModel, State, Proposition, Relation, Transition
from mafia_players import Mafioso, Roles, Villager, Doctor, Informant


class MafiaGame:
    def __init__(self, villagers=10, mafiosi=3, doctors=1, informants=1):
        self.kripke_model = KripkeModel(self)
        
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
            player = Role()
            player.name = f"{player.role.name.capitalize()} {itr}"
            player.kripke_model = self.kripke_model
            self.players.append(player)

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
        
        for player in self.alivePlayers:
            player.update_beliefs(villager)

        return villager

    def kill(self, player):
        """Eliminate a player from the game."""
        self.alivePlayers.remove(player)
        self.deadPlayers.append(player)
        player.die()

        # Update player beliefs
        for alivePlayer in self.alivePlayers:
            alivePlayer.update_beliefs(player)

        # Update Kripke model after player is killed
        self.kripke_model.build_model()

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