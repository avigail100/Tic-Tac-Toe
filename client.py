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


def listen_to_server():
    while True:
        try:
            data = client_socket.recv(1024).decode(FORMAT)

            # connection closed
            if not data:
                break

            handle_server_message(data)

        except:
            break


def start_client():
    try:
        client_socket.connect((HOST, PORT))
        print("Connected to server.\n")

    except ConnectionRefusedError:
        print("\nError: Cannot connect to server.")
        print("Please make sure the server is running and try again.\n")
        return

    except Exception:
        print("\nError: Connection failed.\n")
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
            players = input("How many players (2-4)? ")
            message = f"CREATE {players}"

        elif choice == "3":
            game_id = input("Enter game id: ")
            message = f"JOIN {game_id}"

        elif choice == "4":
            message = "EXIT"
            client_socket.send(message.encode(FORMAT))
            break

        else:
            print("Invalid option")
            continue


        # send to server
        client_socket.send(message.encode(FORMAT))
        print(f"[SENT] {message}")

        time.sleep(0.3)


    client_socket.close()
    print("\n[CLOSING CONNECTION] client closed socket!")

def handle_server_message(data):
    global in_game, board_size
    message = data.strip()

    if message.startswith("GAMES"):
        games = message[6:]
        print("\nAvailable games:")
        print(games if games else "No available games")
        return

    if message.startswith("CREATED"):
        game_id = message.split()[1]
        print(f"\nGame created successfully. Game id: {game_id}")
        return

    if message.startswith("JOINED"):
        in_game = True
        symbol = message.split()[1]
        print(f"\nYou joined the game as: {symbol}")
        return

    if message.startswith("WAIT"):
        print("\nWaiting for other players to join...")
        return

    if message.startswith("YOURTURN"):
        print("\nIt is your turn!")

        # ask for move directly
        row, col = read_move_safe(board_size)
        msg = f"MOVE {row} {col}"

        client_socket.send(msg.encode(FORMAT))
        print(f"[SENT] {msg}")
        return


    if message.startswith("BOARD"):
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

    if message.startswith("INVALID"):
        reason = message[8:]
        print(f"\nInvalid move: {reason}")
        return

    if message in ["WIN", "LOSE", "DRAW"]:
        in_game = False

        if message == "WIN":
            print("\nYou won the game!")

        elif message == "LOSE":
            print("\nYou lost the game.")

        else:
            print("\nGame ended in a draw.")

        return

    if message == "BYE":
        print("\nDisconnected from server.")
        print("Returning to main menu...")
        return


    print("\n[SERVER]:")
    print(message)


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("[CLIENT] Started running")
    start_client()
    print("\nGoodbye client:)")
