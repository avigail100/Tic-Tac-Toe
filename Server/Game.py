SYMBOLS = ['X', 'O', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
class Game:
    
    def __init__(self, game_id, players_number):
        self.game_id = game_id
        self.waiting = True # True if waiting for players to join. False if game started.
        self.players = {}
        self.board_size = players_number + 1
        self.board = [['available' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_turn = 0 # Index of the player whose turn it is
        self.ended = False
    
    def add_player(self, player):
        self.players[player] = SYMBOLS[len(self.players)]
        if len(self.players) == self.board_size - 1: # All players have joined - start the game
            # self.waiting = False
            self.waiting = False
        return (self.game_id, SYMBOLS[len(self.players) - 1]) # Return the symbol assigned to the player
    
    def start(self):
        current_player = self.players[self.current_turn] 
        return (current_player) # Return the player whose turn it is
                   
    def play(self, move):
        row, col = move
        if not self.invalid_move(row, col):
            self.board[row][col] = self.players[self.current_turn].symbol # Update the board with the player's move
            if self.is_a_win():
                winner = self.players[self.current_turn]
                self.ended = True
                return "win", winner
            if all(self.board[i][j] != 'available' for i in range(self.board_size) for j in range(self.board_size)): # Check for draw
                self.ended = True
                return "draw", None # Game ended with no winner
            self.current_turn = (self.current_turn + 1) % len(self.players) # Move to the next player's turn
        else:
            return "invalid", self.invalid_move(row, col)
        current_player = self.players[self.current_turn] 
        return (current_player) # Return the player whose turn it is
    
    def invalid_move(self, row, col):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return "out_of_bounds"
        if self.board[row][col] != 'available':
            return "cell_occupied"
        return False
    
    # Check if the board contains a sequence of 3 symbols in a row, column, or diagonal for the current player
    def is_a_win(self):
        symbol = self.players[self.current_turn].symbol
        # Check rows
        for row in self.board:
            for i in range(self.board_size - 2):
                if row[i] == row[i + 1] == row[i + 2] == symbol:
                    return True
        # Check columns
        for col in range(self.board_size):
            for i in range(self.board_size - 2):
                if self.board[i][col] == self.board[i + 1][col] == self.board[i + 2][col] == symbol:
                    return True
        # Check diagonals
        for i in range(self.board_size - 2):
            for j in range(self.board_size - 2):
                if self.board[i][j] == self.board[i + 1][j + 1] == self.board[i + 2][j + 2] == symbol:
                    return True
                if self.board[i][j + 2] == self.board[i + 1][j + 1] == self.board[i + 2][j] == symbol:
                    return True
        return False
    def print_board(self):
        for row in self.board:
            print(' | '.join(cell if cell != 'available' else ' ' for cell in row))
            print('-' * (self.board_size * 4 - 3))
    
if __name__ == '__main__':
    game = Game(game_id=1, players_number=3)
    print("Game created with ID:", game.game_id)
    player1 = 1
    player2 = 2
    player3 = 3
    
    players = {player1: game.add_player(player1), player2: game.add_player(player2), player3: game.add_player(player3)}
    
    print("Players added:", players)
    # while game.waiting:
    #     add players
    print("Game started!")
    
    cur_turn = game.start()
    game.print_board()
    while not game.ended:
        print("Current turn:", cur_turn)
        move = input()
        row, col = map(int, move.split()) 
        cur_turn = game.play((row, col))
        game.print_board()
    print("Game ended!")
        
        