import random
import heapq
import time
import pgzrun

# グローバル設定（表示設定）
SHOW_NUMBERS = True  # Trueなら数字を表示、Falseなら隠す

WIDTH = 600
HEIGHT = 350  # 下部にメッセージ表示用
TITLE = "8puzzle"

# 1人モード用
ONE_BOARD_SIZE = 300
ONE_TILE_SIZE = ONE_BOARD_SIZE // 3  # 100
DIFFICULTY = 0  # 非0セルの表示数（初期状態で隠す数）

# 2人対戦モード用（盤面を左右に配置）
TWO_MARGIN_LEFT   = 20
TWO_MARGIN_RIGHT  = 20
TWO_MARGIN_TOP    = 20
TWO_MARGIN_BOTTOM = 20
TWO_MARGIN_BETWEEN = 20
CPULEVEL = 30

available_width = WIDTH - TWO_MARGIN_LEFT - TWO_MARGIN_RIGHT - TWO_MARGIN_BETWEEN
TWO_BOARD_SIZE = min(available_width // 2, HEIGHT - TWO_MARGIN_TOP - TWO_MARGIN_BOTTOM)
TWO_TILE_SIZE = TWO_BOARD_SIZE // 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
RED   = (255, 0, 0)

# ============================
# ゲーム状態管理
# ============================
game_state = "menu"   # "menu": メニュー画面, "selectlevel": レベル選択, "game": ゲーム中
game_mode = None      # "one": 1人モード, "two": 2人対戦モード, "cpu": CPU対戦モード

# ----------------------------
# 1人モード用グローバル変数
# ----------------------------
one_board = None
one_move_count = 0
one_game_clear = False

# ----------------------------
# 2人対戦モード用グローバル変数
# ----------------------------
board1 = None       # Player 1 (左側)
board2 = None       # Player 2 (右側)
move_count1 = 0
move_count2 = 0
# 各プレイヤーの累積操作時間（操作中のみ更新）
p1_elapsed_time = 0
p2_elapsed_time = 0
# サイクル内の操作回数（0: 1Pのターン, 1: 2Pのターン, 2: サイクル終了）
cycle_moves = 0
winner = None       # "Player 1", "Player 2", "Draw" または None

# ----------------------------
# タイマー管理用（2人対戦）
# ----------------------------
last_update_time = 0
turn_start_time = 0

# ----------------------------
# 1人モード用共通変数
# ----------------------------
start_time = 0
freeze_elapsed = 0
feedback_message = ""

ROWS = 3
COLS = 3

# ============================
# 盤面操作関連の関数
# ============================
def init_board(hide_number: int):
    """
    解かれた状態の盤面を dict のリスト形式で返す。
    各セルは {n: n} （nが表示される）または n != 0 の場合はマスクされると {n: "*"} となる。
    引数 hide_number の数だけ、ランダムに非0セルの表示を "*" に変更する。
    0は常に {0:0} とする。
    """
    board = []
    nums = list(range(1, ROWS * COLS)) + [0]
    idx = 0
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            n = nums[idx]
            if n == 0:
                cell = {n: 0}
            else:
                cell = {n: n}  # 初期は数字表示
            row.append(cell)
            idx += 1
        board.append(row)
    
    # 非0セルの位置を収集
    positions = []
    for i in range(ROWS):
        for j in range(COLS):
            key = list(board[i][j].keys())[0]
            if key != 0:
                positions.append((i, j))
    # 隠すセル数を有効な数に調整
    hide_number = min(hide_number, len(positions))
    hide_positions = random.sample(positions, hide_number)
    for (i, j) in hide_positions:
        key = list(board[i][j].keys())[0]
        board[i][j] = {key: "*"}
    return board

def shuffle_board(bd, moves=100):
    directions = ['up', 'down', 'left', 'right']
    for _ in range(moves):
        move_tile_by_arrow(bd, random.choice(directions))

def is_solved(bd):
    """
    bd の各セルのキーを行順・列順に抽出し、[1,2,...,8,0] と一致するか判定する
    """
    goal = list(range(1, ROWS * COLS)) + [0]
    flat = []
    for i in range(ROWS):
        for j in range(COLS):
            key = list(bd[i][j].keys())[0]
            flat.append(key)
    return flat == goal

def get_blank_position(bd):
    """
    bd の中から、キーが 0 のセルの位置 (i, j) を返す
    """
    for i in range(len(bd)):
        for j in range(len(bd[0])):
            key = list(bd[i][j].keys())[0]
            if key == 0:
                return (i, j)
    return None

def move_tile_by_arrow(bd, direction):
    """
    矢印キー操作により、空白セルと隣接セルを入れ替える。
    例: 上キーの場合、空白セルの下側のセルと入れ替える。
    """
    pos = get_blank_position(bd)
    if pos is None:
        return False
    i, j = pos
    target = None
    if direction == 'up' and i < ROWS - 1:
        target = (i+1, j)
    elif direction == 'down' and i > 0:
        target = (i-1, j)
    elif direction == 'left' and j < COLS - 1:
        target = (i, j+1)
    elif direction == 'right' and j > 0:
        target = (i, j-1)
    if target:
        bd[i][j], bd[target[0]][target[1]] = bd[target[0]][target[1]], bd[i][j]
        return True
    return False

def move_tile_by_mouse(bd, clicked_row, clicked_col):
    """
    マウスでクリックされたセル (clicked_row, clicked_col) が
    空白セルに隣接していれば、入れ替える
    """
    blank = get_blank_position(bd)
    if blank is None:
        return False
    bi, bj = blank
    if ((abs(clicked_row - bi) == 1 and clicked_col == bj) or
        (abs(clicked_col - bj) == 1 and clicked_row == bi)):
        bd[bi][bj], bd[clicked_row][clicked_col] = bd[clicked_row][clicked_col], bd[bi][bj]
        return True
    return False

# 補助関数：盤面をタプル形式に変換する
def board_to_tuple(bd):
    """
    bd は dict のリスト形式（各セルは {n: 表示内容}）であるとする。
    盤面状態として、各セルのキー（元の数字）を行順・列順に並べたタプルを返す。
    """
    return tuple(list(bd[i][j].keys())[0] for i in range(ROWS) for j in range(COLS))

# 補助関数：マンハッタン距離を計算する
def manhattan_distance(state):
    distance = 0
    for index, value in enumerate(state):
        if value == 0:
            continue
        cur_i = index // COLS
        cur_j = index % COLS
        goal_i = (value - 1) // COLS
        goal_j = (value - 1) % COLS
        distance += abs(cur_i - goal_i) + abs(cur_j - goal_j)
    return distance

# evaluate_board(bd) を A* 用の評価値（ヒューリスティック値）として実装
def evaluate_board(bd):
    state = board_to_tuple(bd)
    return manhattan_distance(state)

# 盤面の隣接状態（状態遷移）を返す関数
def get_neighbors(state):
    """
    state はタプル形式の盤面状態。
    0 の位置（空白）の上下左右の移動可能な隣接状態を、
    (new_state, direction) の組で返す。
    なお、ここでの direction は、元のプログラムの move_tile_by_arrow() の仕様に合わせ、
    例えば、"up" は空白セルの下にあるタイルを空白側にスライドさせる操作とする。
    """
    neighbors = []
    idx = state.index(0)
    i = idx // COLS
    j = idx % COLS
    # 上キー操作: 空白が i, j で、i < ROWS-1なら、(i+1, j) と入れ替え
    if i < ROWS - 1:
        new_state = list(state)
        swap_idx = (i+1) * COLS + j
        new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
        neighbors.append((tuple(new_state), 'up'))
    # 下キー操作: i > 0なら、(i-1, j) と入れ替え
    if i > 0:
        new_state = list(state)
        swap_idx = (i-1) * COLS + j
        new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
        neighbors.append((tuple(new_state), 'down'))
    # 左キー操作: j < COLS-1なら、(i, j+1) と入れ替え
    if j < COLS - 1:
        new_state = list(state)
        swap_idx = i * COLS + (j+1)
        new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
        neighbors.append((tuple(new_state), 'left'))
    # 右キー操作: j > 0なら、(i, j-1) と入れ替え
    if j > 0:
        new_state = list(state)
        swap_idx = i * COLS + (j-1)
        new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
        neighbors.append((tuple(new_state), 'right'))
    return neighbors

# get_best_choice(bd) を A*アルゴリズムで実装
def get_best_choice(bd):
    """
    現在の盤面 bd から、A*アルゴリズムを用いて目標状態 (1,2,3,...,8,0) への最短解路を探索し、
    最初の移動（'up', 'down', 'left', 'right' のいずれか）を返す。
    解路が見つからなければ None を返す。
    """
    start_state = board_to_tuple(bd)
    goal_state = tuple(list(range(1, ROWS * COLS)) + [0])
    
    # A*探索用の優先度付きキュー
    # 各要素は (f, g, state, first_move) となる。
    # f = g + h,  g は実際のコスト, h はマンハッタン距離
    heap = []
    h = manhattan_distance(start_state)
    heapq.heappush(heap, (h, 0, start_state, None))
    visited = {start_state: 0}
    
    while heap:
        f, g, state, first_move = heapq.heappop(heap)
        if state == goal_state:
            return first_move  # 解路の最初の移動を返す
        for neighbor, direction in get_neighbors(state):
            new_g = g + 1
            if neighbor not in visited or new_g < visited[neighbor]:
                visited[neighbor] = new_g
                h = manhattan_distance(neighbor)
                new_f = new_g + h
                next_first_move = first_move if first_move is not None else direction
                heapq.heappush(heap, (new_f, new_g, neighbor, next_first_move))
    return None

# ============================
# ゲーム初期化処理
# ============================
def start_game():
    global one_board, one_move_count, one_game_clear
    global board1, board2, move_count1, move_count2, winner, cycle_moves
    global start_time, freeze_elapsed, feedback_message, p1_elapsed_time, p2_elapsed_time, last_update_time, turn_start_time

    feedback_message = ""
    freeze_elapsed = 0
    start_time = time.time()

    if game_mode == "one":
        one_board = init_board(DIFFICULTY)
        shuffle_board(one_board, moves=100)
        one_move_count = 0
        one_game_clear = False
    elif game_mode == "two" or game_mode == "cpu":
        base_board = init_board(DIFFICULTY)
        shuffle_board(base_board, moves=100)
        board1 = [row[:] for row in base_board]
        board2 = [row[:] for row in base_board]
        move_count1 = 0
        move_count2 = 0
        winner = None
        cycle_moves = 0
        p1_elapsed_time = 0
        p2_elapsed_time = 0
        turn_start_time = time.time()
        last_update_time = time.time()

# ============================
# 描画関連の関数
# ============================
def draw_board_at(bd, offset_x, offset_y, tile_size):
    for i in range(ROWS):
        for j in range(COLS):
            rect = Rect((offset_x + j * tile_size, offset_y + i * tile_size), (tile_size, tile_size))
            screen.draw.filled_rect(rect, WHITE)
            screen.draw.rect(rect, BLACK)
            cell = bd[i][j]
            # 各セルは辞書形式になっているので、最初のキーとその値を取得
            key = list(cell.keys())[0]
            value = cell[key]
            textcolor = BLACK
            if key == 0:
                text = ""
            elif one_move_count == 0:
                text = str(key)
                textcolor = BLACK if value!='*' else RED
            else:
                text = str(value)
                textcolor = BLACK
            x = offset_x + j * tile_size + tile_size // 2
            y = offset_y + i * tile_size + tile_size // 2
            screen.draw.text(text, (x, y), fontsize=int(tile_size * 0.8), color=textcolor, anchor=(0.5, 0.5))

def draw_menu_screen():
    screen.fill(GRAY)
    screen.draw.text("8puzzle", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=64, color=BLACK)
    one_button = Rect((WIDTH//2 - 70, HEIGHT//2 - 70), (150, 50))
    two_button = Rect((WIDTH//2 - 70, HEIGHT//2 + 0), (150, 50))
    three_button = Rect((WIDTH//2 - 70, HEIGHT//2 + 70), (150, 50))
    screen.draw.filled_rect(one_button, WHITE)
    screen.draw.rect(one_button, BLACK)
    screen.draw.text("One Player", center=one_button.center, fontsize=20, color=BLACK)
    screen.draw.filled_rect(two_button, WHITE)
    screen.draw.rect(two_button, BLACK)
    screen.draw.text("Two Player", center=two_button.center, fontsize=20, color=BLACK)
    screen.draw.filled_rect(three_button, WHITE)
    screen.draw.rect(three_button, BLACK)
    screen.draw.text("CPU Mode", center=three_button.center, fontsize=20, color=BLACK)

def draw_level_screen():
    screen.fill(GRAY)
    screen.draw.text("Select Level", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=64, color=BLACK)
    one_button = Rect((WIDTH//2 - 160, HEIGHT//2 - 20), (150, 50))
    two_button = Rect((WIDTH//2 + 10, HEIGHT//2 - 20), (150, 50))
    screen.draw.filled_rect(one_button, WHITE)
    screen.draw.rect(one_button, BLACK)
    screen.draw.text("Level 1", center=one_button.center, fontsize=20, color=BLACK)
    screen.draw.filled_rect(two_button, WHITE)
    screen.draw.rect(two_button, BLACK)
    screen.draw.text("Level 2", center=two_button.center, fontsize=20, color=BLACK)

def draw_game_screen():
    if game_mode == "one":
        screen.fill(GRAY)
        offset_x = (WIDTH - ONE_BOARD_SIZE) // 2
        offset_y = 0
        draw_board_at(one_board, offset_x, offset_y, ONE_TILE_SIZE)
        elapsed = freeze_elapsed if one_game_clear else int(time.time() - start_time)
        status_text = f"Moves: {one_move_count}   Time: {elapsed} sec"
        screen.draw.text(status_text, (10, HEIGHT - 45), fontsize=20, color=BLACK)
        screen.draw.text(feedback_message, (WIDTH//2, HEIGHT - 25), fontsize=20, color=BLACK, anchor=(0.5, 0.5))
        if one_game_clear:
            screen.draw.text("Press 'R' to restart", center=(WIDTH//2, HEIGHT//2), fontsize=32, color=BLACK)
    elif game_mode == "two" or game_mode == "cpu":
        screen.fill(GRAY)
        left_board_x = TWO_MARGIN_LEFT
        right_board_x = TWO_MARGIN_LEFT + TWO_BOARD_SIZE + TWO_MARGIN_BETWEEN
        board_y = TWO_MARGIN_TOP

        draw_board_at(board1, left_board_x, board_y, TWO_TILE_SIZE)
        draw_board_at(board2, right_board_x, board_y, TWO_TILE_SIZE)
        
        stat_y = board_y + TWO_BOARD_SIZE + 5
        p1_stat = f"P1 Moves: {move_count1}   Time: {int(p1_elapsed_time)} sec"
        p2_stat = f"P2 Moves: {move_count2}   Time: {int(p2_elapsed_time)} sec"
        screen.draw.text(p1_stat, (left_board_x, stat_y), fontsize=16, color=BLACK)
        screen.draw.text(p2_stat, (right_board_x, stat_y), fontsize=16, color=BLACK)
        
        if winner:
            screen.draw.text(f"{winner} wins! Press 'R' to restart", center=(WIDTH//2, HEIGHT - 30), fontsize=24, color=BLACK)
        else:
            # cycle_movesが0なら1Pのターン、1なら2Pのターン
            turn_text = "Player 1's turn" if cycle_moves == 0 else "Player 2's turn"
            screen.draw.text(turn_text, (WIDTH//2, 5), fontsize=24, color=BLACK, anchor=(0.5, 0))

def draw():
    if game_state == "menu":
        draw_menu_screen()
    elif game_state == "selectlevel":
        draw_level_screen()
    elif game_state == "game":
        draw_game_screen()

# ============================
# 入力処理
# ============================
def on_mouse_down(pos):
    global feedback_message, one_move_count, move_count1, move_count2, game_state, game_mode, cycle_moves, last_update_time, DIFFICULTY, CPULEVEL
    if game_state == "menu":
        one_button = Rect((WIDTH//2 - 70, HEIGHT//2 - 70), (150, 50))
        two_button = Rect((WIDTH//2 - 70, HEIGHT//2 + 0), (150, 50))
        three_button = Rect((WIDTH//2 - 70, HEIGHT//2 + 70), (150, 50))
        if one_button.collidepoint(pos):
            game_mode = "one"
            DIFFICULTY = 0
            game_state = "selectlevel"
        elif two_button.collidepoint(pos):
            game_mode = "two"
            DIFFICULTY = 0
            game_state = "game"
            start_game()
        elif three_button.collidepoint(pos):
            game_mode = "cpu"
            DIFFICULTY = 0
            game_state = "selectlevel"
            start_game()
        return

    if game_mode == "one" and game_state == "selectlevel":
        one_button = Rect((WIDTH//2 - 160, HEIGHT//2 - 20), (150, 50))
        two_button = Rect((WIDTH//2 + 10, HEIGHT//2 - 20), (150, 50))
        if one_button.collidepoint(pos):
            game_mode = "one"
            DIFFICULTY = 0
            game_state = "game"
            start_game()
        elif two_button.collidepoint(pos):
            game_mode = "one"
            DIFFICULTY = 2
            game_state = "game"
            start_game()
        return

    if game_mode == "cpu" and game_state == "selectlevel":
        one_button = Rect((WIDTH//2 - 160, HEIGHT//2 - 20), (150, 50))
        two_button = Rect((WIDTH//2 + 10, HEIGHT//2 - 20), (150, 50))
        if one_button.collidepoint(pos):
            game_mode = "cpu"
            DIFFICULTY = 0
            CPULEVEL = 30
            game_state = "game"
            start_game()
        elif two_button.collidepoint(pos):
            game_mode = "cpu"
            DIFFICULTY = 0
            CPULEVEL = 10
            game_state = "game"
            start_game()
        return

    if game_state == "game":
        if game_mode == "one":
            offset_x = (WIDTH - ONE_BOARD_SIZE) // 2
            offset_y = 0
            if offset_x <= pos[0] < offset_x + ONE_BOARD_SIZE and offset_y <= pos[1] < offset_y + ONE_BOARD_SIZE:
                clicked_col = (pos[0] - offset_x) // ONE_TILE_SIZE
                clicked_row = (pos[1] - offset_y) // ONE_TILE_SIZE
                if move_tile_by_mouse(one_board, clicked_row, clicked_col):
                    one_move_count += 1
                    feedback_message = ""
                else:
                    feedback_message = "Invalid move!"
        elif game_mode == "two":
            left_board_x = TWO_MARGIN_LEFT
            right_board_x = TWO_MARGIN_LEFT + TWO_BOARD_SIZE + TWO_MARGIN_BETWEEN
            board_y = TWO_MARGIN_TOP
            now = time.time()
            # cycle_moves == 0: Player 1's turn, 1: Player 2's turn
            if cycle_moves == 0:
                if left_board_x <= pos[0] < left_board_x + TWO_BOARD_SIZE and board_y <= pos[1] < board_y + TWO_BOARD_SIZE:
                    clicked_col = (pos[0] - left_board_x) // TWO_TILE_SIZE
                    clicked_row = (pos[1] - board_y) // TWO_TILE_SIZE
                    if move_tile_by_mouse(board1, clicked_row, clicked_col):
                        move_count1 += 1
                        cycle_moves = 1
                        last_update_time = now
                        feedback_message = ""
                    else:
                        feedback_message = "Invalid move for Player 1!"
            elif cycle_moves == 1:
                if right_board_x <= pos[0] < right_board_x + TWO_BOARD_SIZE and board_y <= pos[1] < board_y + TWO_BOARD_SIZE:
                    clicked_col = (pos[0] - right_board_x) // TWO_TILE_SIZE
                    clicked_row = (pos[1] - board_y) // TWO_TILE_SIZE
                    if move_tile_by_mouse(board2, clicked_row, clicked_col):
                        move_count2 += 1
                        cycle_moves = 2
                        last_update_time = now
                        feedback_message = ""
                    else:
                        feedback_message = "Invalid move for Player 2!"

def on_key_down(key):
    global feedback_message, one_move_count, move_count1, move_count2, cycle_moves, last_update_time, game_state
    if game_state == "menu":
        return
    elif game_state == "game":
        if key == keys.R:
            game_state = "menu"
            return
        if game_mode == "one":
            if one_game_clear:
                return
            moved = False
            if key == keys.UP:
                moved = move_tile_by_arrow(one_board, 'up')
            elif key == keys.DOWN:
                moved = move_tile_by_arrow(one_board, 'down')
            elif key == keys.LEFT:
                moved = move_tile_by_arrow(one_board, 'left')
            elif key == keys.RIGHT:
                moved = move_tile_by_arrow(one_board, 'right')
            if moved:
                one_move_count += 1
                feedback_message = ""
        elif game_mode == "two" or game_mode == "cpu":
            if winner is not None:
                return
            now = time.time()
            if cycle_moves == 0:
                moved = False
                if key == keys.UP:
                    moved = move_tile_by_arrow(board1, 'up')
                elif key == keys.DOWN:
                    moved = move_tile_by_arrow(board1, 'down')
                elif key == keys.LEFT:
                    moved = move_tile_by_arrow(board1, 'left')
                elif key == keys.RIGHT:
                    moved = move_tile_by_arrow(board1, 'right')
                if moved:
                    move_count1 += 1
                    cycle_moves = 1
                    last_update_time = now
                    feedback_message = ""
            elif cycle_moves == 1:
                moved = False
                if key == keys.W:
                    moved = move_tile_by_arrow(board2, 'up')
                elif key == keys.S:
                    moved = move_tile_by_arrow(board2, 'down')
                elif key == keys.A:
                    moved = move_tile_by_arrow(board2, 'left')
                elif key == keys.D:
                    moved = move_tile_by_arrow(board2, 'right')
                if moved:
                    move_count2 += 1
                    cycle_moves = 2
                    last_update_time = now
                    feedback_message = ""

# ============================
# 更新処理
# ============================
def update():
    global one_game_clear, freeze_elapsed, winner, feedback_message
    global p1_elapsed_time, p2_elapsed_time, last_update_time, cycle_moves, turn_start_time
    global move_count2, cycle_moves
    if game_state == "menu":
        return
    elif game_state == "selectlevel":
        return
    elif game_mode == "one":
        if not one_game_clear and is_solved(one_board):
            freeze_elapsed = int(time.time() - start_time)
            feedback_message = "Congratulations! Press 'R' to restart."
            one_game_clear = True
    elif game_mode == "two" or game_mode == "cpu":
        now = time.time()
        # 現在のサイクル中、対応するプレイヤーの経過時間を更新
        if cycle_moves == 0:
            p1_elapsed_time += now - last_update_time
        elif cycle_moves == 1:
            p2_elapsed_time += now - last_update_time
            if game_mode == "cpu":
                # CPUの場合、Player 2の操作を自動化
                next_move = get_best_choice(board2)
                if move_count2 <= CPULEVEL:
                    # CPULEVEL以内の場合はランダムに操作を
                    while True:
                        if move_tile_by_arrow(board2, random.choice(['up', 'down', 'left', 'right'])):
                            move_tile_by_arrow(board2, next_move)
                            break
                else:
                    move_tile_by_arrow(board2, next_move)
                move_count2 += 1
                cycle_moves = 2
                last_update_time = now
        last_update_time = now

        # サイクル終了時（cycle_moves == 2）の勝敗判定を行う
        if cycle_moves == 2 and winner is None:
            solved1 = is_solved(board1)
            solved2 = is_solved(board2)
            if solved1 or solved2:
                cycle_moves = 4 #決着状態
                if solved1 and not solved2:
                    winner = "Player 1"
                elif solved2 and not solved1:
                    winner = "Player 2"
                elif solved1 and solved2:
                    if p1_elapsed_time < p2_elapsed_time:
                        winner = "Player 1"
                    elif p2_elapsed_time < p1_elapsed_time:
                        winner = "Player 2"
                    else:
                        winner = "Draw"
            else:
                # どちらも未解ならサイクルをリセットして次の操作サイクルへ
                cycle_moves = 0
                turn_start_time = time.time()

pgzrun.go()
