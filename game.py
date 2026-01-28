"""
Tic-Tac-Toe Game Logic Module
Handles game state, player management, and win detection for multi-player games
"""

SYMBOLS = ['X', 'O', '△', '𝄞', '✿', '♕', '♖', '☀︎', '♥', '♣', '♦', '♠', '♫']


class Player:
    """Represents a player in the game"""
    
    def __init__(self, player_id, symbol):
        self.player_id = player_id
        self.symbol = symbol
    
    def __str__(self):
        return f"Player {self.player_id} ({self.symbol})"
    
    def __repr__(self):
        return self.__str__()


class Game:
    """
    Multi-player Tic-Tac-Toe game with dynamic board size.
    Board size = number_of_players + 1
    Win condition: 3 in a row (horizontal, vertical, or diagonal)
    """
    
    def __init__(self, game_id, num_players):
        """
        Initialize a new game
        
        Args:
            game_id: Unique identifier for the game
            num_players: Number of players (2-9)
        """
        if num_players < 2 or num_players > 13:
            raise ValueError("Number of players must be between 2 and 13")
        
        self.game_id = game_id
        self.num_players = num_players
        self.waiting = True  # True if waiting for players to join
        self.players = []  # List of Player objects in turn order
        self.board_size = num_players + 1
        self.board = [['.' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_turn_index = 0  # Index in players list
        self.ended = False
        self.winner = None
        self.move_count = 0
    
    def add_player(self, player_id):
        """
        Add a player to the game
        
        Args:
            player_id: Unique identifier for the player
            
        Returns:
            tuple: (success: bool, symbol: str or error_message: str)
        """
        if not self.waiting:
            return False, "Game already started"
        
        if len(self.players) >= self.num_players:
            return False, "Game is full"
        
        # Check if player already joined
        if any(p.player_id == player_id for p in self.players):
            return False, "Player already in game"
        
        symbol = SYMBOLS[len(self.players)]
        player = Player(player_id, symbol)
        self.players.append(player)
        
        # Start game if all players joined
        if len(self.players) == self.num_players:
            self.waiting = False
        
        return True, symbol
    
    def get_current_player(self):
        """
        Get the player whose turn it is
        
        Returns:
            Player object or None if game hasn't started
        """
        if self.waiting or self.ended or not self.players:
            return None
        return self.players[self.current_turn_index]
    
    def play_move(self, player_id, row, col):
        """
        Execute a player's move
        
        Args:
            player_id: ID of the player making the move
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            tuple: (status: str, data: dict)
            Status can be: "success", "invalid_turn", "invalid_move", "win", "draw"
        """
        if self.waiting:
            return "error", {"message": "Game hasn't started yet"}
        
        if self.ended:
            return "error", {"message": "Game already ended"}
        
        # Verify it's this player's turn
        current_player = self.get_current_player()
        if current_player.player_id != player_id:
            return "invalid_turn", {
                "message": f"Not your turn. Current player: {current_player.symbol}",
                "current_player": current_player.symbol
            }
        
        # Validate move
        error = self._validate_move(row, col)
        if error:
            return "invalid_move", {"message": error}
        
        # Execute move
        self.board[row][col] = current_player.symbol
        self.move_count += 1
        
        # Check for win
        if self._check_win(current_player.symbol):
            self.ended = True
            self.winner = current_player
            return "win", {
                "winner": current_player.symbol,
                "winner_id": current_player.player_id,
                "board": self.get_board_state()
            }
        
        # Check for draw
        if self.move_count == self.board_size * self.board_size:
            self.ended = True
            return "draw", {
                "message": "Game ended in a draw",
                "board": self.get_board_state()
            }
        
        # Move to next player
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
        
        return "success", {
            "board": self.get_board_state(),
            "next_player": self.get_current_player().symbol
        }
    
    def _validate_move(self, row, col):
        """
        Validate if a move is legal
        
        Returns:
            str: Error message if invalid, None if valid
        """
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return f"Move out of bounds. Board size is {self.board_size}x{self.board_size}"
        
        if self.board[row][col] != '.':
            return f"Cell ({row},{col}) is already occupied"
        
        return None
    
    def _check_win(self, symbol):
        """
        Check if the current player has won
        Win condition: 3 symbols in a row (horizontal, vertical, or diagonal)
        
        Args:
            symbol: The symbol to check for
            
        Returns:
            bool: True if player won, False otherwise
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
    
    def get_board_state(self):
        """
        Get current board state
        
        Returns:
            list: 2D array representing the board
        """
        return [row[:] for row in self.board]
    
    def get_game_state(self):
        """
        Get complete game state
        
        Returns:
            dict: Complete game information
        """
        return {
            "game_id": self.game_id,
            "num_players": self.num_players,
            "waiting": self.waiting,
            "players": [{"id": p.player_id, "symbol": p.symbol} for p in self.players],
            "board_size": self.board_size,
            "board": self.get_board_state(),
            "current_turn": self.get_current_player().symbol if not self.waiting and not self.ended else None,
            "ended": self.ended,
            "winner": self.winner.symbol if self.winner else None,
            "move_count": self.move_count
        }
    
    def print_board(self):
        """Print board to console (for debugging/local play)"""
        print(f"\nGame {self.game_id} - Board:")
        print("  " + " ".join(str(i) for i in range(self.board_size)))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join(cell for cell in row))
        print()
    
    def get_available_games_info(self):
        """Get info for game lobby listing"""
        return {
            "game_id": self.game_id,
            "num_players": self.num_players,
            "joined_players": len(self.players),
            "waiting": self.waiting,
            "status": "Waiting for players" if self.waiting else "In progress"
        }
