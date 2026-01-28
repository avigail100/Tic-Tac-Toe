SYMBOLS = ['X', 'O', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
EMPTY = None


class Player:
    def __init__(self, player_id, symbol):
        self.player_id = player_id
        self.symbol = symbol
