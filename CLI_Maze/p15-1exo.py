import random

# 定数
EMPTY = 0
BLACK = 1
WHITE = 2
DRAW = 3
SIZE = 8
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

# グローバル変数
board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
turn = BLACK
log = []

# 表示用
def piece_symbol(value):
    return {EMPTY: '.', BLACK: '●', WHITE: '○'}.get(value, '?')

def show_board():
    s = '  ' + ' '.join(str(i) for i in range(SIZE)) + '\n'
    for i in range(SIZE):
        s += str(i) + ' ' + ' '.join(piece_symbol(cell) for cell in board[i]) + '\n'
    return s

# 初期化
def init_board():
    global board
    board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    mid = SIZE // 2
    board[mid-1][mid-1] = WHITE
    board[mid][mid] = WHITE
    board[mid-1][mid] = BLACK
    board[mid][mid-1] = BLACK

def init_turn():
    global turn
    turn = BLACK

def change_turn():
    global turn
    turn = BLACK if turn == WHITE else WHITE

def opponent(t):
    return BLACK if t == WHITE else WHITE

# 手の合法性
def is_on_board(i, j):
    return 0 <= i < SIZE and 0 <= j < SIZE

def is_valid_move(i, j, t):
    if not is_on_board(i, j) or board[i][j] != EMPTY:
        return False

    opp = opponent(t)
    for di, dj in DIRECTIONS:
        ni, nj = i + di, j + dj
        found_opponent = False
        while is_on_board(ni, nj) and board[ni][nj] == opp:
            ni += di
            nj += dj
            found_opponent = True
        if found_opponent and is_on_board(ni, nj) and board[ni][nj] == t:
            return True
    return False

def get_valid_moves(t):
    return [(i, j) for i in range(SIZE) for j in range(SIZE) if is_valid_move(i, j, t)]

# 石をひっくり返す
def apply_move(i, j, t):
    board[i][j] = t
    opp = opponent(t)
    for di, dj in DIRECTIONS:
        ni, nj = i + di, j + dj
        to_flip = []
        while is_on_board(ni, nj) and board[ni][nj] == opp:
            to_flip.append((ni, nj))
            ni += di
            nj += dj
        if is_on_board(ni, nj) and board[ni][nj] == t:
            for fi, fj in to_flip:
                board[fi][fj] = t

# 勝敗判定
def count_pieces():
    b = sum(row.count(BLACK) for row in board)
    w = sum(row.count(WHITE) for row in board)
    return b, w

def get_winner():
    b, w = count_pieces()
    if b > w:
        return BLACK
    elif w > b:
        return WHITE
    else:
        return DRAW

# AI
def ai_move():
    moves = get_valid_moves(turn)
    return random.choice(moves) if moves else None

# メインゲーム
def play():
    global log
    init_board()
    init_turn()
    log = []

    while True:
        moves = get_valid_moves(turn)
        print(show_board())
        print(f"{'●' if turn == BLACK else '○'} の番です")

        if not moves:
            print("合法手がありません。パスします。")
            change_turn()
            if not get_valid_moves(turn):
                break
            continue

        if turn == BLACK:
            # 人間のターン
            while True:
                try:
                    row = int(input("行を入力: "))
                    col = int(input("列を入力: "))
                    if (row, col) in moves:
                        break
                    print("その手は打てません。")
                except:
                    print("正しい形式で入力してください。")
        else:
            # AIターン
            row, col = ai_move()
            print(f"AI が ({row}, {col}) に打ちました。")

        apply_move(row, col, turn)
        log.append([row, col, turn])
        change_turn()

    # 終局
    print(show_board())
    b, w = count_pieces()
    print(f"●: {b} vs ○: {w}")
    winner = get_winner()
    if winner == DRAW:
        print("引き分けです！")
    elif winner == BLACK:
        print("AI（●）の勝ちです！")
    else:
        print("あなた（○）の勝ちです！")

    print("棋譜:")
    for move in log:
        print(move)

# エントリーポイント
if __name__ == '__main__':
    print("オセロ（リバーシ）")
    play()
