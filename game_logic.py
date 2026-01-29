"""
Tic-Tac-Toe Game Logic
flat implementation for a multi-player game
"""

# List of symbols assigned to players (supports up to 13 players)
SYMBOLS = ['X', 'O', '△', '𝄞', '✿', '♕', '♖', '☀︎', '♥', '♣', '♦', '♠', '♫']

class Player:
    """
    Represents a single player in the game.
    Holds the socket connection, address, and assigned symbol.
    """
    def __init__(self, conn, addr, symbol):
        self.conn = conn      # Client socket connection
        self.addr = addr      # Client address (IP, port)
        self.symbol = symbol  # Player's symbol on the board
    
    def __repr__(self):
        return f"Player({self.symbol}, {self.addr})"

class Game:
    """
    Tic-Tac-Toe game logic class.
    
    Board size = number of players + 1
    Win condition: 3 identical symbols in a row (row / column / diagonal)
    """
    
    def __init__(self, game_id, num_players):
        """
        Initialize a new game instance.
        
        Args:
            game_id: Unique identifier of the game
            num_players: Number of players in the game (2-13)
        """
        if num_players < 2 or num_players > 13:
            raise ValueError("Number of players must be between 2 and 13")
        
        self.game_id = game_id
        self.num_players = num_players
        self.players = []  # List of Player objects
        
        # Board size is players + 1
        self.board_size = num_players + 1
        
        # Initialize empty board ('.' means empty cell)
        self.board = [['.' for _ in range(self.board_size)]
                      for _ in range(self.board_size)]
        
        self.current_turn = 0     # Index of current player in players list
        self.started = False      # True once all players joined
        self.ended = False        # True when game ends
        self.winner = None        # Winning Player object
        self.move_count = 0       # Total number of moves played
        
        # Available symbols pool
        self.available_symbols = SYMBOLS[:]
    
    def is_full(self):
        """Return True if the game already has all required players"""
        return len(self.players) >= self.num_players
    
    def is_waiting(self):
        """Return True if the game has not started yet"""
        return not self.started
    
    def add_player(self, conn, addr):
        """
        Add a new player to the game.
        
        Returns:
            (True, symbol) on success
            (False, error_message) on failure
        """
        if self.started:
            return False, "Game already started"
        
        if self.is_full():
            return False, "Game is full"
        
        # Assign next available symbol
        if not self.available_symbols:
            return False, "No symbols available"

        symbol = self.available_symbols.pop(0)
        player = Player(conn, addr, symbol)
        self.players.append(player)
        
        # Start the game when all players have joined
        if len(self.players) == self.num_players:
            self.started = True
        
        return True, symbol
    
    def get_current_player(self):
        """Return the player whose turn it is"""
        if not self.started or self.ended:
            return None
        return self.players[self.current_turn]
    
    def is_player_turn(self, conn):
        """Check if the given connection belongs to the current player"""
        current = self.get_current_player()
        return current is not None and current.conn == conn
    
    def make_move(self, conn, row, col):
        """
        Execute a move on behalf of a player.
        
        Returns:
            (status, data)
            status can be: "success", "invalid", "win", "draw"
        """
        if self.ended:
            return "invalid", "Game already ended"
        
        if not self.is_player_turn(conn):
            return "invalid", "Not your turn"
        
        # Validate board boundaries
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return "invalid", "Out of bounds"
        
        # Validate cell is empty
        if self.board[row][col] != '.':
            return "invalid", "Cell already occupied"
        
        # Execute the move
        current_player = self.get_current_player()
        self.board[row][col] = current_player.symbol
        self.move_count += 1
        
        # Check for win condition
        if self.check_win(current_player.symbol):
            self.ended = True
            self.winner = current_player
            return "win", current_player.symbol
        
        # Check for draw (board is full)
        if self.move_count == self.board_size * self.board_size:
            self.ended = True
            return "draw", None
        
        # Advance turn to next player
        self.current_turn = (self.current_turn + 1) % len(self.players)
        
        return "success", None
    
    def check_win(self, symbol):
        """
        Check whether the given symbol has won the game
        (3 consecutive symbols in any direction)
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
        
        # Check diagonal (top-left to bottom-right)
        for row in range(self.board_size - 2):
            for col in range(self.board_size - 2):
                if (self.board[row][col] == symbol and
                    self.board[row + 1][col + 1] == symbol and
                    self.board[row + 2][col + 2] == symbol):
                    return True
        
        # Check diagonal (top-right to bottom-left)
        for row in range(self.board_size - 2):
            for col in range(2, self.board_size):
                if (self.board[row][col] == symbol and
                    self.board[row + 1][col - 1] == symbol and
                    self.board[row + 2][col - 2] == symbol):
                    return True
        
        return False
    
    def get_board_string(self):
        """
        Return the board as a string.
        """
        lines = ["BOARD"]
        for row in self.board:
            lines.append(" ".join(row))
        return "\n".join(lines)
    
    def get_player_by_conn(self, conn):
        """Return the Player object associated with the given connection"""
        for player in self.players:
            if player.conn == conn:
                return player
        return None
    
    def remove_player(self, conn):
        """
        Remove a player from the game.
        
        Returns:
            symbol of removed player
            "abort" if the game must be terminated
        """
        player = self.get_player_by_conn(conn)
        if not player:
            return None

        self.players.remove(player)
        self.available_symbols.append(player.symbol)

        # No players left → abort game
        if len(self.players) == 0:
            self.ended = True
            return "abort"

        # Adjust game state if game already started
        if self.started and not self.ended:
            if len(self.players) <= 1:
                self.ended = True
                return "abort"

            # Fix current turn index if needed
            if self.current_turn >= len(self.players):
                self.current_turn = 0

        return player.symbol