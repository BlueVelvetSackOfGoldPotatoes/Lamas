import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import messagebox

import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from kripke_model import KripkeModel
from mafia_model import MafiaGame


class MainWindow(tk.Tk):
<<<<<<< HEAD
    def __init__(self, villagers=7, mafiosi=2, doctors=0, informants=0, mafia_strategy='enemy'):
=======
    def __init__(self, villagers=10, mafiosi=2, doctors=1, informants=1,
                 mafia_strategy='enemy', informant_strategy='random',
                 doctors_strategy='deterministic', num_protectedPlayers=1):
>>>>>>> strategies
        super().__init__()
        self.villagers = villagers
        self.mafiosi = mafiosi
        self.doctors = doctors
        self.informants = informants
        self.mafia_strategy = mafia_strategy
        self.informant_strategy = informant_strategy
        self.doctors_strategy = doctors_strategy
        self.num_protectedPlayers = num_protectedPlayers
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
<<<<<<< HEAD
        self.game = MafiaGame(villagers=self.villagers, mafiosi=self.mafiosi, doctors=self.doctors, informants=self.informants)
=======
        self.game = MafiaGame(villagers=self.villagers, mafiosi=self.mafiosi, doctors=self.doctors,
                              informants=self.informants)
>>>>>>> strategies
        self.totalPlayers = len(self.game.players)
        self.model = KripkeModel(self.game)
        for player in self.game.players:
            player.kripke_model = self.model  # Pass the Kripke model to the players
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
            # In the rest rounds, follow a certain strategy to kill
            villager = self.game.voteVillager(mafia_strategy=self.mafia_strategy, votes=self.votes)

        # Choose a player to protect after the night phase
        protected = self.game.choose_protected_player()
        # Check whether the player that was killed will be indeed saved
        if 'DOCTOR' in [player.role.name for player in self.game.alivePlayers] and villager == protected:
            if self.game.protectedID_is_known(protected):
                print(f"{villager.name} was saved by the Doctor(s) after the night phase, but it is already common "
                      f"knowledge that he is innocent!\n")
            else:
                self.game.savePlayer(protected)
                print(f"{villager.name} was saved by the Doctor(s) after the night phase!\n")
        else:
            # Either the Doctor is not active, or the protected player is not the one that was killed
            # Kill the innocent player and update the model
            self.game.kill(villager)
            print(f"{villager.name} was killed during the night phase!\n")

        if 'DOCTOR' in [player.role.name for player in self.game.alivePlayers]:
            # For this round, decide whether Doctor(s) will let the rest players know about their identity and knowledge
            self.game.apply_doctors_strategy(doctors_strategy=self.doctors_strategy,
                                             num_protectedPLayers=self.num_protectedPlayers)

        # The mafiosi might win the game by killing a villager at night
        win = self.game.checkWin()
        if win:
            messagebox.showinfo("Game Over", f"{win} win!")
            return
        elif len(self.game.alivePlayers) <= 2:
            messagebox.showinfo("Game Over", "Tie!")
            return
        
        # Update player beliefs..
        #for player in self.game.alivePlayers:
            #player.updateBeliefs(villager)

        # Check whether the Informant will reveal the identity of the one known mafia member
        if not self.game.revealedMafioso:
            self.game.apply_informant_strategy(informant_strategy=self.informant_strategy)

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
        
        #for player in self.game.alivePlayers:
            #player.updateBeliefs(maxPlayer)

        self.model.build_model()
        self.model.draw_model(iteration)
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
<<<<<<< HEAD
    app = MainWindow(villagers=6 , mafiosi=2, doctors=1, informants=1, mafia_strategy='enemy')
    app.mainloop()
=======
    """ mafia_strategy = {enemy, allied, random}
        informant_strategy = {deterministic, random} 
        doctors_strategy = {deterministic, random} """

    app = MainWindow(villagers=7, mafiosi=2, doctors=2, informants=1,
                     mafia_strategy='enemy', informant_strategy='random',
                     doctors_strategy='deterministic', num_protectedPlayers=1)
    app.mainloop()
>>>>>>> strategies
