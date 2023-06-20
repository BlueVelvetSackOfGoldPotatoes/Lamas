import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QMessageBox, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

import networkx as nx

from kripke_model import KripkeModel
from mafia_model import MafiaGame

class ScrollablePlotWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def update_plot(self, graph):
        self.figure.clear()
        pos = nx.spring_layout(graph, scale=2)
        nx.draw_networkx(graph, pos, ax=self.figure.add_subplot(111))

        ax = self.figure.gca()
        ax.set_aspect("auto")
        ax.autoscale(enable=True)

        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self, villagers=10, mafiosi=2, doctors=1, informants=1, mafia_strategy='enemy'):
        super().__init__()
        self.villagers = villagers
        self.mafiosi = mafiosi
        self.doctors = doctors
        self.informants = informants
        self.mafia_strategy = mafia_strategy
        self.game = None
        self.model = None
        self.votes = None
        self.totalPlayers = 0
        self.round = 0

        self.setGeometry(500, 500, 500, 300)
        self.setWindowTitle("Mafia Game")

        # Start button
        self.start_button = QPushButton(self)
        self.start_button.setText("Start Game")
        self.start_button.clicked.connect(self.start_game)
        self.start_button.move(10, 10)

        # Game log text box
        self.game_log = QTextEdit(self)
        self.game_log.setGeometry(500, 50, 1000, 500)
        self.game_log.setAlignment(Qt.AlignCenter)

        # Scrollable plot window
        self.scrollable_plot_window = ScrollablePlotWindow(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(500, 500, 1000, 500)
        self.scroll_area.setWidget(self.scrollable_plot_window)

        # Players list
        self.players_label = QLabel(self)
        self.players_label.setGeometry(10, 600, 780, 30)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.playMafia)

    def start_game(self):
        self.game = MafiaGame(villagers=self.villagers, mafiosi=self.mafiosi, doctors=self.doctors)
        self.totalPlayers = len(self.game.players)
        self.model = KripkeModel(self.game)
        self.playMafia()

    def playMafia(self):
        self.round += 1
        self.game_log.append(f"\n\n=== Round {self.round} ===\n\n")

        for player in self.game.alivePlayers:
            player.print_state()
            player_status = f"{player.name} (Role: {player.role.name})\n"
            self.game_log.append(player_status)

        # Perform a round of night phase
        if len(self.game.alivePlayers) == self.totalPlayers:
            # In the first round, always kill randomly a villager during the night phase
            villager = self.game.voteVillager(mafia_strategy='random')
        else:
            # In the rest of the rounds, follow a certain strategy
            villager = self.game.voteVillager(mafia_strategy=self.mafia_strategy, votes=self.votes)

        # Kill the villager and update the model
        self.game.kill(villager)
        self.game_log.append(f"{villager.name} was killed during the night phase!\n")

        # The mafiosi might win the game by killing a villager at night
        win = self.game.checkWin()
        if win:
            QMessageBox.information(self, "Game Over", f"{win} win!")
            self.timer.stop()
            return
        elif len(self.game.alivePlayers) <= 2:
            QMessageBox.information(self, "Game Over", "Tie!")
            self.timer.stop()
            return

        # Perform a round of day phase
        voteCount = {}
        self.votes = {}
        for player in self.game.alivePlayers:
            # Open vote for the player to be eliminated
            vote = player.vote()
            self.game_log.append(f"{player.name} votes to eliminate {vote.name}")
            if vote in voteCount:
                voteCount[vote] += 1
            else:
                voteCount[vote] = 1

            if vote.role.name == 'MAFIOSO':
                # Keep track of the votes against true Mafia members
                player.suspectMafioso(player, vote)
                self.votes[player] = 1
            else:
                self.votes[player] = 0

        # Find the player with the majority of votes to be eliminated during the day phase
        maxVote = 0
        maxPlayer = None
        for player in voteCount:
            if voteCount[player] > maxVote:
                maxVote = voteCount[player]
                maxPlayer = player
        self.game_log.append(f"{maxPlayer.name} is eliminated!\n")
        # Kill the player and update the model
        self.game.kill(maxPlayer)

        for player in self.game.players:
            self.game_log.append(f"{player.name} correctly suspects {player.accusations}")

        if maxPlayer.role.name == 'MAFIOSO':
            # Update players' beliefs if a Mafia member is eliminated
            for player in self.game.players:
                if player.accusations[maxPlayer.name] >= 1:
                    self.game_log.append(f"{player.name} correctly suspected {maxPlayer.name}!")
                    player.updateKnowledge()

        self.model.build_model()
        self.scrollable_plot_window.update_plot(self.model.G.copy())  # Create a copy of the graph
        self.game_log.append("---------------------------------------------------------------------------------------------------\n")

        win = self.game.checkWin()
        if win:
            QMessageBox.information(self, "Game Over", f"{win} win!")
            self.timer.stop()
            return

        self.start_timer()

    def start_timer(self):
        self.timer.start(500)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(villagers=10, mafiosi=2, doctors=0, mafia_strategy='enemy')
    window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
    window.showMaximized()
    sys.exit(app.exec_())