"""
Local test for game logic - test without networking
"""

from game_logic import Game, Player


def test_game_creation():
    """Test basic game creation"""
    print("Test 1: Game Creation")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=2)
    assert game.game_id == 1
    assert game.num_players == 2
    assert game.board_size == 3
    assert not game.started
    assert not game.ended
    
    print("✓ Game created successfully")
    print(f"  Game ID: {game.game_id}")
    print(f"  Players: {game.num_players}")
    print(f"  Board size: {game.board_size}x{game.board_size}")
    print()


def test_player_joining():
    """Test player joining"""
    print("Test 2: Player Joining")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=2)
    
    # Add first player
    success, symbol1 = game.add_player("conn1", "addr1")
    assert success == True
    assert symbol1 == "X"
    assert not game.started  # Game should not start yet
    
    print(f"✓ Player 1 joined as {symbol1}")
    
    # Add second player
    success, symbol2 = game.add_player("conn2", "addr2")
    assert success == True
    assert symbol2 == "O"
    assert game.started  # Game should start now
    
    print(f"✓ Player 2 joined as {symbol2}")
    print(f"✓ Game started: {game.started}")
    print()


def test_board_string():
    """Test board string generation"""
    print("Test 3: Board String Format")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=2)
    game.add_player("conn1", "addr1")
    game.add_player("conn2", "addr2")
    
    board_str = game.get_board_string()
    print("Board string:")
    print(board_str)
    print()
    
    assert board_str.startswith("BOARD")
    lines = board_str.split("\n")
    assert len(lines) == 4  # BOARD + 3 rows for 2 players
    
    print("✓ Board string format correct")
    print()


def test_moves_and_win():
    """Test making moves and win detection"""
    print("Test 4: Moves and Win Detection")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=2)
    conn1 = "conn1"
    conn2 = "conn2"
    
    game.add_player(conn1, "addr1")
    game.add_player(conn2, "addr2")
    
    print("Initial board:")
    print(game.get_board_string())
    print()
    
    # Player 1 (X) moves
    status, _ = game.make_move(conn1, 0, 0)
    assert status == "success"
    print(f"✓ Move 1: X at (0,0) - {status}")
    
    # Player 2 (O) moves
    status, _ = game.make_move(conn2, 1, 0)
    assert status == "success"
    print(f"✓ Move 2: O at (1,0) - {status}")
    
    # Player 1 (X) moves
    status, _ = game.make_move(conn1, 0, 1)
    assert status == "success"
    print(f"✓ Move 3: X at (0,1) - {status}")
    
    # Player 2 (O) moves
    status, _ = game.make_move(conn2, 1, 1)
    assert status == "success"
    print(f"✓ Move 4: O at (1,1) - {status}")
    
    # Player 1 (X) wins with (0, 2)
    status, winner = game.make_move(conn1, 0, 2)
    print(f"✓ Move 5: X at (0,2) - {status}")
    
    assert status == "win"
    assert winner == "X"
    assert game.ended
    
    print("\nFinal board:")
    print(game.get_board_string())
    print()
    
    print(f"✓ Win detected! Winner: {winner}")
    print()


def test_invalid_moves():
    """Test invalid move detection"""
    print("Test 5: Invalid Moves")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=2)
    conn1 = "conn1"
    conn2 = "conn2"
    
    game.add_player(conn1, "addr1")
    game.add_player(conn2, "addr2")
    
    # Valid move
    status, _ = game.make_move(conn1, 0, 0)
    assert status == "success"
    print("✓ Move 1: X at (0,0) - success")
    
    # Try to play on occupied cell
    status, msg = game.make_move(conn2, 0, 0)
    assert status == "invalid"
    print(f"✓ Invalid move detected: {msg}")
    
    # Try to play out of turn
    status, msg = game.make_move(conn1, 0, 1)
    assert status == "invalid"
    print(f"✓ Out of turn detected: {msg}")
    
    # Valid move
    status, _ = game.make_move(conn2, 1, 1)
    assert status == "success"
    print("✓ Move 2: O at (1,1) - success")
    
    # Try out of bounds
    status, msg = game.make_move(conn1, 5, 5)
    assert status == "invalid"
    print(f"✓ Out of bounds detected: {msg}")
    
    print()


def test_three_players():
    """Test game with 3 players"""
    print("Test 6: Three Player Game")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=3)
    
    game.add_player("conn1", "addr1")
    game.add_player("conn2", "addr2")
    success, symbol = game.add_player("conn3", "addr3")
    
    assert success == True
    assert symbol == "A"
    assert game.started
    assert game.board_size == 4
    
    print(f"✓ 3-player game created")
    print(f"  Board size: {game.board_size}x{game.board_size}")
    print(f"  Players: X, O, A")
    print()
    
    print("Board:")
    print(game.get_board_string())
    print()


def test_draw():
    """Test draw detection"""
    print("Test 7: Draw Detection")
    print("-" * 40)
    
    game = Game(game_id=1, num_players=2)
    conn1 = "conn1"
    conn2 = "conn2"
    
    game.add_player(conn1, "addr1")
    game.add_player(conn2, "addr2")
    
    # Fill the board without winning
    # X O X
    # X O O
    # O X X
    moves = [
        (conn1, 0, 0),  # X
        (conn2, 0, 1),  # O
        (conn1, 0, 2),  # X
        (conn2, 1, 2),  # O
        (conn1, 1, 0),  # X
        (conn2, 2, 0),  # O
        (conn1, 2, 1),  # X
        (conn2, 1, 1),  # O
        (conn1, 2, 2),  # X - DRAW
    ]
    
    for i, (conn, row, col) in enumerate(moves):
        status, _ = game.make_move(conn, row, col)
        if i < len(moves) - 1:
            assert status == "success"
        else:
            assert status == "draw"
            print(f"✓ Draw detected after {i+1} moves")
    
    print("\nFinal board:")
    print(game.get_board_string())
    print()


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("GAME LOGIC TESTS")
    print("=" * 60)
    print()
    
    try:
        test_game_creation()
        test_player_joining()
        test_board_string()
        test_moves_and_win()
        test_invalid_moves()
        test_three_players()
        test_draw()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
