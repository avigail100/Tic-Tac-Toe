# מדריך שימוש - שרת Tic-Tac-Toe

## קבצים במערכת

```
game_logic.py       - לוגיקת המשחק (שכבה שטוחה)
server_main.py      - השרת המלא
test_game.py        - בדיקות לוגיקה מקומית
client.py           - הלקוח שלך (קיים)
ui.py              - ממשק הלקוח (קיים)
```

## התקנה והרצה

### שלב 1: בדיקה מקומית

לפני הרצת השרת, בדוק שהלוגיקה עובדת:

```bash
python test_game.py
```

אמור להדפיס:
```
============================================================
GAME LOGIC TESTS
============================================================
...
ALL TESTS PASSED! ✓
```

### שלב 2: הרצת השרת

```bash
python server_main.py
```

תראה:
```
============================================================
TIC-TAC-TOE SERVER
============================================================
[LISTENING] Server listening on 127.0.0.1:5000
============================================================
```

### שלב 3: חיבור לקוחות

פתח טרמינלים נפרדים עבור כל לקוח:

#### טרמינל 1 - לקוח ראשון:
```bash
python client.py
```

#### טרמינל 2 - לקוח שני:
```bash
python client.py
```

## הפרוטוקול המדויק

### CLIENT → SERVER

| פקודה | פורמט | תיאור |
|-------|-------|-------|
| `LIST` | `LIST` | בקשת רשימת משחקים פתוחים |
| `CREATE` | `CREATE <num_players>` | יצירת משחק חדש (2-4 שחקנים) |
| `JOIN` | `JOIN <game_id>` | הצטרפות למשחק קיים |
| `MOVE` | `MOVE <row> <col>` | ביצוע מהלך |
| `EXIT` | `EXIT` | יציאה מהשרת |

### SERVER → CLIENT

| תגובה | פורמט | תיאור |
|-------|-------|-------|
| `GAMES` | `GAMES <list>` | רשימת משחקים זמינים |
| `CREATED` | `CREATED <game_id>` | משחק נוצר בהצלחה |
| `JOINED` | `JOINED <symbol>` | הצטרפות למשחק |
| `WAIT` | `WAIT` | ממתין לשחקנים נוספים |
| `BOARD` | `BOARD\n<board_data>` | מצב הלוח הנוכחי |
| `YOURTURN` | `YOURTURN` | התור שלך |
| `INVALID` | `INVALID <reason>` | מהלך לא חוקי |
| `WIN` | `WIN` | ניצחת! |
| `LOSE` | `LOSE` | הפסדת |
| `DRAW` | `DRAW` | תיקו |
| `BYE` | `BYE` | התנתקות בהצלחה |

## דוגמת משחק מלא

### יצירת משחק

**Client 1:**
```
Choose option: 2
How many players (2-4)? 2
[SENT] CREATE 2
```

**Server → Client 1:**
```
CREATED 1
JOINED X
WAIT
```

### הצטרפות למשחק

**Client 2:**
```
Choose option: 1
[SENT] LIST
```

**Server → Client 2:**
```
GAMES waiting 1:2:1
```
(פירוש: משחק 1, 2 שחקנים, 1 הצטרף)

**Client 2:**
```
Choose option: 3
Enter game id: 1
[SENT] JOIN 1
```

**Server → Client 2:**
```
JOINED O
```

**Server → Both Clients:**
```
BOARD
. . .
. . .
. . .
```

**Server → Client 1:**
```
YOURTURN
```

### ביצוע מהלכים

**Client 1:**
```
Row: 0
Col: 0
[SENT] MOVE 0 0
```

**Server → Both:**
```
BOARD
X . .
. . .
. . .
```

**Server → Client 2:**
```
YOURTURN
```

**Client 2:**
```
Row: 1
Col: 1
[SENT] MOVE 1 1
```

**Server → Both:**
```
BOARD
X . .
. O .
. . .
```

**Server → Client 1:**
```
YOURTURN
```

### ניצחון

לאחר מהלך מנצח:

**Server → Winner:**
```
BOARD
X X X
. O .
. . O

WIN
```

**Server → Loser:**
```
BOARD
X X X
. O .
. . O

LOSE
```

## פרטים טכניים

### מבנה הלוח

- לוח מתחיל ריק עם נקודות: `.`
- סימני שחקנים: `X`, `O`, `A`, `B`
- תנאי ניצחון: **3 ברצף** (אופקי/אנכי/אלכסוני)
- גודל לוח: `num_players + 1`
  - 2 שחקנים → לוח 3×3
  - 3 שחקנים → לוח 4×4
  - 4 שחקנים → לוח 5×5

### רשימת משחקים

פורמט: `waiting <game_id>:<num_players>:<joined>`

דוגמאות:
- `GAMES waiting 1:2:1` - משחק 1, דרושים 2, הצטרף 1
- `GAMES waiting 1:2:1 2:3:2` - שני משחקים זמינים
- `GAMES` - אין משחקים זמינים

### הודעות שגיאה

- `INVALID Not your turn` - ניסיון לשחק מחוץ לתור
- `INVALID Out of bounds` - קואורדינטות מחוץ ללוח
- `INVALID Cell already occupied` - התא תפוס
- `INVALID Game already ended` - המשחק הסתיים

## טיפול בשגיאות

### צד השרת

1. **Thread-safe operations** - כל הגישה למשחקים מוגנת ב-locks
2. **Validation מלאה** - כל קלט נבדק לפני ביצוע
3. **Exception handling** - טיפול בשגיאות ברמת ה-thread

### צד הלקוח

הלקוח שלך כבר מטפל ב:
- ניתוק לא צפוי
- הודעות אסינכרוניות
- parsing של פורמט הלוח

## הרחבות אפשריות

### 1. Reconnection

הוסף מזהה שחקן ייחודי:

```python
# בעת יצירה/הצטרפות:
player_id = generate_unique_id()
player.player_id = player_id
self.send(conn, f"PLAYERID {player_id}")

# בעת reconnect:
# CLIENT → SERVER: RECONNECT <player_id>
# SERVER → CLIENT: RESTORED <game_id> <symbol>
```

### 2. Spectator Mode

```python
# CLIENT → SERVER: SPECTATE <game_id>
# SERVER → CLIENT: SPECTATING
# שולח עדכוני BOARD ללא YOURTURN
```

### 3. Chat

```python
# CLIENT → SERVER: CHAT <message>
# SERVER → ALL: CHAT <player_symbol> <message>
```

### 4. Timeout

```python
# הוסף timer לכל תור
self.turn_timeout = 30  # 30 שניות
# אם עבר הזמן, עבור לשחקן הבא
```

### 5. Game History

```python
# שמור היסטוריית מהלכים:
game.history = []
# כל מהלך: (player, row, col, timestamp)
```

## בדיקת תקינות

### בדיקה 1: משחק בסיסי
```bash
# Terminal 1: Server
python server_main.py

# Terminal 2: Client 1
python client.py
> Create game with 2 players

# Terminal 3: Client 2
python client.py
> Join game 1
> Play until win/draw
```

### בדיקה 2: מספר משחקים במקביל
```bash
# צור 2 משחקים שונים
# וודא שהם לא משפיעים זה על זה
```

### בדיקה 3: מקרי קצה
- ניסיון לשחק מחוץ לתור
- ניסיון לתפוס תא תפוס
- ניסיון לשחק מחוץ ללוח
- ניסיון להצטרף למשחק מלא

## Debugging

### הפעלת logging מפורט

הוסף בתחילת `server_main.py`:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
```

### מעקב אחר מהלכים

כל הפעולות מודפסות ב-server:
```
[NEW CONNECTION] ('127.0.0.1', 54321)
[RECEIVED from ('127.0.0.1', 54321)] CREATE 2
[GAME CREATED] Game 1 by ('127.0.0.1', 54321) (2 players)
[SENT] CREATED 1
...
```

## שאלות נפוצות

**ש: איך לשנות את הפורט?**
```python
# ב-server_main.py וב-client.py:
PORT = 8080  # במקום 5000
```

**ש: איך לאפשר חיבורים מרחוק?**
```python
# ב-server_main.py:
HOST = '0.0.0.0'  # במקום '127.0.0.1'

# ב-client.py:
HOST = '<server_ip_address>'
```

**ש: איך להגביל מספר משחקים?**
```python
# הוסף ב-TicTacToeServer:
MAX_GAMES = 10

def handle_create(self, ...):
    if len(self.games) >= MAX_GAMES:
        self.send(conn, "Server is full")
        return
```

**ש: איך לשמור משחקים לאחר קריסה?**
```python
# השתמש ב-pickle או JSON:
import pickle

def save_games(self):
    with open('games.pkl', 'wb') as f:
        pickle.dump(self.games, f)

def load_games(self):
    with open('games.pkl', 'rb') as f:
        self.games = pickle.load(f)
```

## תיעוד נוסף

- `game_logic.py` - הלוגיקה עצמה מתועדת בקוד
- `server_main.py` - השרת מתועד בקוד
- `test_game.py` - דוגמאות שימוש

---

**בהצלחה!** 🎮
