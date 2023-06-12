from mafia_model import MafiaGame


def playMafia(villagers=10, mafiosi=3, mafia_strategy='random'):
    game = MafiaGame(villagers, mafiosi)
    votes = None

    while len(game.alivePlayers) > 2:
        for player in game.alivePlayers:
            player.print_state()

        # Perform a round of night phase
        if len(game.alivePlayers) == villagers + mafiosi:
            # In the first round, always kill randomly a villager during the night phase
            villager = game.voteVillager(mafia_strategy='random')
        else:
            # In the rest rounds, follow a certain strategy
            villager = game.voteVillager(mafia_strategy=mafia_strategy, votes=votes)

        # Kill the villager and update the model
        game.kill(villager)
        print(f"{villager.name} was killed during the night phase!\n")

        # Perform a round of day phase
        voteCount = {}
        votes = {}
        for player in game.alivePlayers:
            # Open vote for the player to be eliminated
            vote = player.vote()
            print(f"{player.name} votes to eliminate {vote.name}")
            if vote in voteCount:
                voteCount[vote] += 1
            else:
                voteCount[vote] = 1

            if vote.role.name == 'MAFIOSO':
                # Keep track of the votes against true Mafia members
                player.suspectMafioso(player, vote)
                votes[player] = 1
            else:
                votes[player] = 0

        # Find the player with the majority of votes to be eliminated during the day phase
        maxVote = 0
        maxPlayer = None
        for player in voteCount:
            if voteCount[player] > maxVote:
                maxVote = voteCount[player]
                maxPlayer = player
        print(f"{maxPlayer.name} is eliminated!\n")
        # Kill the player and update the model
        game.kill(maxPlayer)

        for player in game.players:
            print(f"{player.name} correctly suspects {player.accusations}")

        if maxPlayer.role.name == 'MAFIOSO':
            # Update players' beliefs if a Mafia member is eliminated
            for player in game.players:
                if player.accusations[maxPlayer.name] >= 1:
                    print(f"{player.name} correctly suspected {maxPlayer.name}!")
                    player.updateKnowledge()

        win = game.checkWin()
        if win:
            return win

        print("---------------------------------------------------------------------------------------------------\n")

    print("Tie!")
    return "Tie"


if __name__ == '__main__':
    # window = mainWindow()
    # window.update()
    # addBoard(window)
    # window.mainloop()
    playMafia(villagers=10, mafiosi=2, mafia_strategy='enemy')
