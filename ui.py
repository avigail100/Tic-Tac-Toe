# ui.py - User Interface Functions

def print_menu():
    """Display main menu"""
    print("\n" + "=" * 35)
    print("    TIC TAC TOE CLIENT")
    print("=" * 35)
    print("1. List available games")
    print("2. Create new game")
    print("3. Join existing game")
    print("4. Exit")
    print("=" * 35)


def print_board_text(board_text):
    """
    Print the board in a nice format
    Returns: board size (int) or None if error
    """
    # Clean up the input
    board_text = board_text.replace("\r", "").strip()
    lines = board_text.split("\n")

    # Remove "BOARD" line if present
    lines = [line.strip() for line in lines if line.strip() and line.strip() != "BOARD"]

    # # Safety check
    # if not lines:
    #     print("Empty board received")
    #     return None

    size = len(lines)

    print("\nCurrent Board:")
    print()

    # Print column headers
    header = "    " + "   ".join(str(i) for i in range(size))
    print(header)
    print("  " + "=" * (size * 4 - 1))

    # Print each row
    for i in range(size):
        cells = lines[i].split()
        
        # Make sure we have the right number of cells
        if len(cells) != size:
            print(f"Warning: Row {i} has {len(cells)} cells, expected {size}")
            continue
        
        # Format cells nicely
        formatted_cells = []
        for cell in cells:
            if cell == '.':
                formatted_cells.append(' ')  # Empty cell
            else:
                formatted_cells.append(cell)  # X, O, A, B
        
        row = f"{i} | " + " | ".join(formatted_cells) + " |"
        print(row)

        if i < size - 1:
            print("  " + "----" * size)

    print()
    return size

def read_move_safe(board_size, game_active_check=None):
    """
    Read a move from the user with validation
    
    Args:
        board_size: Size of the game board
        game_active_check: Optional callable that returns True if game is still active
        
    Returns: 
        (row_str, col_str) - both as strings for compatibility
        (None, None) if game was aborted during input
    """
    while True:
        try:
            # Check if game is still active before asking for input
            if game_active_check and not game_active_check():
                return None, None
            
            print("\nEnter your move:")
            row_input = input("  Row: ").strip()
            
            # Check again after row input
            if game_active_check and not game_active_check():
                return None, None
            
            col_input = input("  Col: ").strip()
            
            # Check again after col input
            if game_active_check and not game_active_check():
                return None, None

            # Try to parse as integers
            try:
                row = int(row_input)
                col = int(col_input)
            except ValueError:
                print("Please enter valid numbers")
                continue

            # Validate range if we know the board size
            if board_size is not None:
                if row < 0 or row >= board_size:
                    print(f"Row must be between 0 and {board_size - 1}")
                    continue

                if col < 0 or col >= board_size:
                    print(f"Column must be between 0 and {board_size - 1}")
                    continue

            # Valid input - return as strings (for compatibility with existing code)
            return str(row), str(col)
    
        except Exception as e:
            print(f"Error reading input: {e}")
            continue


def print_welcome():
    """Print welcome banner"""
    print()
    print("=" * 50)
    print("     WELCOME TO TIC-TAC-TOE MULTIPLAYER")
    print("=" * 50)
    print()


def print_game_rules():
    """Print game rules"""
    print("\nGame Rules:")
    print("  • Get 3 symbols in a row to win (horizontal, vertical, or diagonal)")
    print("  • Board size = number of players + 1")
    print("  • 2 players → 3×3 board")
    print("  • 3 players → 4×4 board")
    print("  • 4 players → 5×5 board")
    print()