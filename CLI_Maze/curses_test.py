import random
import curses

class MazeGame:
    # コンストラクタ
    def __init__(self):
        #マップ
        self.maze = [
            ["■", "■", "■", "■", "■","■","■","■","■","■","■","■","■","■","■","■","■"],
            ["■", " ", " ", " ", " "," "," "," "," "," ","■"," "," "," "," ","○","■"],
            ["■", " ", " ", "■", "■","■","■","■","■"," ","■"," ","■"," ","■"," ","■"],
            ["■", " ", " ", "■", " "," "," "," "," "," ","■"," "," "," "," "," ","■"],
            ["■", " ", " ", "■", "■","■","■","■"," "," ","■"," ","■"," ","■"," ","■"],
            ["■", " ", " ", "■", " "," "," ","■"," "," ","■","●"," "," "," "," ","■"],
            ["S", " ", " ", "■", " "," "," ","■","■","■","■","■","■","■","■","■","■"],
            ["■", " ", " ", " ", " ","■"," ","■"," "," "," ","●","■"," "," "," ","■"],
            ["■", " ", " ", " ", " "," "," ","■"," ","■"," "," ","■"," "," "," ","■"],
            ["■", " ", " ", " ", " ","■"," ","■"," "," ","■"," "," "," ","■"," ","■"],
            ["■", "■", " ", "■", " "," "," ","■"," "," "," ","■","■"," "," "," ","■"],
            ["■", "■", "○", "■", " "," "," ","■"," "," "," "," ","■"," "," "," ","■"],
            ["■", "■", "■", "■", "■","■","■","■","■","■","■","■","■","■","■"," ","■"]
        ]
        # ワープの座標組み合わせ
        self.warp_points = {
            # ○ のセット
            (1, 15): (11, 2),
            (11, 2): (1, 15),
            # ● のセット
            (7, 11): (5, 11),
            (5, 11): (7, 11)
        }
        # 各設定の座標
        self.weapon_pos = {(5, 8)}
        self.player_pos = (6, 0)
        self.enemies = [
            {"pos": (8, 5), "type": "random"},
            {"pos": (1, 11), "type": "chase"},
            {"pos": (8, 15), "type": "patrol"}
        ]
        self.key_pos = {(3, 13), (11,11)}
        self.goal_pos = {(12, 15)}
        self.door_pos = {(10, 2)}
        self.switch_pos = {(3, 4), (8, 6)}
        self.spawn_points = {(6, 5), (10, 5), (1, 11), (5, 15), (10, 10)}
        # キー、武器の所持状態
        self.has_key = False
        self.has_weapon = False
        # 歩数のカウント
        self.counter = 0

    # 敵の行動制限
    def is_valid_move_for_enemy(self, x, y):
        return (0 <= x < len(self.maze) and
                0 <= y < len(self.maze[0]) and
                self.maze[x][y] != "■")
    # 敵の座標の取得
    def get_enemy_positions(self):
        return [e["pos"] for e in self.enemies]
    # マップに表示するアイコンの設定
    def print_maze(self, stdscr):
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                pos = (i, j)
                char = cell
                color = curses.color_pair(0)
                # 重なったときにプレイヤーよりエネミーを優先させたいためエネミーを先に
                if pos in self.get_enemy_positions():
                    char = "E"
                    color = curses.color_pair(1)
                elif pos == self.player_pos:
                    char = "P"
                    color = curses.color_pair(2)
                elif pos in self.key_pos:
                    char = "K"
                    color = curses.color_pair(3)
                elif pos in self.goal_pos:
                    char = "G"
                    color = curses.color_pair(4)
                elif pos in self.door_pos:
                    char = "-"
                elif pos in self.switch_pos:
                    char = "▲"
                    color = curses.color_pair(5)
                elif pos in self.weapon_pos:
                    char = "?"

                stdscr.addstr(i, j * 2, char + " ", color)
        # 右側に表示する、プレイヤーの状況と行動回数
        info_x = len(self.maze[0]) * 2 + 2
        stdscr.addstr(0, info_x, "----------------")
        stdscr.addstr(1, info_x, f"カギ : {'所持' if self.has_key else '未所持'}")
        stdscr.addstr(2, info_x, f"武器 : {'所持' if self.has_weapon else '未所持'}")
        stdscr.addstr(3, info_x, f"敵の数 : {len(self.get_enemy_positions())}")
        stdscr.addstr(4, info_x, f"行動回数 : {self.counter}")
        stdscr.addstr(5, info_x, "----------------")
    # プレイヤーの挙動設定
    def move_player(self, direction):
        x, y = self.player_pos
        # 矢印キーで移動
        if direction == curses.KEY_UP and x > 0:
            new_pos = (x - 1, y)
        elif direction == curses.KEY_DOWN and x < len(self.maze) - 1:
            new_pos = (x + 1, y)
        elif direction == curses.KEY_LEFT and y > 0:
            new_pos = (x, y - 1)
        elif direction == curses.KEY_RIGHT and y < len(self.maze[0]) - 1:
            new_pos = (x, y + 1)
        # 以下二つはテストコマンド
        elif direction == ord('x'):
            new_pos = (12, 15)
        elif direction == ord('y'):
            new_pos = (6, 0)
        # 矢印キー以外はその場で行動を終える
        else:
            self.counter += 1
            return
        self.counter += 1
        # 移動制限
        if self.maze[new_pos[0]][new_pos[1]] != "■" and new_pos not in self.door_pos:
            self.player_pos = new_pos
    # エネミーの挙動設定
    def move_enemies(self):
        new_enemies = []
        px, py = self.player_pos
        occupied_positions = set(self.get_enemy_positions())  # 現在の敵位置（移動前）

        for enemy in self.enemies:
            ex, ey = enemy["pos"]
            etype = enemy["type"]

            occupied_positions.discard((ex, ey))
            # ランダムの場合
            if etype == "random":
                new_pos = self.move_enemy_random(ex, ey, occupied_positions)
            # 追跡してくる場合
            elif etype == "chase":
                new_pos = self.move_enemy_chase(ex, ey, px, py, occupied_positions)
            # 巡回の場合
            elif etype == "patrol":
                new_pos, next_idx = self.move_enemy_patrol(enemy, occupied_positions)
            else:
                new_pos = (ex, ey)

            # 移動先が他の敵と被っていないか最終チェック
            if new_pos in occupied_positions:
                new_pos = (ex, ey)

            # 移動済みの敵の位置を追加しておく
            occupied_positions.add(new_pos)

            new_enemy = enemy.copy()
            new_enemy["pos"] = new_pos
            if etype == "patrol":
                new_enemy["path_index"] = next_idx
            new_enemies.append(new_enemy)

        self.enemies = new_enemies

    # 敵の挙動・ランダム
    def move_enemy_random(self, ex, ey, occupied_positions):
        moves = [(0,1), (0,-1), (1,0), (-1,0)]
        random.shuffle(moves)
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if self.is_valid_move_for_enemy(nx, ny) and (nx, ny) not in occupied_positions:
                return (nx, ny)
        return (ex, ey)

    # 敵の挙動・追跡
    def move_enemy_chase(self, ex, ey, px, py, occupied_positions):
        moves = [(0,1), (0,-1), (1,0), (-1,0)]
        move_distances = []
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if self.is_valid_move_for_enemy(nx, ny) and (nx, ny) not in occupied_positions:
                dist = abs(px - nx) + abs(py - ny)
                move_distances.append(((nx, ny), dist))
        if move_distances:
            move_distances.sort(key=lambda x: x[1])
            return move_distances[0][0]
        return (ex, ey)

    # 敵の挙動・巡回
    def move_enemy_patrol(self, enemy, occupied_positions):
        if "path" not in enemy:
            # 相対移動（dy, dx）
            enemy["path"] = [(0, -1), (0, -1), (1, 0), (1, 0), (0, 1), (0, 1), (-1, 0), (-1, 0)]
            enemy["path_index"] = 0

        path = enemy["path"]
        idx = enemy["path_index"]
        dx, dy = path[idx]

        # 現在位置を取得
        x, y = enemy["pos"]
        nx, ny = x + dx, y + dy

        # 次のインデックス（ループさせる）
        next_idx = (idx + 1) % len(path)

        # 有効な移動かどうかを判定
        if self.is_valid_move_for_enemy(nx, ny) and (nx, ny) not in occupied_positions:
            return (nx, ny), next_idx

        # 移動できない場合は位置そのまま、インデックスも進めない
        return (x, y), idx


    # エネミーのスポーン設定
    def spawn_random_enemy(self, stdscr):
        candidates = [pos for pos in self.spawn_points
                      if pos != self.player_pos and pos not in self.get_enemy_positions()]
        if candidates:
            new_pos = random.choice(candidates)
            new_type = random.choice(["random", "chase"])
            self.enemies.append({"pos": new_pos, "type": new_type})
            stdscr.addstr(len(self.maze)+1, 0, "敵が出現した！", curses.color_pair(1) | curses.A_BOLD)
            stdscr.refresh()
            curses.napms(1000)

    def play(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(False) 
        # 色の設定
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        while True:
            # ゲームの初期化
            self.__init__()  # ゲーム状態リセット
            self.counter = 0

            game_over = False
            while game_over == False:
                stdscr.clear()

                self.print_maze(stdscr)

                # 説明文
                stdscr.addstr(len(self.maze)+3, 0, "--------------------------------------------------------------------------------------------------".ljust(80))
                stdscr.addstr(len(self.maze)+4, 0, "'S': スタート, 'G': ゴール, 'E': エネミー, '?': アイテム".ljust(80))
                stdscr.addstr(len(self.maze)+5, 0, "'○','●': ワープ, '-': ドア, 'K': ゴールのカギ, '▲': ドアのスイッチ".ljust(80))
                stdscr.addstr(len(self.maze)+6, 0, "移動は矢印キー(↑、↓、←、→), Qで終了、Rでリセット、その他のものを入力するとその場で行動を終えます。".ljust(80))
                stdscr.addstr(len(self.maze)+7, 0, "--------------------------------------------------------------------------------------------------".ljust(80))

                stdscr.refresh()

                move = stdscr.getch()
                if move == ord('q'):
                    return
                elif move == ord('r'):
                    self.__init__()  # ゲーム状態を初期化
                    self.counter = 0
                    stdscr.addstr(len(self.maze)+1, 0, "リセットします", curses.A_REVERSE)
                    stdscr.refresh()
                    curses.napms(1000)
                    continue  # すぐにループの先頭へ戻る（画面更新も行う）
                # プレイヤーが動く
                self.move_player(move)

                self.print_maze(stdscr)  # 最新の迷路を再描画

                # カギと座標が重なった場合
                if self.player_pos in self.key_pos:
                    self.has_key = True
                    self.key_pos.clear()
                    stdscr.addstr(len(self.maze)+1, 0, "カギを拾いました！", curses.A_BOLD)
                    stdscr.refresh()
                    curses.napms(800)
                # スイッチと座標が重なった場合
                if self.player_pos in self.switch_pos:
                    self.door_pos.clear()
                    self.switch_pos.clear()
                    stdscr.addstr(len(self.maze)+1, 0, "扉が開いた!", curses.A_BOLD)
                    stdscr.refresh()
                    curses.napms(800)
                # 敵と座標が重なった場合
                if self.player_pos in self.get_enemy_positions():
                    #　武器を持っている場合
                    if self.has_weapon:
                        self.enemies = [e for e in self.enemies if e["pos"] != self.player_pos]
                        stdscr.addstr(len(self.maze)+1, 0, "敵を倒しました！", curses.color_pair(3) | curses.A_BOLD)
                        stdscr.refresh()
                        curses.napms(800)
                    # 武器を持っていない場合
                    else:
                        self.print_maze(stdscr)
                        stdscr.addstr(len(self.maze)+1, 0, "敵に捕まりました！ゲームオーバー。", curses.color_pair(1) | curses.A_BOLD)
                        stdscr.refresh()
                        curses.napms(2000)
                        game_over = True
                        continue
                # ワープの座標と重なった場合
                if self.player_pos in self.warp_points:
                    self.player_pos = self.warp_points[self.player_pos]
                    stdscr.addstr(len(self.maze)+1, 0, "ワープしました！", curses.color_pair(3) | curses.A_BOLD)
                    stdscr.refresh()
                    curses.napms(800)
                # 剣の座標と重なった場合
                if self.player_pos in self.weapon_pos:
                    self.has_weapon = True
                    self.weapon_pos.remove(self.player_pos)
                    stdscr.addstr(len(self.maze)+1, 0, "剣を入手しました！", curses.color_pair(3) | curses.A_BOLD)
                    stdscr.refresh()
                    curses.napms(800)
                # ゴールの座標と重なった場合
                if self.player_pos in self.goal_pos:
                    # カギを持っていた場合
                    if self.has_key:
                        self.print_maze(stdscr)
                        stdscr.addstr(len(self.maze)+1, 0, f"ゴールに到達しました！おめでとうございます！", curses.A_BOLD)
                        stdscr.addstr(len(self.maze)+2, 0, f"ゴールまでに{self.counter}回動きました。", curses.A_BOLD)
                        stdscr.refresh()
                        curses.napms(3000)
                        break
                    # カギを持っていなかった場合
                    else:
                        stdscr.addstr(len(self.maze)+1, 0, "鍵が必要です。", curses.color_pair(4))
                        stdscr.refresh()
                        curses.napms(800)
                # 敵が動く
                self.move_enemies()

                self.print_maze(stdscr)  # 最新の迷路を再描画

                # 再度敵の座標との関係を確認
                if self.player_pos in self.get_enemy_positions():
                    if self.has_weapon:
                        self.enemies = [e for e in self.enemies if e["pos"] != self.player_pos]
                        stdscr.addstr(len(self.maze)+1, 0, "敵を倒しました！", curses.color_pair(3) | curses.A_BOLD)
                        stdscr.refresh()
                        curses.napms(800)
                    else:
                        self.print_maze(stdscr)
                        stdscr.addstr(len(self.maze)+1, 0, "敵に捕まりました！ゲームオーバー。", curses.color_pair(1) | curses.A_BOLD)
                        stdscr.refresh()
                        curses.napms(2000)
                        game_over = True
                        continue
                # 歩数を確認して条件を満たしていれば敵を増やす
                if(len(self.get_enemy_positions()) != 8):
                    if self.counter % 15 == 0:
                        self.spawn_random_enemy(stdscr)
            # ゲームオーバー時のリトライ処理
            if game_over == True:
                stdscr.clear()
                stdscr.addstr(0, 0, "リトライしますか?(y/n)")
                stdscr.refresh()
                while True:
                    key = stdscr.getch()
                    if key in (ord('y'), ord('Y')):
                        break  # リトライ→外側のループ再開
                    elif key in (ord('n'), ord('N')):
                        return  # 完全終了
            else:
                return

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: MazeGame().play(stdscr))
