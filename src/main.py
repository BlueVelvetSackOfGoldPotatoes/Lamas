import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QMessageBox, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

import networkx as nx

from kripke_model import KripkeModel
from mafia_model import MafiaGame

class ScrollablePlotWindow(QScrollArea):
    def __init__(self, round, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        content_widget = QWidget()
        self.setWidget(content_widget)

        self.figure = Figure(figsize=(5, 5), dpi=300)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.round = round

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"=== Round {self.round} ==="))
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        content_widget.setLayout(layout)

    def save_plot(self, filename):
        self.figure.savefig(filename, dpi=300)

    def update_plot(self, graph, game):
        player_roles = {player.name: player.role.name for player in game.players}

        pos = nx.spring_layout(graph, scale=2)

        # Clear the figure before adding a new subplot
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        for role, color in [('MAFIOSO', 'red'), ('DOCTOR', 'blue'), ('INFORMANT', 'yellow'), ('VILLAGER', 'green')]:
            nodes_of_role = [node for node in graph.nodes if player_roles.get(node, None) == role]
            nx.draw_networkx_nodes(graph, pos, nodelist=nodes_of_role, node_color=color, ax=ax, label=role)

        nx.draw_networkx_edges(graph, pos, ax=ax)
        nx.draw_networkx_labels(graph, pos, ax=ax)

        ax.legend()  # Add a legend

        ax.set_aspect("auto")
        ax.autoscale(enable=True)

        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self, villagers=10, mafiosi=2, doctors=1, informants=1, mafia_strategy='enemy'):
        super().__init__()

        self.plots = []

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

        # Create a main widget and layout for the window
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Start button
        self.start_button = QPushButton()
        self.start_button.setText("Start Game")
        self.start_button.clicked.connect(self.start_game)

        # Game log text box
        self.game_log = QTextEdit()
        self.game_log.setAlignment(Qt.AlignCenter)

        # Players list
        self.players_label = QLabel()

        # Create a widget for the plot area
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)

        # Create a scroll area for the plot area
        plot_scroll_area = QScrollArea()
        plot_scroll_area.setWidgetResizable(True)

        # Create a widget to hold the plots
        plots_widget = QWidget()
        plots_layout = QVBoxLayout(plots_widget)
        plot_scroll_area.setWidget(plots_widget)

        # Add the scroll area to the plot layout
        plot_layout.addWidget(plot_scroll_area)

        # Add widgets to the main layout
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.game_log)
        main_layout.addWidget(self.players_label)
        main_layout.addWidget(plot_widget)

        self.setCentralWidget(main_widget)

        self.plots_layout = plots_layout

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.playMafia)

    def start_game(self):
        self.game = MafiaGame(villagers=self.villagers, mafiosi=self.mafiosi, doctors=self.doctors)
        self.totalPlayers = len(self.game.players)
        self.model = KripkeModel(self.game)
        self.playMafia()

    def plot(self):
        try:
            # 1. Instantiate new figure and canvas
            figure = Figure(figsize=(5, 5), dpi=300)
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar(canvas, self)

            # 2. Update the plot using new figure
            self.update_plot(figure, self.model.G.copy(), self.game)

            # 3. Add the canvas and navigation toolbar to the plot widget
            plot_widget = QWidget()
            plot_layout = QVBoxLayout(plot_widget)
            plot_layout.addWidget(QLabel(f"=== Round {self.round} ==="))
            plot_layout.addWidget(toolbar)
            plot_layout.addWidget(canvas)

            # 4. Add the plot widget to the plots layout
            self.plots_layout.addWidget(plot_widget)

            # Optionally save the plot
            figure.savefig(f"./graphs/round_{self.round}.png", dpi=300)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            traceback.print_exc()
            return

    def update_plot(self, figure, graph, game):
        player_roles = {player.name: player.role.name for player in game.players}

        pos = nx.spring_layout(graph, scale=2)
        
        # Clear the figure before adding a new subplot
        figure.clear()

        ax = figure.add_subplot(111)
        for role, color in [('MAFIOSO', 'red'), ('DOCTOR', 'blue'), ('INFORMANT', 'yellow'), ('VILLAGER', 'green')]:
            nodes_of_role = [node for node in graph.nodes if player_roles.get(node, None) == role]
            nx.draw_networkx_nodes(graph, pos, nodelist=nodes_of_role, node_color=color, ax=ax, label=role)

        nx.draw_networkx_edges(graph, pos, ax=ax)
        nx.draw_networkx_labels(graph, pos, ax=ax)

        ax.legend()  # Add a legend

        ax.set_aspect("auto")
        ax.autoscale(enable=True)

    def playMafia(self):
        self.round += 1
        self.game_log.append(f"\n\n=== Round {self.round} ===\n\n")

        for player in self.game.alivePlayers:
            player.print_state()
            player_status = f"{player.name} (Role: {player.role.name})\n"
            self.game_log.append(player_status)
        
        win = self.game.checkWin()
        if win:
            QMessageBox.information(self, "Game Over", f"{win} win!")
            self.timer.stop()

            return

        if self.round > 1:
            self.plot()

        # Perform a round of night phase
        if len(self.game.alivePlayers) == self.totalPlayers:
            # In the first round, always kill randomly a villager during the night phase
            villager = self.game.voteVillager(mafia_strategy='random')
            if villager == None:
                QMessageBox.information(self, "Game Over", "Mafia Win!")
                self.timer.stop()
                return
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
            if player in self.game.alivePlayers:
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
        
        self.game_log.append("---------------------------------------------------------------------------------------------------\n")

        win = self.game.checkWin()
        if win:
            QMessageBox.information(self, "Game Over", f"{win} win!")
            self.timer.stop()

            return

        if self.round == 1:
            self.plot()

        self.start_timer()

    def start_timer(self):
        self.timer.start(500)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(villagers=3, mafiosi=2, informants=1, doctors=1, mafia_strategy='enemy')
    window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
    window.showMaximized()
    sys.exit(app.exec_())