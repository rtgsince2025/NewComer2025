import random
import curses

def is_valid_enemy_move(game, x, y, occupied):
    return game.is_valid_move_for_enemy(x, y) and (x, y) not in occupied

def move_enemy_random(game, ex, ey, occupied):
    moves = [(0,1), (0,-1), (1,0), (-1,0)]
    random.shuffle(moves)
    for dx, dy in moves:
        nx, ny = ex + dx, ey + dy
        if is_valid_enemy_move(game, nx, ny, occupied):
            return (nx, ny)
    return (ex, ey)

def move_enemy_chase(game, ex, ey, px, py, occupied):
    moves = [(0,1), (0,-1), (1,0), (-1,0)]
    best = (ex, ey)
    min_dist = abs(px - ex) + abs(py - ey)
    for dx, dy in moves:
        nx, ny = ex + dx, ey + dy
        if is_valid_enemy_move(game, nx, ny, occupied):
            dist = abs(px - nx) + abs(py - ny)
            if dist < min_dist:
                best = (nx, ny)
                min_dist = dist
    return best

def move_enemy_patrol(game, enemy, occupied):
    if "path" not in enemy:
        enemy["path"] = [(0,-1), (0,-1), (1,0), (1,0), (0,1), (0,1), (-1,0), (-1,0)]
        enemy["path_index"] = 0
    path = enemy["path"]
    idx = enemy["path_index"]
    dx, dy = path[idx]
    x, y = enemy["pos"]
    nx, ny = x + dx, y + dy
    next_idx = (idx + 1) % len(path)
    if is_valid_enemy_move(game, nx, ny, occupied):
        return (nx, ny), next_idx
    return (x, y), idx

def move_enemies(game):
    new_enemies = []
    occupied = set(game.get_enemy_positions())
    px, py = game.player_pos

    for enemy in game.enemies:
        ex, ey = enemy["pos"]
        etype = enemy["type"]
        occupied.discard((ex, ey))

        if etype == "random":
            new_pos = move_enemy_random(game, ex, ey, occupied)
        elif etype == "chase":
            new_pos = move_enemy_chase(game, ex, ey, px, py, occupied)
        elif etype == "patrol":
            new_pos, next_idx = move_enemy_patrol(game, enemy, occupied)
        else:
            new_pos = (ex, ey)

        if new_pos in occupied:
            new_pos = (ex, ey)

        occupied.add(new_pos)
        new_enemy = enemy.copy()
        new_enemy["pos"] = new_pos
        if etype == "patrol":
            new_enemy["path_index"] = next_idx
        new_enemies.append(new_enemy)

    return new_enemies

def spawn_random_enemy(game, stdscr):
    candidates = [pos for pos in game.spawn_points
                  if pos != game.player_pos and pos not in game.get_enemy_positions()]
    if candidates:
        new_pos = random.choice(candidates)
        new_type = random.choice(["random", "chase"])
        game.enemies.append({"pos": new_pos, "type": new_type})
        stdscr.addstr(len(game.maze)+1, 0, "敵が出現した！", curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(1000)
