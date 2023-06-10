import sys
import random
from enum import Enum

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QTextEdit, QMainWindow, QMessageBox, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QDir, QFileInfo, QTimer

import networkx as nx
from pyvis.network import Network

class KripkeModel:
    def __init__(self, game):
        self.game = game
        self.G = nx.DiGraph()
        self.net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    def build_model(self):
        for player in self.game.players:
            for belief in player.playerBeliefs:
                for role in belief[1]:
                    self.G.add_edge(player.name, f"{belief[0].name}_{role}")

    def draw_model(self, iter):
        self.net.from_nx(self.G)
        file_path = QFileInfo(QDir.tempPath() + f"/kripke_{iter}.html").absoluteFilePath()
        self.net.show(file_path)
        return file_path

class Roles(Enum):
    VILLAGER = 5
    MAFIOSO = 2
    DETECTIVE = 2
    DOCTOR = 3

class Player:
    def __init__(self, name = "Player"):
        self.role = None
        self.alivePlayers = []
        self.deadPlayers = []
        self.playerBeliefs = [] # List of tuples (player, list of beliefs)
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
                self.playerBeliefs.append([player, [self.role.name]])
            else:
                self.playerBeliefs.append([player, [role.name for role in Roles]])
    
    def vote(self):
        candidates = [belief[0] for belief in self.playerBeliefs if (belief[0] in self.alivePlayers and "MAFIOSO" in belief[1])]

        # Check if there are valid candidates to vote for
        if not candidates:
            return None

        # Vote for a random possible mafioso
        return random.choice(candidates)
    
    def die(self):
        for player in self.alivePlayers:
            for belief in player.playerBeliefs:
                if belief[0] == self:
                    for role in Roles:
                        if role.name in belief[1] and role != self.role:
                            belief[1].remove(role.name)
class Villager(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.VILLAGER

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
        candidates = [belief[0] for belief in self.playerBeliefs if (belief[0] in self.alivePlayers and "MAFIOSO" not in belief[1])]
        
        # Check if there are valid candidates to vote for
        if not candidates:
            return None

        # Vote for a random villager who is not in the mafia
        return random.choice(candidates)

class Detective(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.DETECTIVE

    def investigate(self):
        candidates = [player for player in self.alivePlayers if player != self]
        investigated = random.choice(candidates)
        for belief in self.playerBeliefs:
            if belief[0] == investigated:
                belief[1] = [investigated.role.name]
        return investigated

class Doctor(Player):
    def __init__(self):
        super().__init__()
        self.role = Roles.DOCTOR

    def protect(self):
        candidates = [player for player in self.alivePlayers if player != self]
        protected = random.choice(candidates)
        return protected

class MafiaGame:
    def __init__(self, villagers=7, mafiosi=2, detectives=1, doctors=1):
        self.players = []
        for itr in range(mafiosi):
            self.players.append(Mafioso())
            self.players[-1].name = "Mafioso " + str(itr)
        for itr in range(villagers):
            self.players.append(Villager())
            self.players[-1].name = "Villager " + str(itr)
        for itr in range(detectives):
            self.players.append(Detective())
            self.players[-1].name = "Detective " + str(itr)
        for itr in range(doctors):
            self.players.append(Doctor())
            self.players[-1].name = "Doctor " + str(itr)
        self.alivePlayers = self.players
        self.deadPlayers = []
        for player in self.players:
            player.alivePlayers = self.alivePlayers
            player.initializeBeliefs()

    def kill(self, player):
        if player not in self.alivePlayers:
            print(f"{player.name} is already dead!")
            return
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Mafia Game")

        # Create a QWebEngineView
        self.browser = QWebEngineView()

        # Create other widgets
        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.start_game)

        self.game_log = QTextEdit()
        self.game_log.setReadOnly(True)

        # Create layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.game_log)
        self.layout.addWidget(self.browser)

        # Set the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def start_game(self):
        self.game = MafiaGame(villagers=7, mafiosi=2, detectives=1, doctors=1)
        self.model = KripkeModel(self.game)
        self.play_mafia_single_round()

    def play_mafia_single_round(self, iter=0):
        self.game_log.append(f"\n\n=== Round {iter} ===\n\n")

        for player in self.game.alivePlayers:
            player_status = f"{player.name} (Role: {player.role.name})\n"
            self.game_log.append(player_status)

        # Daytime
        voteCount = {}
        for player in self.game.alivePlayers:
            if isinstance(player, Detective):
                investigated = player.investigate()
                self.game_log.append(f"{player.name} investigates {investigated.name}")
            elif isinstance(player, Doctor):
                protected = player.protect()
                self.game_log.append(f"{player.name} protects {protected.name}")
            vote = player.vote()
            self.game_log.append(f"{player.name} votes to eliminate {vote.name}")
            if vote in voteCount:
                voteCount[vote] += 1
            else:
                voteCount[vote] = 1
        maxVote = 0
        maxPlayer = None
        for player in voteCount:
            if voteCount[player] > maxVote:
                maxVote = voteCount[player]
                maxPlayer = player

        if maxPlayer is not None:
            self.game_log.append(f"{maxPlayer.name} is eliminated!\n")
            self.game.kill(maxPlayer)
        else:
            self.game_log.append("No one is eliminated this round.\n")

        self.model.build_model()
        html_file = self.model.draw_model(iter)
        self.browser.load(QUrl.fromLocalFile(html_file))

        win = self.game.checkWin()
        if win:
            QMessageBox.information(self, "Game Over", f"{win} win!")
            return
        elif len(self.game.alivePlayers) <= 2:
            QMessageBox.information(self, "Game Over", "Tie!")
            return
        else:
            QTimer.singleShot(500, lambda: self.play_mafia_single_round(iter + 1))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())