import socket
import time
import threading 
from ui import print_menu, print_board_text, read_move_safe


HOST = '127.0.0.1'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)

board_size = None
in_game = False
waiting_for_move = False  # NEW: Track if we're waiting for player input


def listen_to_server():
    """Background thread that listens for server messages"""
    while True:
        try:
            data = client_socket.recv(1024).decode(FORMAT)

            # connection closed
            if not data:
                print("\n[CONNECTION LOST] Server disconnected")
                break

            handle_server_message(data)

        except Exception as e:
            # Only print error if it's not just a closed socket
            if client_socket.fileno() != -1:
                print(f"\n[ERROR] Connection error: {e}")
            break


def start_client():
    """Main client function"""
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


    # -------- START LISTENER THREAD --------
    threading.Thread(target=listen_to_server, daemon=True).start()
    # ---------------------------------------


    while True:

        # בזמן משחק – הלולאה הראשית לא עושה כלום
        if in_game:
            time.sleep(0.2)
            continue

        # רק כשלא במשחק מציגים תפריט
        print_menu()
        choice = input("Choose option: ")

        if choice == "1":
            message = "LIST"

        elif choice == "2":
            players = input("How many players (2-13)? ")
            # Validate input
            try:
                num = int(players)
                if num < 2 or num > 13:
                    print("Number of players must be between 2 and 13")
                    continue
            except ValueError:
                print("Invalid number")
                continue
            message = f"CREATE {players}"

        elif choice == "3":
            game_id = input("Enter game id: ")
            # Validate input
            try:
                int(game_id)
            except ValueError:
                print("Invalid game ID")
                continue
            message = f"JOIN {game_id}"

        elif choice == "4":
            message = "EXIT"
            client_socket.send(message.encode(FORMAT))
            break

        else:
            print("Invalid option")
            continue


        # send to server
        try:
            client_socket.send(message.encode(FORMAT))
            print(f"[SENT] {message}")
        except Exception as e:
            print(f"\n[ERROR] Failed to send message: {e}")
            break

        time.sleep(0.3)


    try:
        client_socket.close()
    except:
        pass
    print("\n[CLOSING CONNECTION] client closed socket!")


def ask_for_move():
    """Ask player for a move and send it to server"""
    global waiting_for_move
    
    waiting_for_move = True
    print("\nIt is your turn!")
    
    # Get move from player
    row, col = read_move_safe(board_size)
    
    # Validate that we got valid integers
    try:
        r = int(row)
        c = int(col)
        msg = f"MOVE {r} {c}"
    except (ValueError, TypeError):
        print("Invalid input, please try again")
        ask_for_move()  # Try again
        return
    
    # Send to server
    try:
        client_socket.send(msg.encode(FORMAT))
        print(f"[SENT] {msg}")
    except Exception as e:
        print(f"\n[ERROR] Failed to send move: {e}")
    
    waiting_for_move = False


def handle_server_message(data):
    """Handle incoming messages from server"""
    global in_game, board_size
    
    # Handle multiple messages in one packet
    messages = data.strip().split('\n')
    
    for message in messages:
        message = message.strip()
        if not message:
            continue
        
        handle_single_message(message)


def handle_single_message(message):
    """Handle a single message from server"""
    global in_game, board_size
    
    # GAMES - List of available games
    if message.startswith("GAMES"):
        games = message[6:].strip()
        print("\nAvailable games:")
        if games:
            # Parse: "waiting 1:2:1 2:3:2"
            if games.startswith("waiting"):
                game_list = games[8:].strip().split()
                if game_list:
                    print("  ID | Players | Joined")
                    print("  " + "-" * 25)
                    for game in game_list:
                        parts = game.split(':')
                        if len(parts) == 3:
                            gid, total, joined = parts
                            print(f"  {gid:2} | {total:7} | {joined:6}")
                else:
                    print("  No available games")
            else:
                print(f"  {games}")
        else:
            print("  No available games")
        return

    # CREATED - Game created successfully
    if message.startswith("CREATED"):
        parts = message.split()
        if len(parts) >= 2:
            game_id = parts[1]
            print(f"\nGame created successfully. Game ID: {game_id}")
        return

    # JOINED - Joined game successfully
    if message.startswith("JOINED"):
        in_game = True
        parts = message.split()
        if len(parts) >= 2:
            symbol = parts[1]
            print(f"\nYou joined the game as: {symbol}")
        return

    # WAIT - Waiting for other players
    if message.startswith("WAIT"):
        print("\nWaiting for other players to join...")
        return

    # YOURTURN - It's your turn
    if message.startswith("YOURTURN"):
        # Start a new thread to ask for move (so we don't block the listener)
        threading.Thread(target=ask_for_move, daemon=True).start()
        return

    # BOARD - Board state
    # if message.startswith("BOARD"):
    #     # Board might be sent with other commands on same line
    #     # We need to extract just the board part
    #     print("\n" + "=" * 40)
    #     size = print_board_text(message)
    #     if size is not None:
    #         board_size = size
    #     print("=" * 40)
    #     return
    if message.startswith("BOARD"):
        print(message)
        # split board block from the rest
        parts = message.split("\n")

        board_part = ["BOARD"]
        rest = []

        for line in parts[1:]:
            if line in ["YOURTURN", "WIN", "LOSE", "DRAW", "BYE"]:
                rest.append(line)
            else:
                board_part.append(line)

        # print the board
        size = print_board_text("\n".join(board_part))
        if size is not None:
            board_size = size

        # now handle the remaining commands
        for cmd in rest:
            handle_server_message(cmd)

        return

    # INVALID - Invalid move
    if message.startswith("INVALID"):
        reason = message[8:].strip() if len(message) > 8 else "Unknown reason"
        print(f"\nInvalid move: {reason}")
        print("Please try again.")
        # The server should send YOURTURN again, so we wait for that
        return

    # WIN - You won!
    if message == "WIN":
        in_game = False
        print("\n" + "=" * 40)
        print("CONGRATULATIONS! YOU WON! :)")
        print("=" * 40)
        return

    # LOSE - You lost
    if message == "LOSE":
        in_game = False
        print("\n" + "=" * 40)
        print("You lost the game :( Better luck next time!")
        print("=" * 40)
        return

    # DRAW - Game ended in draw
    if message == "DRAW":
        in_game = False
        print("\n" + "=" * 40)
        print("Game ended in a draw.")
        print("=" * 40)
        return

    # BYE - Disconnected
    if message == "BYE":
        print("\nDisconnected from server.")
        print("Returning to main menu...")
        return

    # Unknown message - just print it
    if message:
        print(f"\n[SERVER]: {message}")


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("=" * 50)
    print("TIC-TAC-TOE CLIENT")
    print("=" * 50)
    print("[CLIENT] Starting...")
    start_client()
    print("\nGoodbye!")
