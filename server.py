"""
Tic-Tac-Toe Game Server
"""

import socket
import threading
from game_logic import Game


# Server Configuration
HOST = '127.0.0.1'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)


class TicTacToeServer:
    """Server managing multiple games"""
    
    def __init__(self):
        self.server_socket = None
        self.games = {}  # game_id -> Game object
        self.next_game_id = 1
        self.games_lock = threading.Lock()
        
        # Track which game each connection is in
        self.conn_to_game = {}  # conn -> game_id
        self.conn_lock = threading.Lock()
        
        self.running = False
    
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(ADDR)
            self.server_socket.listen()
            self.running = True
            
            print("=" * 60)
            print("TIC-TAC-TOE SERVER")
            print("=" * 60)
            print(f"[LISTENING] Server listening on {HOST}:{PORT}")
            print("=" * 60)
            
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    print(f"[NEW CONNECTION] {addr}")
                    
                    # Handle client in new thread
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                    
                    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
                
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] Accept error: {e}")
        
        except Exception as e:
            print(f"[ERROR] Server start failed: {e}")
        
        finally:
            self.shutdown()
    
    def handle_client(self, conn, addr):
        """Handle a single client connection"""
        print(f"[CLIENT CONNECTED] {addr}")
        
        try:
            while self.running:
                try:
                    # Receive message
                    data = conn.recv(1024).decode(FORMAT)
                    
                    if not data:
                        break
                    
                    message = data.strip()
                    print(f"[RECEIVED from {addr}] {message}")
                    
                    # Parse and handle command
                    self.handle_command(conn, addr, message)
                
                except ConnectionResetError:
                    print(f"[CONNECTION RESET] {addr}")
                    break
                except Exception as e:
                    print(f"[ERROR handling {addr}] {e}")
                    break
        
        finally:
            self.disconnect_client(conn, addr)
    
    def handle_command(self, conn, addr, message):
        """Parse and execute client command"""
        
        parts = message.split()
        if not parts:
            return
        
        command = parts[0]
        
        print(f"[COMMAND from {addr}] {message}")  # Better logging
        
        # LIST - List available games
        if command == "LIST":
            self.handle_list(conn)
        
        # CREATE <players> - Create new game
        elif command == "CREATE":
            if len(parts) < 2:
                self.send(conn, "Invalid CREATE command")
                return
            try:
                num_players = int(parts[1])
                self.handle_create(conn, addr, num_players)
            except ValueError:
                self.send(conn, "Invalid number of players")
        
        # JOIN <game_id> - Join existing game
        elif command == "JOIN":
            if len(parts) < 2:
                self.send(conn, "Invalid JOIN command")
                return
            try:
                game_id = int(parts[1])
                self.handle_join(conn, addr, game_id)
            except ValueError:
                self.send(conn, "Invalid game ID")
        
        # MOVE <row> <col> - Make a move
        elif command == "MOVE":
            if len(parts) < 3:
                self.send(conn, "INVALID Missing row or column")
                # Get their game and send YOURTURN again
                with self.conn_lock:
                    game_id = self.conn_to_game.get(conn)
                if game_id:
                    with self.games_lock:
                        game = self.games.get(game_id)
                    if game and game.is_player_turn(conn):
                        self.send(conn, "YOURTURN")
                return
            try:
                row = int(parts[1])
                col = int(parts[2])
                self.handle_move(conn, addr, row, col)
            except (ValueError, IndexError):
                self.send(conn, "INVALID Invalid move format (use: MOVE <row> <col>)")
                # Send YOURTURN again
                with self.conn_lock:
                    game_id = self.conn_to_game.get(conn)
                if game_id:
                    with self.games_lock:
                        game = self.games.get(game_id)
                    if game and game.is_player_turn(conn):
                        self.send(conn, "YOURTURN")
        
        # EXIT - Disconnect
        elif command == "EXIT":
            self.send(conn, "BYE")
            conn.close()
        
        else:
            self.send(conn, f"Unknown command: {command}")
    
    def handle_list(self, conn):
        """
        Handle LIST command
        Send: GAMES <list>
        Format: "waiting 2:full:1 3:full:2"
        """
        with self.games_lock:
            waiting_games = []
            
            for game_id, game in self.games.items():
                if game.is_waiting():
                    # Format: <game_id>:<num_players>:<joined>
                    waiting_games.append(f"{game_id}:{game.num_players}:{len(game.players)}")
            
            if waiting_games:
                games_str = " ".join(waiting_games)
            else:
                games_str = ""
            
            response = f"GAMES {games_str}"
            self.send(conn, response)
            print(f"[SENT] {response}")
    
    def handle_create(self, conn, addr, num_players):
        """
        Handle CREATE command
        Send: CREATED <game_id>
        """
        if num_players < 2 or num_players > 13:
            self.send(conn, "Number of players must be 2-13")
            return
        
        with self.games_lock:
            game_id = self.next_game_id
            self.next_game_id += 1
            
            # Create game
            game = Game(game_id, num_players)
            
            # Add creator as first player
            success, symbol = game.add_player(conn, addr)
            
            if not success:
                self.send(conn, f"Error: {symbol}")
                return
            
            self.games[game_id] = game
            
            # Track connection
            with self.conn_lock:
                self.conn_to_game[conn] = game_id
        
        # Send responses
        self.send(conn, f"CREATED {game_id}")
        self.send(conn, f"JOINED {symbol}")
        self.send(conn, "WAIT")
        
        print(f"[GAME CREATED] Game {game_id} by {addr} ({num_players} players)")
        
    def handle_join(self, conn, addr, game_id):
        """
        Handle JOIN command
        Send: JOINED <symbol>
        Then: WAIT or start game
        """
        with self.games_lock:
            game = self.games.get(game_id)
            
            if not game:
                self.send(conn, f"Game {game_id} not found")
                return
            
            if not game.is_waiting():
                self.send(conn, "Game already started")
                return
            
            if game.is_full():
                self.send(conn, "Game is full")
                return
            
            # Add player
            success, symbol = game.add_player(conn, addr)
            
            if not success:
                self.send(conn, f"Error: {symbol}")
                return
            
            # Track connection
            with self.conn_lock:
                self.conn_to_game[conn] = game_id
        
        # Send join confirmation
        self.send(conn, f"JOINED {symbol}")
        
        print(f"[PLAYER JOINED] {addr} joined game {game_id} as {symbol}")
        
        # Check if game should start
        if game.started:
            self.start_game(game)
        else:
            self.send(conn, "WAIT")
    
    def start_game(self, game):
        """
        Start the game - notify all players
        Send board and tell first player it's their turn
        """
        print(f"[GAME STARTED] Game {game.game_id}")

        # Send board to all players
        board_str = game.get_board_string()
        
        for i, player in enumerate(game.players):
            self.send(player.conn, board_str)
            
            # Tell first player it's their turn
            if i == 0:
                self.send(player.conn, "YOURTURN")
    
    def handle_move(self, conn, addr, row, col):
        """
        Handle MOVE command
        Send: BOARD, then YOURTURN/WIN/LOSE/DRAW
        """
        # Get player's game
        with self.conn_lock:
            game_id = self.conn_to_game.get(conn)
        
        if game_id is None:
            self.send(conn, "INVALID Not in a game")
            return
        
        with self.games_lock:
            game = self.games.get(game_id)
        
        if not game:
            self.send(conn, "INVALID Game not found")
            return
        
        # Make the move
        status, data = game.make_move(conn, row, col)
        
        if status == "invalid":
            self.send(conn, f"INVALID {data}")
            # Send YOURTURN again so player can retry
            self.send(conn, "YOURTURN")
            return
        
        # Move was successful - send board to all players
        board_str = game.get_board_string()
        
        for player in game.players:
            self.send(player.conn, board_str)
        
        # Handle game end
        if status == "win":
            # Winner gets WIN, others get LOSE
            winner = game.winner
            for player in game.players:
                if player.conn == winner.conn:
                    self.send(player.conn, "WIN")
                else:
                    self.send(player.conn, "LOSE")
            
            print(f"[GAME ENDED] Game {game_id} - Winner: {winner.symbol}")
        
        elif status == "draw":
            # All players get DRAW
            for player in game.players:
                self.send(player.conn, "DRAW")
            
            print(f"[GAME ENDED] Game {game_id} - Draw")
        
        else:  # status == "success"
            # Tell next player it's their turn
            current_player = game.get_current_player()
            self.send(current_player.conn, "YOURTURN")
    
    def send(self, conn, message):
        """Send message to client"""
        try:
            conn.send((message + "\n").encode(FORMAT))
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
    

    def disconnect_client(self, conn, addr):
        print(f"[DISCONNECTED] {addr}")
    
        with self.conn_lock:
            game_id = self.conn_to_game.pop(conn, None)
    
        if game_id:
            with self.games_lock:
                game = self.games.get(game_id)
    
                if game:
                    result = game.remove_player(conn)
    
                    # הודעה לשחקנים שנשארו
                    for p in game.players:
                        self.send(p.conn, f"PLAYER_LEFT")
    
                    # אם המשחק נגמר/בוטל
                    if result == "abort":
                        for p in game.players:
                            self.send(p.conn, "GAME_ABORTED")
    
                        del self.games[game_id]
                        print(f"[GAME REMOVED] Game {game_id} deleted")
    
        try:
            conn.close()
        except:
            pass

    
    def shutdown(self):
        """Shutdown the server"""
        print("\n[SHUTTING DOWN] Server shutting down...")
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[SHUTDOWN COMPLETE]")


def main():
    """Main server entry point"""
    server = TicTacToeServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Shutting down...")
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
