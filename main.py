"""
Local Game Test - Test the game logic without networking
Run this to verify game functionality before implementing the server
"""

from game import Game


def display_menu():
    """Display main menu"""
    print("\n" + "=" * 50)
    print("TIC-TAC-TOE - LOCAL TEST")
    print("=" * 50)
    print("1. Start new game")
    print("2. Exit")
    print("=" * 50)


def get_valid_input(prompt, valid_range=None):
    """Get validated input from user"""
    while True:
        try:
            value = input(prompt).strip()
            if value.lower() == 'q':
                return None
            
            num = int(value)
            if valid_range and num not in valid_range:
                print(f"Invalid input. Please enter a number in range {valid_range}")
                continue
            return num
        except ValueError:
            print("Invalid input. Please enter a number (or 'q' to quit)")


def play_game():
    """Run a complete game session"""
    print("\n--- New Game Setup ---")
    
    # Get number of players
    num_players = get_valid_input(
        "Enter number of players (2-9): ",
        valid_range=range(2, 10)
    )
    
    if num_players is None:
        return
    
    # Create game
    game = Game(game_id=1, num_players=num_players)
    print(f"\nGame created! Board size: {game.board_size}x{game.board_size}")
    print(f"Win condition: 3 in a row\n")
    
    # Add players
    print("Adding players...")
    player_ids = []
    for i in range(num_players):
        player_id = f"Player{i+1}"
        success, symbol = game.add_player(player_id)
        if success:
            player_ids.append(player_id)
            print(f"  {player_id} joined as symbol: {symbol}")
        else:
            print(f"  Error adding {player_id}: {symbol}")
            return
    
    print(f"\nAll players joined! Game starting...\n")
    
    # Game loop
    move_number = 1
    while not game.ended:
        current_player = game.get_current_player()
        game.print_board()
        
        print(f"Move #{move_number}")
        print(f"Current turn: {current_player.symbol} ({current_player.player_id})")
        print("Enter move as: row col (e.g., '0 1' for row 0, column 1)")
        print("Or enter 'q' to quit\n")
        
        # Get move
        move_input = input("Your move: ").strip()
        if move_input.lower() == 'q':
            print("Game aborted.")
            return
        
        try:
            parts = move_input.split()
            if len(parts) != 2:
                print("Invalid format. Use: row col (e.g., '0 1')")
                continue
            
            row, col = int(parts[0]), int(parts[1])
        except ValueError:
            print("Invalid input. Please enter two numbers.")
            continue
        
        # Execute move
        status, data = game.play_move(current_player.player_id, row, col)
        
        if status == "invalid_turn":
            print(f"\n❌ {data['message']}")
        elif status == "invalid_move":
            print(f"\n❌ {data['message']}")
        elif status == "success":
            print(f"\n✓ Move accepted!")
            move_number += 1
        elif status == "win":
            game.print_board()
            print("=" * 50)
            print(f"🎉 GAME OVER - {data['winner']} WINS!")
            print("=" * 50)
            
            # Show winning player
            winner = game.winner
            print(f"Winner: {winner.player_id} (Symbol: {winner.symbol})")
            print(f"Total moves: {game.move_count}")
        elif status == "draw":
            game.print_board()
            print("=" * 50)
            print("🤝 GAME OVER - DRAW!")
            print("=" * 50)
            print(f"Total moves: {game.move_count}")
        else:
            print(f"\n⚠️  Error: {data.get('message', 'Unknown error')}")
    
    print("\nGame statistics:")
    print(f"  Total moves: {game.move_count}")
    print(f"  Board size: {game.board_size}x{game.board_size}")
    print(f"  Players: {len(game.players)}")


def test_game_scenarios():
    """Run automated tests on game logic"""
    print("\n" + "=" * 50)
    print("RUNNING AUTOMATED TESTS")
    print("=" * 50)
    
    # Test 1: Game creation
    print("\nTest 1: Game creation and player joining")
    game = Game(game_id=1, num_players=2)
    assert game.waiting == True
    assert game.board_size == 3
    print("  ✓ Game created successfully")
    
    # Test 2: Adding players
    success, symbol = game.add_player("p1")
    assert success == True
    assert symbol == 'X'
    print("  ✓ First player added: X")
    
    success, symbol = game.add_player("p2")
    assert success == True
    assert symbol == 'O'
    assert game.waiting == False  # Game should start
    print("  ✓ Second player added: O")
    print("  ✓ Game started automatically")
    
    # Test 3: Prevent duplicate players
    success, msg = game.add_player("p1")
    assert success == False
    print("  ✓ Duplicate player rejected")
    
    # Test 4: Valid moves
    print("\nTest 2: Move validation")
    status, data = game.play_move("p1", 0, 0)
    assert status == "success"
    print("  ✓ Valid move accepted")
    
    # Test 5: Invalid turn
    status, data = game.play_move("p1", 0, 1)
    assert status == "invalid_turn"
    print("  ✓ Wrong turn rejected")
    
    # Test 6: Occupied cell
    status, data = game.play_move("p2", 0, 0)
    assert status == "invalid_move"
    print("  ✓ Occupied cell rejected")
    
    # Test 7: Out of bounds
    status, data = game.play_move("p2", 5, 5)
    assert status == "invalid_move"
    print("  ✓ Out of bounds rejected")
    
    # Test 8: Win detection
    print("\nTest 3: Win detection")
    game2 = Game(game_id=2, num_players=2)
    game2.add_player("p1")
    game2.add_player("p2")
    
    # Set up a winning scenario
    # X X X
    # O O .
    # . . .
    game2.play_move("p1", 0, 0)  # X
    game2.play_move("p2", 1, 0)  # O
    game2.play_move("p1", 0, 1)  # X
    game2.play_move("p2", 1, 1)  # O
    status, data = game2.play_move("p1", 0, 2)  # X wins!
    
    assert status == "win"
    assert data["winner"] == "X"
    print("  ✓ Horizontal win detected")
    
    print("\nTest 4: Diagonal win detection")
    game3 = Game(game_id=3, num_players=2)
    game3.add_player("p1")
    game3.add_player("p2")
    
    # X O .
    # O X .
    # . . X
    game3.play_move("p1", 0, 0)  # X
    game3.play_move("p2", 0, 1)  # O
    game3.play_move("p1", 1, 1)  # X
    game3.play_move("p2", 1, 0)  # O
    status, data = game3.play_move("p1", 2, 2)  # X wins!
    
    assert status == "win"
    print("  ✓ Diagonal win detected")
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)


def main():
    """Main program loop"""
    while True:
        display_menu()
        choice = get_valid_input("Enter choice: ", valid_range=range(1, 3))
        
        if choice is None:
            choice = 2
        
        if choice == 1:
            play_game()
        elif choice == 2:
            print("\nGoodbye!")
            break


if __name__ == '__main__':
    import sys
    
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_game_scenarios()
    else:
        main()
