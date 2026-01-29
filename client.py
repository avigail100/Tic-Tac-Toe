import socket
import time
import threading 
from ui import print_menu, print_board_text, read_move_safe

# Server connection settings
HOST = '127.0.0.1'      # Server IP address (localhost)
PORT = 5000             # Server port
FORMAT = 'utf-8'        # Encoding format for messages
ADDR = (HOST, PORT)     # Full server address tuple

# Global state variables
board_size = None       # Board size (NxN)
in_game = False         # True if the player is currently in a game
waiting_for_move = False  # True while waiting for user input
game_active = False     # True while the game is active

def listen_to_server():
    """
    Background thread that continuously listens
    for messages from the server.
    """
    while True:
        try:
            data = client_socket.recv(1024).decode(FORMAT)

            # Connection closed by server
            if not data:
                print("\n[CONNECTION LOST] Server disconnected")
                break

            handle_server_message(data)

        except Exception as e:
            # Print error only if socket is still open
            if client_socket.fileno() != -1:
                print(f"\n[ERROR] Connection error: {e}")
            break

def start_client():
    """
    Main client function:
    - Connects to the server
    - Starts the listener thread
    - Displays the main menu
    """
    try:
        client_socket.connect((HOST, PORT))
        print("Connected to server.\n")

    except ConnectionRefusedError:
        print("\nError: Cannot connect to server.")
        print("Please make sure the server is running and try again.\n")
        return

    except Exception as e:
        print(f"\nError: Connection failed - {e}\n")
        return

    # START LISTENER THREAD
    threading.Thread(target=listen_to_server, daemon=True).start()

    while True:
        # If already inside a game, skip the menu
        if in_game:
            time.sleep(0.2)
            continue

        # Show main menu
        print_menu()
        choice = input("Choose option: ")

        # Request list of available games
        if choice == "1":
            message = "LIST"

        # Create a new game
        elif choice == "2":
            players = input("How many players (2-13)? ")
            try:
                num = int(players)
                if num < 2 or num > 13:
                    print("Number of players must be between 2 and 13")
                    continue
            except ValueError:
                print("Invalid number")
                continue
            message = f"CREATE {players}"

        # Join an existing game
        elif choice == "3":
            game_id = input("Enter game id: ")
            try:
                int(game_id)
            except ValueError:
                print("Invalid game ID")
                continue
            message = f"JOIN {game_id}"

        # Exit client
        elif choice == "4":
            message = "EXIT"
            client_socket.send(message.encode(FORMAT))
            break

        else:
            print("Invalid option")
            continue

        # Send message to server
        try:
            client_socket.send(message.encode(FORMAT))
        except Exception as e:
            print(f"\n[ERROR] Failed to send message: {e}")
            break

        time.sleep(0.3)

    # Close connection
    try:
        client_socket.close()
    except:
        pass
    print("\nCLOSING CONNECTION...")

def ask_for_move():
    """
    Prompts the player for a move and sends it to the server.
    Runs in a separate thread.
    """
    global waiting_for_move, game_active
    
    if not game_active:
        return
    
    waiting_for_move = True
    print("\nIt is your turn!")
    
    # Safe input function that stops if the game ends
    row, col = read_move_safe(board_size, lambda: game_active)

    # Game aborted during input
    if row is None or col is None:
        waiting_for_move = False
        return

    if not game_active:
        waiting_for_move = False
        return

    # Convert input to integers
    try:
        r = int(row)
        c = int(col)
        msg = f"MOVE {r} {c}"
    except (ValueError, TypeError):
        if not game_active:
            waiting_for_move = False
            return
        print("Invalid input, please try again")
        waiting_for_move = False
        ask_for_move()  # Try again
        return
    
    if not game_active:
        waiting_for_move = False
        return
    
    # Send move to server
    try:
        client_socket.send(msg.encode(FORMAT))
    except Exception as e:
        print(f"\n[ERROR] Failed to send move: {e}")
    
    waiting_for_move = False

def handle_server_message(data):
    """
    Handles raw data received from the server.
    Supports multiple messages in a single packet.
    """
    global in_game, board_size
    
    if data.startswith("BOARD"):
        handle_single_message(data.strip())
        return
    
    messages = data.strip().split('\n')
    
    for message in messages:
        message = message.strip()
        if not message:
            continue
        
        handle_single_message(message)

def handle_single_message(message):
    """
    Handles a single server message.
    """
    global in_game, board_size, game_active
    
    # List available games
    if message.startswith("GAMES"):
        games = message[6:].strip()
        print("\nAvailable games:")
        if games:
            game_list = games.split()
            print("  ID | Players | Joined")
            print("  " + "-" * 25)
            for game in game_list:
                parts = game.split(':')
                if len(parts) == 3:
                    gid, total, joined = parts
                    print(f"  {gid:2} | {total:7} | {joined:6}")
        else:
            print("  No available games")
        return

    # Game created
    if message.startswith("CREATED"):
        parts = message.split()
        if len(parts) >= 2:
            print(f"\nGame created successfully. Game ID: {parts[1]}")
        return

    # Joined game
    if message.startswith("JOINED"):
        in_game = True
        game_active = True
        parts = message.split()
        if len(parts) >= 2:
            print(f"\nYou joined the game as: {parts[1]}")
        return

    # Waiting for players
    if message.startswith("WAIT"):
        print("\nWaiting for other players to join...")
        return

    # Player's turn
    if message.startswith("YOURTURN"):
        if game_active:
            threading.Thread(target=ask_for_move, daemon=True).start()
        return

    # Board state
    if message.startswith("BOARD"):
        parts = message.split("\n")
        board_part = ["BOARD"]
        rest = []

        for line in parts[1:]:
            if line in ["YOURTURN", "WIN", "LOSE", "DRAW", "BYE"]:
                rest.append(line)
            else:
                board_part.append(line)

        size = print_board_text("\n".join(board_part))
        if size is not None:
            board_size = size

        for cmd in rest:
            handle_server_message(cmd)
        return

    # Invalid move
    if message.startswith("INVALID"):
        reason = message[8:].strip() if len(message) > 8 else "Unknown reason"
        print(f"\nInvalid move: {reason}")
        print("Please try again.")
        return

    # Win
    if message == "WIN":
        in_game = False
        game_active = False
        print("\n" + "=" * 40)
        print("CONGRATULATIONS! YOU WON! :)")
        print("=" * 40)
        return

    # Lose
    if message == "LOSE":
        in_game = False
        game_active = False
        print("\n" + "=" * 40)
        print("You lost the game :( Better luck next time!")
        print("=" * 40)
        return

    # Draw
    if message == "DRAW":
        in_game = False
        game_active = False
        print("\n" + "=" * 40)
        print("Game ended in a draw.")
        print("=" * 40)
        return

    # Disconnected
    if message == "BYE":
        print("\nDisconnected from server.")
        print("Returning to main menu...")
        return

    # Player left the game
    if message.startswith("PLAYER_LEFT"):
        print("\nA player has left the game.")
        return

    # Game aborted
    if message == "GAME_ABORTED":
        print("\nGame aborted (not enough players).")
        in_game = False
        game_active = False
        return

    # Unknown message
    if message:
        print(f"\n{message}")

if __name__ == "__main__":
    # Create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("=" * 50)
    print("WELCOME TO TIC-TAC-TOE")
    print("=" * 50)

    start_client()
    print("\nGoodbye!")