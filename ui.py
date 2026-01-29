# ui.py - User Interface Functions

def print_menu():
    """Display the main menu options to the user"""
    print("\n" + "=" * 35)
    print(" MENU ")
    print("=" * 35)
    print("1. List available games")
    print("2. Create new game")
    print("3. Join existing game")
    print("4. Exit")
    print("=" * 35)

def print_board_text(board_text):
    """
    Print the game board in a formatted table
    
    Args:
        board_text: Raw board string received from the server
    
    Returns:
        Board size (int) or None if an error occurs
    """
    # Remove carriage returns and trim whitespace
    board_text = board_text.replace("\r", "").strip()
    lines = board_text.split("\n")

    # Remove the "BOARD" header line if present
    lines = [line.strip() for line in lines if line.strip() and line.strip() != "BOARD"]

    # Board size is determined by number of rows
    size = len(lines)

    print("\nCurrent Board:\n")

    # Print column headers
    header = "    " + "   ".join(str(i) for i in range(size))
    print(header)
    print("  " + "=" * (size * 4 - 1))

    # Print each board row
    for i in range(size):
        cells = lines[i].split()
        
        # Validate correct number of cells
        if len(cells) != size:
            print(f"Warning: Row {i} has {len(cells)} cells, expected {size}")
            continue
        
        # Convert '.' to empty space for display
        formatted_cells = []
        for cell in cells:
            if cell == '.':
                formatted_cells.append(' ')
            else:
                formatted_cells.append(cell)
        
        row = f"{i} | " + " | ".join(formatted_cells) + " |"
        print(row)

        # Print row separator
        if i < size - 1:
            print("  " + "----" * size)

    print()
    return size

def read_move_safe(board_size, game_active_check=None):
    """
    Safely read a move from the user with validation
    
    Args:
        board_size: Size of the game board
        game_active_check: Optional callable to verify game is still active
    
    Returns:
        (row_str, col_str) as strings
        (None, None) if game was aborted during waiting for input
    """
    while True:
        try:
            # Check if the game is still active
            if game_active_check and not game_active_check():
                return None, None
            
            print("\nEnter your move:")
            row_input = input("  Row: ").strip()
            
            if game_active_check and not game_active_check():
                return None, None
            
            col_input = input("  Col: ").strip()
            
            if game_active_check and not game_active_check():
                return None, None

            # Convert input to integers
            try:
                row = int(row_input)
                col = int(col_input)
            except ValueError:
                print("Please enter valid numbers")
                continue

            # Validate input range
            if board_size is not None:
                if row < 0 or row >= board_size:
                    print(f"Row must be between 0 and {board_size - 1}")
                    continue

                if col < 0 or col >= board_size:
                    print(f"Column must be between 0 and {board_size - 1}")
                    continue

            # Return values as strings for compatibility
            return str(row), str(col)
    
        except Exception as e:
            print(f"Error reading input: {e}")
            continue