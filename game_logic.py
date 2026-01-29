"""
Tic-Tac-Toe Game Logic
Simple, flat implementation for multi-player game
"""

SYMBOLS = ['X', 'O', '△', '𝄞', '✿', '♕', '♖', '☀︎', '♥', '♣', '♦', '♠', '♫']

class Player:
    """Represents a player in the game"""
    def __init__(self, conn, addr, symbol):
        self.conn = conn
        self.addr = addr
        self.symbol = symbol
    
    def __repr__(self):
        return f"Player({self.symbol}, {self.addr})"


class Game:
    """
    Tic-Tac-Toe game logic
    Board size = num_players + 1
    Win condition: 3 in a row
    """
    
    def __init__(self, game_id, num_players):
        """Initialize a new game"""
        if num_players < 2 or num_players > 13:
            raise ValueError("Number of players must be between 2 and 13")
        
        self.game_id = game_id
        self.num_players = num_players
        self.players = []  # List of Player objects
        self.board_size = num_players + 1
        self.board = [['.' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_turn = 0  # Index in players list
        self.started = False
        self.ended = False
        self.winner = None
        self.move_count = 0
        self.available_symbols = SYMBOLS[:]

    
    def is_full(self):
        """Check if game is full"""
        return len(self.players) >= self.num_players
    
    def is_waiting(self):
        """Check if waiting for players"""
        return not self.started
    
    def add_player(self, conn, addr):
        """
        Add a player to the game
        Returns: (success, symbol or error_message)
        """
        if self.started:
            return False, "Game already started"
        
        if self.is_full():
            return False, "Game is full"
        
        # Assign symbol
        if not self.available_symbols:
            return False, "No symbols available"

        symbol = self.available_symbols.pop(0)
        player = Player(conn, addr, symbol)
        self.players.append(player)
        
        # Start game if all players joined
        if len(self.players) == self.num_players:
            self.started = True
        
        return True, symbol
    
    def get_current_player(self):
        """Get the player whose turn it is"""
        if not self.started or self.ended:
            return None
        return self.players[self.current_turn]
    
    def is_player_turn(self, conn):
        """Check if it's this connection's turn"""
        current = self.get_current_player()
        return current is not None and current.conn == conn
    
    def make_move(self, conn, row, col):
        """
        Execute a move
        Returns: (status, message)
        status can be: "success", "invalid", "win", "draw"
        """
        if self.ended:
            return "invalid", "Game already ended"
        
        if not self.is_player_turn(conn):
            return "invalid", "Not your turn"
        
        # Validate move
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return "invalid", "Out of bounds"
        
        if self.board[row][col] != '.':
            return "invalid", "Cell already occupied"
        
        # Execute move
        current_player = self.get_current_player()
        self.board[row][col] = current_player.symbol
        self.move_count += 1
        
        # Check for win
        if self.check_win(current_player.symbol):
            self.ended = True
            self.winner = current_player
            return "win", current_player.symbol
        
        # Check for draw
        if self.move_count == self.board_size * self.board_size:
            self.ended = True
            return "draw", None
        
        # Move to next player
        self.current_turn = (self.current_turn + 1) % len(self.players)
        
        return "success", None
    
    def check_win(self, symbol):
        """
        Check if symbol has won (3 in a row)
        """
        # Check rows
        for row in range(self.board_size):
            for col in range(self.board_size - 2):
                if (self.board[row][col] == symbol and
                    self.board[row][col + 1] == symbol and
                    self.board[row][col + 2] == symbol):
                    return True
        
        # Check columns
        for col in range(self.board_size):
            for row in range(self.board_size - 2):
                if (self.board[row][col] == symbol and
                    self.board[row + 1][col] == symbol and
                    self.board[row + 2][col] == symbol):
                    return True
        
        # Check diagonals (top-left to bottom-right)
        for row in range(self.board_size - 2):
            for col in range(self.board_size - 2):
                if (self.board[row][col] == symbol and
                    self.board[row + 1][col + 1] == symbol and
                    self.board[row + 2][col + 2] == symbol):
                    return True
        
        # Check diagonals (top-right to bottom-left)
        for row in range(self.board_size - 2):
            for col in range(2, self.board_size):
                if (self.board[row][col] == symbol and
                    self.board[row + 1][col - 1] == symbol and
                    self.board[row + 2][col - 2] == symbol):
                    return True
        
        return False
    
    def get_board_string(self):
        """
        Get board as string for transmission
        Format:
        BOARD
        X O .
        . X .
        . . O
        """
        lines = ["BOARD"]
        for row in self.board:
            lines.append(" ".join(row))
        return "\n".join(lines)
    
    def get_player_by_conn(self, conn):
        """Get player by connection"""
        for player in self.players:
            if player.conn == conn:
                return player
        return None

    def remove_player(self, conn):
        player = self.get_player_by_conn(conn)
        if not player:
            return None

        self.players.remove(player)
        self.available_symbols.append(player.symbol)

        if len(self.players) == 0:
            self.ended = True
            return "abort"
        # Adjust current turn index
        if self.started and not self.ended:
            if len(self.players) <= 1:
                self.ended = True
                return "abort"

            # update current turn index if necessary
            if self.current_turn >= len(self.players):
                self.current_turn = 0

        return player.symbol

