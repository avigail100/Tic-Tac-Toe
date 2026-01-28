# ארכיטקטורת המערכת

## מבנה הפרויקט

```
┌─────────────────────────────────────────────────────────┐
│                    TIC-TAC-TOE SYSTEM                   │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   CLIENT 1       │         │   CLIENT 2       │
│  (client.py)     │         │  (client.py)     │
│                  │         │                  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │   ui.py    │  │         │  │   ui.py    │  │
│  │  (display) │  │         │  │  (display) │  │
│  └────────────┘  │         │  └────────────┘  │
└────────┬─────────┘         └─────────┬────────┘
         │                             │
         │  TCP Socket                 │  TCP Socket
         │  (127.0.0.1:5000)          │  (127.0.0.1:5000)
         │                             │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │      SERVER MAIN            │
         │   (server_main.py)          │
         │                             │
         │  ┌─────────────────────┐    │
         │  │ TicTacToeServer     │    │
         │  │                     │    │
         │  │ - handle_client()   │    │
         │  │ - handle_command()  │    │
         │  │ - handle_list()     │    │
         │  │ - handle_create()   │    │
         │  │ - handle_join()     │    │
         │  │ - handle_move()     │    │
         │  │                     │    │
         │  │ Games Management:   │    │
         │  │ - games {}          │    │
         │  │ - conn_to_game {}   │    │
         │  │ - locks             │    │
         │  └──────────┬──────────┘    │
         │             │                │
         │   ┌─────────▼──────────┐    │
         │   │   GAME LOGIC       │    │
         │   │  (game_logic.py)   │    │
         │   │                    │    │
         │   │  ┌──────────────┐  │    │
         │   │  │ Game         │  │    │
         │   │  │ - board      │  │    │
         │   │  │ - players    │  │    │
         │   │  │ - make_move()│  │    │
         │   │  │ - check_win()│  │    │
         │   │  └──────────────┘  │    │
         │   │                    │    │
         │   │  ┌──────────────┐  │    │
         │   │  │ Player       │  │    │
         │   │  │ - conn       │  │    │
         │   │  │ - symbol     │  │    │
         │   │  └──────────────┘  │    │
         │   └────────────────────┘    │
         └─────────────────────────────┘
```

## תרשים תהליכי (Flow)

### 1. יצירת משחק והצטרפות

```
Client 1                  Server                   Game Logic
   │                         │                          │
   ├─ CREATE 2 ─────────────>│                          │
   │                         ├─ new Game(1, 2) ───────>│
   │                         │                          │
   │                         │<── Game object ──────────┤
   │                         │                          │
   │                         ├─ game.add_player() ────>│
   │                         │<── (True, "X") ──────────┤
   │<─ CREATED 1 ────────────┤                          │
   │<─ JOINED X ─────────────┤                          │
   │<─ WAIT ─────────────────┤                          │
   │                         │                          │
                             │
Client 2                     │                          │
   │                         │                          │
   ├─ LIST ─────────────────>│                          │
   │<─ GAMES waiting 1:2:1 ──┤                          │
   │                         │                          │
   ├─ JOIN 1 ───────────────>│                          │
   │                         ├─ game.add_player() ────>│
   │                         │<── (True, "O") ──────────┤
   │                         │     game.started = True  │
   │<─ JOINED O ─────────────┤                          │
   │                         │                          │
   │<─ BOARD ────────────────┤<─ get_board_string() ────┤
   │<─ (empty board)         │                          │
   │                         │                          │
Client 1                     │                          │
   │<─ BOARD ────────────────┤                          │
   │<─ YOURTURN ─────────────┤                          │
```

### 2. ביצוע מהלכים

```
Client 1 (X's turn)       Server                   Game Logic
   │                         │                          │
   ├─ MOVE 0 0 ─────────────>│                          │
   │                         ├─ game.make_move() ─────>│
   │                         │     - validate move      │
   │                         │     - update board       │
   │                         │     - check win          │
   │                         │<── ("success", None) ────┤
   │                         │                          │
   │<─ BOARD ────────────────┤<─ get_board_string() ────┤
   │   (X at 0,0)            │                          │
   │                         │                          │
Client 2 (O)                │                          │
   │<─ BOARD ────────────────┤  (broadcast to all)      │
   │<─ YOURTURN ─────────────┤                          │
   │                         │                          │
   ├─ MOVE 1 1 ─────────────>│                          │
   │                         ├─ game.make_move() ─────>│
   │                         │<── ("success", None) ────┤
   │<─ BOARD ────────────────┤                          │
   │                         │                          │
Client 1                     │                          │
   │<─ BOARD ────────────────┤                          │
   │<─ YOURTURN ─────────────┤                          │
```

### 3. סיום משחק (ניצחון)

```
Client 1 (X's turn)       Server                   Game Logic
   │                         │                          │
   ├─ MOVE 0 2 ─────────────>│  (winning move)          │
   │                         ├─ game.make_move() ─────>│
   │                         │     - place X at (0,2)   │
   │                         │     - check_win()        │
   │                         │     - found: X X X       │
   │                         │<── ("win", "X") ─────────┤
   │                         │     game.ended = True    │
   │                         │     game.winner = X      │
   │                         │                          │
   │<─ BOARD ────────────────┤<─ get_board_string() ────┤
   │   (X X X in row 0)      │                          │
   │<─ WIN ──────────────────┤                          │
   │                         │                          │
Client 2 (O)                │                          │
   │<─ BOARD ────────────────┤  (broadcast)             │
   │<─ LOSE ─────────────────┤                          │
```

## מבנה המחלקות

### Game (game_logic.py)

```python
class Game:
    # State
    - game_id: int
    - num_players: int
    - players: List[Player]
    - board: List[List[str]]
    - board_size: int
    - current_turn: int
    - started: bool
    - ended: bool
    - winner: Player
    - move_count: int
    
    # Methods
    + __init__(game_id, num_players)
    + is_full() -> bool
    + is_waiting() -> bool
    + add_player(conn, addr) -> (bool, str)
    + get_current_player() -> Player
    + is_player_turn(conn) -> bool
    + make_move(conn, row, col) -> (str, data)
    + check_win(symbol) -> bool
    + get_board_string() -> str
    + get_player_by_conn(conn) -> Player
```

### Player (game_logic.py)

```python
class Player:
    # State
    - conn: socket
    - addr: tuple
    - symbol: str
    
    # Methods
    + __init__(conn, addr, symbol)
```

### TicTacToeServer (server_main.py)

```python
class TicTacToeServer:
    # State
    - server_socket: socket
    - games: Dict[int, Game]
    - next_game_id: int
    - conn_to_game: Dict[socket, int]
    - games_lock: Lock
    - conn_lock: Lock
    - running: bool
    
    # Methods
    + __init__()
    + start()
    + handle_client(conn, addr)
    + handle_command(conn, addr, message)
    + handle_list(conn)
    + handle_create(conn, addr, num_players)
    + handle_join(conn, addr, game_id)
    + handle_move(conn, addr, row, col)
    + start_game(game)
    + send(conn, message)
    + disconnect_client(conn, addr)
    + shutdown()
```

## ניהול Threads

```
Main Thread
  │
  ├─ start() - Accept loop
  │   │
  │   ├─ Thread 1: handle_client(conn1, addr1)
  │   │   │
  │   │   └─ Handles commands from Client 1
  │   │       - Acquires locks when needed
  │   │       - Modifies shared state (games, conn_to_game)
  │   │
  │   ├─ Thread 2: handle_client(conn2, addr2)
  │   │   │
  │   │   └─ Handles commands from Client 2
  │   │       - Acquires locks when needed
  │   │       - Modifies shared state
  │   │
  │   └─ Thread N: handle_client(connN, addrN)
  │
  └─ cleanup on shutdown
```

## Thread Safety

### Locks משמשים ל:

1. **games_lock** - מגן על:
   - `self.games` - dictionary של כל המשחקים
   - `self.next_game_id` - מונה ייחודי
   - גישה למשחק ספציפי

2. **conn_lock** - מגן על:
   - `self.conn_to_game` - מיפוי connection למשחק

### דוגמת שימוש:

```python
def handle_join(self, conn, addr, game_id):
    # Lock 1: Access games
    with self.games_lock:
        game = self.games.get(game_id)
        # ... validate and add player
    
    # Lock 2: Update connection mapping
    with self.conn_lock:
        self.conn_to_game[conn] = game_id
```

## פרוטוקול תקשורת

### Encoding
- כל ההודעות: UTF-8
- ניתן להוסיף גם \r\n אבל השרת מטפל ב-strip()

### Message Format
```
<COMMAND> [<PARAM1>] [<PARAM2>] ...
```

אין headers, אין JSON - פשוט text commands.

### דוגמאות:
```
CREATE 2          → יצירת משחק ל-2 שחקנים
JOIN 1            → הצטרפות למשחק 1
MOVE 0 1          → מהלך בשורה 0 עמודה 1
LIST              → רשימת משחקים
EXIT              → ניתוק
```

## מבנה הלוח בזיכרון

```python
# For 2 players (3x3 board):
board = [
    ['.', '.', '.'],  # Row 0
    ['.', '.', '.'],  # Row 1
    ['.', '.', '.']   # Row 2
]

# After some moves:
board = [
    ['X', 'O', 'X'],  # Row 0
    ['.', 'X', '.'],  # Row 1
    ['O', '.', '.']   # Row 2
]
```

## מבנה הלוח בפרוטוקול

```
BOARD
X O X
. X .
O . .
```

- שורה ראשונה: `BOARD`
- שורות הבאות: תאי הלוח מופרדים ברווחים
- `.` = תא ריק
- `X`, `O`, `A`, `B` = סימני שחקנים

## אלגוריתם זיהוי ניצחון

```python
def check_win(symbol):
    # Check all possible 3-in-a-row combinations:
    
    # 1. Horizontal (rows)
    for row in board:
        for start_col in range(board_size - 2):
            if row[start_col:start_col+3] == [symbol, symbol, symbol]:
                return True
    
    # 2. Vertical (columns)
    for col in range(board_size):
        for start_row in range(board_size - 2):
            if board[start_row][col] == board[start_row+1][col] == board[start_row+2][col] == symbol:
                return True
    
    # 3. Diagonal (↘)
    for row in range(board_size - 2):
        for col in range(board_size - 2):
            if board[row][col] == board[row+1][col+1] == board[row+2][col+2] == symbol:
                return True
    
    # 4. Diagonal (↙)
    for row in range(board_size - 2):
        for col in range(2, board_size):
            if board[row][col] == board[row+1][col-1] == board[row+2][col-2] == symbol:
                return True
    
    return False
```

## סיבוכיות חישובית

### זיהוי ניצחון: O(n²)
- n = board_size
- עובר על כל האפשרויות פעם אחת

### ביצוע מהלך: O(n²)
- בדיקת תקינות: O(1)
- עדכון לוח: O(1)
- זיהוי ניצחון: O(n²)

### הצטרפות למשחק: O(1)
- פשוט מוסיף לרשימה

## זיכרון

### Per Game:
- Board: n² cells (strings)
- Players: max 4 Player objects
- State variables: ~10 variables
- **Total: ~O(n²)**

### Per Server:
- Games dictionary: O(G) where G = number of games
- Connection mappings: O(C) where C = connections
- **Total: O(G·n² + C)**

---

**סיום תיעוד ארכיטקטורה**
