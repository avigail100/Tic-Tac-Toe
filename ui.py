# ui.py

def print_menu():
    print("\n==== TIC TAC TOE CLIENT ====")
    print("1. List games")
    print("2. Create game")
    print("3. Join game")
    print("4. Exit")


def print_board_text(board_text):
    board_text = board_text.replace("\r", "").strip()
    lines = board_text.split("\n")

    lines = [line for line in lines if line != "BOARD"]

    # Safety check
    if not lines:
        print("Empty board received")
        return None

    size = len(lines)

    print("\nCurrent Board:\n")

    header = "    " + "   ".join(str(i) for i in range(size))
    print(header)

    for i in range(size):
        cells = lines[i].split()

        row = f"{i} | " + " | ".join(cells) + " |"
        print(row)

        if i < size - 1:
            print("  " + "----" * size)

    print()

    return size   #return size for the client


def read_move_safe(board_size):
    while True:
        row = input("Row: ")
        col = input("Col: ")

        r = int(row)
        c = int(col)

        if board_size is not None:
            if r < 0 or r >= board_size or c < 0 or c >= board_size:
                print(f"Move must be between 0 and {board_size - 1}")
                continue

        return row, col
