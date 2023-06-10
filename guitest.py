import tkinter as tk
from tkinter import messagebox
from enum import Enum
import random
import networkx as nx
import matplotlib.pyplot as plt

import tkinter.scrolledtext as st
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class KripkeModel:
    def __init__(self, game):
        self.game = game
        self.G = nx.DiGraph()

    def build_model(self):
        for player in self.game.players:
            for belief in player.playerBeliefs:
                for role in belief[1]:
                    self.G.add_edge(player.name, f"{belief[0].name}_{role}")

    def draw_model(self, iter):
        pos = nx.spring_layout(self.G)
        plt.figure(figsize=(8, 6))
        nx.draw_networkx(self.G, pos, arrows=True, with_labels=True, node_size=1000, alpha=0.3, font_weight='bold')
        plt.title("Kripke Model")
        plt.savefig("./model_graph/kripke_" + str(iter) + ".png")

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

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Mafia Game")

        # Start button
        self.start_button = tk.Button(self, text="Start Game", command=self.start_game)
        self.start_button.pack()

        # Game log text box
        self.game_log = st.ScrolledText(self, width=80, height=20)
        self.game_log.pack()

        # Initialize figure and canvas
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack()

        # Players list
        self.players_label = tk.Label(self, text="")
        self.players_label.pack()

    def start_game(self):
        # self.game = MafiaGame(villagers=7, mafiosi=2, detectives=1, doctors=1)
        self.game = MafiaGame(villagers=7, mafiosi=2, detectives=1, doctors=1)
        self.model = KripkeModel(self.game)
        self.play_mafia_single_round()

    def play_mafia_single_round(self, iter=0):
        self.game_log.insert('end', f"\n\n=== Round {iter} ===\n\n")

        for player in self.game.alivePlayers:
            player_status = f"{player.name} (Role: {player.role.name})\n"
            self.game_log.insert('end', player_status)

        # Daytime
        voteCount = {}
        for player in self.game.alivePlayers:
            if isinstance(player, Detective):
                investigated = player.investigate()
                print(f"{player.name} investigates {investigated.name}")
            elif isinstance(player, Doctor):
                protected = player.protect()
                print(f"{player.name} protects {protected.name}")
            vote = player.vote()
            print(f"{player.name} votes to eliminate {vote.name}")
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
            print(f"{maxPlayer.name} is eliminated!\n")
            self.game.kill(maxPlayer)
        else:
            print("No one is eliminated this round.\n")

        self.model.build_model()
        self.model.draw_model(iter)
        self.figure.clear()
        pos = nx.spring_layout(self.model.G, scale=2)
        nx.draw_networkx(self.model.G, pos, ax=self.figure.add_subplot(111))
        self.canvas.draw()

        win = self.game.checkWin()
        if win:
            messagebox.showinfo("Game Over", f"{win} win!")
            return
        elif len(self.game.alivePlayers) <= 2:
            messagebox.showinfo("Game Over", "Tie!")
            return
        else:
            self.after(500, self.play_mafia_single_round, iter + 1)

if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()