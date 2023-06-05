# This program was created with the help of Github Copilot

import tkinter as tk
from enum import Enum
import random

def testTK():
    print("before!")
    window = tk.Tk()
    window.title("Test for tkinter")
    greeting = tk.Label(text="TEST2")
    button = tk.Button(window, text="This is a button!")
    greeting.pack()
    button.pack()
    print("after!")
    window.mainloop()


def mainWindow():
    window = tk.Tk()
    window.title("Test for tkinter")
    window.geometry("1920x1080")
    return window


def addBoard(window, color1 = 'black', color2 = 'white'):
    board = tk.Canvas(window, width=1920, height=1080, bd=0, bg='red')
    x = 0
    y = 0
    horCount = window.winfo_width()//20
    verCount = window.winfo_height()//20
    horSize = window.winfo_width() // horCount
    print(horSize)
    verSize = window.winfo_height() // verCount
    while (x < horCount*horSize):
        color = color1
        if x % (2 * horSize):
            color = color2
        while(y < verCount*verSize):
            board.create_rectangle(x, y, x+horSize, y+verSize, fill=color)
            if color == color1:
                color = color2
            else:
                color = color1
            y += verSize
        y = 0
        x += horSize
    board.pack()


class Roles(Enum):
    VILLAGER = 0
    MAFIOSO = 1


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
                self.playerBeliefs.append((player, [self.role.name]))
            else:
                self.playerBeliefs.append((player, [role.name for role in Roles]))
    
    def vote(self):
        candidates = [belief[0] for belief in self.playerBeliefs if (belief[0] in self.alivePlayers and "MAFIOSO" in belief[1])]
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
        # Vote for a random villager who is not in the mafia
        return random.choice(candidates)


class MafiaGame:
    def __init__(self, villagers = 10, mafiosi = 3):
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

def playMafia(villagers = 10, mafiosi = 3):
    game = MafiaGame(villagers, mafiosi)
    while len(game.alivePlayers) > 2:
        for player in game.alivePlayers:
            player.print_state()
        # Daytime
        voteCount = {}
        for player in game.alivePlayers:
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
        print(f"{maxPlayer.name} is eliminated!\n")
        game.kill(maxPlayer)
        win = game.checkWin()
        if win:
            return win
    print("Tie!")
    return "Tie"

if __name__ == '__main__':
    #window = mainWindow()
    #window.update()
    #addBoard(window)
    #window.mainloop()
    playMafia(villagers = 10, mafiosi = 2)
    