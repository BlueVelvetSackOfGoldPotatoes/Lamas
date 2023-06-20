import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import messagebox

import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from kripke_model import KripkeModel
from mafia_model import MafiaGame




class MainWindow(tk.Tk):
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
        self.game = MafiaGame(villagers=self.villagers, mafiosi=self.mafiosi, doctors=self.doctors, informants=self.informants)
        self.totalPlayers = len(self.game.players)
        self.model = KripkeModel(self.game)
        self.playMafia()

    def playMafia(self, iteration=0):
        self.game_log.insert('end', f"\n\n=== Round {iteration} ===\n\n")

        for player in self.game.alivePlayers:
            player.print_state()
            player_status = f"{player.name} (Role: {player.role.name})\n"
            self.game_log.insert('end', player_status)

        # Perform a round of night phase
        if len(self.game.alivePlayers) == self.totalPlayers:
            # In the first round, always kill randomly a villager during the night phase
            villager = self.game.voteVillager(mafia_strategy='random')
        else:
            # In the rest rounds, follow a certain strategy
            villager = self.game.voteVillager(mafia_strategy=self.mafia_strategy, votes=self.votes)

        # If the doctor is alive, try to protect one player after the night phase
        protected = self.game.protectPlayer()
        if 'DOCTOR' in [player.role.name for player in self.game.alivePlayers] and villager == protected:
            # Check if the player to be protected was the 'villager' killed in the night phase and protect him
            print(f"{villager.name} was saved by the Doctor after the night phase!\n")
            # Update the knowledge of Doctors about this player
            for player in self.game.alivePlayers:
                if player.role.name == 'DOCTOR':
                    player.changeKnowledge(villager)
        else:
            # Either the Doctor is not alive or the protected player is not the same that was killed
            # Kill the villager and update the model
            self.game.kill(villager)
            print(f"{villager.name} was killed during the night phase!\n")

        # The mafiosi might win the game by killing a villager at night
        win = self.game.checkWin()
        if win:
            messagebox.showinfo("Game Over", f"{win} win!")
            return
        elif len(self.game.alivePlayers) <= 2:
            messagebox.showinfo("Game Over", "Tie!")
            return

        # Perform a round of day phase
        voteCount = {}
        self.votes = {}
        for player in self.game.alivePlayers:
            # Open vote for the player to be eliminated
            vote = player.vote()
            print(f"{player.name} votes to eliminate {vote.name}")
            if vote in voteCount:
                voteCount[vote] += 1
            else:
                voteCount[vote] = 1

            if vote.role.name == 'MAFIOSO':
                # Keep track of the votes against true Mafia members
                player.suspectMafioso(vote)
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
        print(f"{maxPlayer.name} is eliminated!\n")
        # Kill the player and update the model
        self.game.kill(maxPlayer)

        for player in self.game.players:
            print(f"{player.name} correctly suspects {player.accusations}")

        if maxPlayer.role.name == 'MAFIOSO':
            # Update players' beliefs if a Mafia member is eliminated
            for player in self.game.players:
                if player.accusations[maxPlayer.name] >= 1:
                    print(f"{player.name} correctly suspected {maxPlayer.name}!")
                    player.updateKnowledge()

        self.model.build_model()
        self.model.draw_model("test")
        self.figure.clear()
        pos = nx.spring_layout(self.model.G, scale=2)
        nx.draw_networkx(self.model.G, pos, ax=self.figure.add_subplot(111))
        self.canvas.draw()

        win = self.game.checkWin()
        print("---------------------------------------------------------------------------------------------------\n")

        if win:
            messagebox.showinfo("Game Over", f"{win} win!")
            return
        else:
            self.after(500, self.playMafia, iteration + 1)


if __name__ == '__main__':
    app = MainWindow(villagers=10, mafiosi=2, doctors=2, informants=0, mafia_strategy='enemy')
    app.mainloop()
