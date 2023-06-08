from mafia_model import MafiaGame


def playMafia(villagers=10, mafiosi=3):
    game = MafiaGame(villagers, mafiosi)

    while len(game.alivePlayers) > 2:
        for player in game.alivePlayers:
            player.print_state()
        # Daytime
        voteCount = {}
        for player in game.alivePlayers:
            vote = player.vote()

            if vote.role.name == 'MAFIOSO':
                player.suspectMafioso(player, vote)

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

        for player in game.players:
            print(f"{player.name} correctly suspects {player.accusations}")

        # Update alive players' beliefs if a Mafia member is eliminated
        if maxPlayer.role.name == 'MAFIOSO':
            for player in game.players:
                if player.accusations[maxPlayer.name] > 0:
                    print(f"{player.name} correctly suspected {maxPlayer.name}!")
                    player.updateKnowledge()

        win = game.checkWin()
        if win:
            return win

        print("-----------------------------------------------------------------------------------------------------")

    print("Tie!")
    return "Tie"


if __name__ == '__main__':
    # window = mainWindow()
    # window.update()
    # addBoard(window)
    # window.mainloop()
    playMafia(villagers=10, mafiosi=3)