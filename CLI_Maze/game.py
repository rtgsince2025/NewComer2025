import curses
import random
from constants import MAZE_MAP, WARP_POINTS, COLOR_PAIR, ITEM_POSITIONS, ITEM_EFFECTS, ITEM_DISPLAY_NAMES
from enemy_logic import move_enemies, spawn_random_enemy

class MazeGame:
    def __init__(self):
        self.maze = [row[:] for row in MAZE_MAP]
        self.warp_points = WARP_POINTS
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
        self.has_key = False
        self.has_weapon = False
        self.counter = 0
        self.item_positions = set(ITEM_POSITIONS)
        self.player_effects = {
            "has_weapon": False,
            "has_shield": False,
            "dash": False  # ← 追加
        }
        self.inventory = None  # 所持アイテム（None または "sword" など）

    def get_enemy_positions(self):
        return [e["pos"] for e in self.enemies]

    def is_valid_move_for_enemy(self, x, y):
        return 0 <= x < len(self.maze) and 0 <= y < len(self.maze[0]) and self.maze[x][y] != "■"

    def print_maze(self, stdscr):
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                pos = (i, j)
                char = cell
                color = curses.color_pair(0)
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
                elif pos in self.item_positions:
                    char = "?"

                stdscr.addstr(i, j * 2, char + " ", color)

        info_x = len(self.maze[0]) * 2 + 2
        stdscr.addstr(0, info_x, "----------------")
        stdscr.addstr(1, info_x, f"カギ : {'所持' if self.has_key else '未所持'}")
        item_name = ITEM_DISPLAY_NAMES.get(self.inventory, "なし") if self.inventory else "なし"
        stdscr.addstr(2, info_x, f"所持アイテム : {item_name}")
        stdscr.addstr(3, info_x, f"敵の数 : {len(self.get_enemy_positions())}")
        stdscr.addstr(4, info_x, f"行動回数 : {self.counter}")
        stdscr.addstr(5, info_x, "----------------")

    def move_player(self, direction):
        x, y = self.player_pos
        dx, dy = 0, 0
        # 通常の移動量
        if direction == curses.KEY_UP:
            dx = -1
        elif direction == curses.KEY_DOWN:
            dx = 1
        elif direction == curses.KEY_LEFT:
            dy = -1
        elif direction == curses.KEY_RIGHT:
            dy = 1
        elif direction == ord('x'):
            self.player_pos = (12, 15)
            self.counter += 1
            return
        elif direction == ord('y'):
            self.player_pos = (6, 0)
            self.counter += 1
            return
        else:
            self.counter += 1
            return

        # 移動量を2倍にするかチェック
        steps = 2 if self.player_effects.get("dash") else 1
        self.player_effects["dash"] = False  # 使い終わったら消費

        for _ in range(steps):
            new_x = self.player_pos[0] + dx
            new_y = self.player_pos[1] + dy
            new_pos = (new_x, new_y)

            if (0 <= new_x < len(self.maze) and
                0 <= new_y < len(self.maze[0]) and
                self.maze[new_x][new_y] != "■" and
                new_pos not in self.door_pos):
                self.player_pos = new_pos
            else:
                break  # 壁 or ドアにぶつかったら止まる

        self.counter += 1

    def play(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(False)
        curses.start_color()
        for i, (fg, bg) in COLOR_PAIR.items():
            curses.init_pair(i, fg, bg)

        while True:
            self.__init__()
            self.counter = 0
            game_over = False

            while not game_over:
                stdscr.clear()
                self.print_maze(stdscr)

                stdscr.addstr(len(self.maze)+3, 0, "--------------------------------------------------------------------------------------------------")
                stdscr.addstr(len(self.maze)+4, 0, "'S': スタート, 'G': ゴール, 'E': エネミー, '?': アイテム")
                stdscr.addstr(len(self.maze)+5, 0, "'○','●': ワープ, '-': ドア, 'K': ゴールのカギ, '▲': ドアのスイッチ")
                stdscr.addstr(len(self.maze)+6, 0, "移動: 矢印キー / 終了: Q / リセット: R / アイテム: A(アイテムを持っている場合)")
                stdscr.addstr(len(self.maze)+7, 0, "--------------------------------------------------------------------------------------------------")

                stdscr.refresh()
                move = stdscr.getch()

                if move == ord('q'):
                    return
                elif move == ord('r'):
                    self.__init__()
                    self.counter = 0
                    stdscr.addstr(len(self.maze)+1, 0, "リセットします", curses.A_REVERSE)
                    stdscr.refresh()
                    curses.napms(1000)
                    continue
                elif move == ord('a') and self.inventory is not None:
                    if self.inventory == "sword":
                        self.player_effects["has_weapon"] = True
                    elif self.inventory == "shield":
                        self.player_effects["has_shield"] = True
                    elif self.inventory == "dash":
                        self.player_effects["dash"] = True

                    display_name = ITEM_DISPLAY_NAMES.get(self.inventory, self.inventory.upper())
                    stdscr.addstr(len(self.maze)+1, 0, f"{display_name} を使用しました！", curses.color_pair(4) | curses.A_BOLD)
                    self.inventory = None
                    stdscr.refresh()
                    curses.napms(800)

                    continue

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
                    if self.player_effects["has_weapon"]:
                        # 敵を倒す
                        self.enemies = [e for e in self.enemies if e["pos"] != self.player_pos]
                        self.player_effects["has_weapon"] = False
                        stdscr.addstr(len(self.maze)+1, 0, "敵を倒した！", curses.color_pair(3) | curses.A_BOLD)
                        stdscr.addstr(len(self.maze)+2, 0, "剣が壊れてしまった...", curses.color_pair(3) | curses.A_BOLD)
                    elif self.player_effects["has_shield"]:
                        self.player_effects["has_shield"] = False
                        stdscr.addstr(len(self.maze)+1, 0, "バリアで敵を防いだ！", curses.color_pair(5) | curses.A_BOLD)
                        stdscr.addstr(len(self.maze)+2, 0, "バリアが壊れてしまった...", curses.color_pair(5) | curses.A_BOLD)
                    else:
                        stdscr.addstr(len(self.maze)+1, 0, "敵に捕まった！ゲームオーバー。", curses.color_pair(1) | curses.A_BOLD)
                        game_over = True
                        stdscr.refresh()
                        curses.napms(2000)
                        continue
                    stdscr.refresh()
                    curses.napms(800)
                # ワープの座標と重なった場合
                if self.player_pos in self.warp_points:
                    self.player_pos = self.warp_points[self.player_pos]
                    stdscr.addstr(len(self.maze)+1, 0, "ワープしました！", curses.color_pair(3) | curses.A_BOLD)
                    stdscr.refresh()
                    curses.napms(800)
                # アイテムの座標と重なった場合
                if self.player_pos in self.item_positions:
                    self.item_positions.remove(self.player_pos)

                    if self.inventory is not None:
                        stdscr.addstr(len(self.maze)+1, 0, "すでにアイテムを所持しています！", curses.color_pair(3) | curses.A_BOLD)
                    else:
                        self.inventory = random.choice(ITEM_EFFECTS)
                        display_name = ITEM_DISPLAY_NAMES.get(self.inventory, self.inventory.upper())
                        stdscr.addstr(len(self.maze)+1, 0, f"{display_name} を手に入れた！ (Aキーで使用)", curses.color_pair(3) | curses.A_BOLD)

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

                self.enemies = move_enemies(self)

                # 再度敵の座標との関係を確認
                if self.player_pos in self.get_enemy_positions():
                    if self.player_effects["has_weapon"]:
                        # 敵を倒す
                        self.enemies = [e for e in self.enemies if e["pos"] != self.player_pos]
                        stdscr.addstr(len(self.maze)+1, 0, "敵を倒した！", curses.color_pair(3) | curses.A_BOLD)
                    elif self.player_effects["has_shield"]:
                        self.player_effects["has_shield"] = False
                        stdscr.addstr(len(self.maze)+1, 0, "バリアで敵を防いだ！", curses.color_pair(5) | curses.A_BOLD)
                    else:
                        stdscr.addstr(len(self.maze)+1, 0, "敵に捕まった！ゲームオーバー。", curses.color_pair(1) | curses.A_BOLD)
                        game_over = True
                        stdscr.refresh()
                        curses.napms(2000)
                        continue
                    stdscr.refresh()
                    curses.napms(800)
                # 歩数を確認して条件を満たしていれば敵を増やす
                if len(self.get_enemy_positions()) < 8 and self.counter % 15 == 0:
                    spawn_random_enemy(self, stdscr)

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
