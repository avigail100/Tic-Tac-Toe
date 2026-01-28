import Game

if __name__ == '__main__':
    game = Game.Game(game_id=1, players_number=2)
    print("Game created with ID:", game.game_id)
    player1 = 1
    player2 = 2
    player3 = 3
    
    game.add_player(player1)
    game.add_player(player2)
    game.add_player(player3)
    