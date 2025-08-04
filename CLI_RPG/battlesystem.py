import random
import time
import msvcrt
from player_characters import Wizard, Healer, Support
from enemy_characters  import Enemy
from wcwidth  import wcswidth
from colorama import Fore, Style, init
init()

def pad_to_width(text, width):
    pad_len = width - wcswidth(text)
    return text + ' ' * pad_len

def flush_input():
    while msvcrt.kbhit():
        msvcrt.getch()  # 入力バッファに残っているキーを読み捨てる

def konami_code_listener(timeout=3):
    """
    コナミコマンドを入力できたか判定（猶予3秒&途中ミスで失敗判定可能）
    """
    code = [b'H', b'H', b'P', b'P', b'K', b'M', b'K', b'M', b'B', b'A']  # ↑↑↓↓←→←→BA
    index = 0
    start_time = time.time()

    while time.time() - start_time < timeout:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':
                key = msvcrt.getch()

            if key.upper() == code[index].upper():
                index += 1
                if index == len(code):
                    return True
            else:
                return False
    
    return False

def battle(player_team, enemy_count,  mode):
    """
    メイン部分
    """
    if mode in ['Easy', 'Normal'] and all(isinstance(c, Support) or isinstance(c, Healer) for c in player_team):
        time.sleep(0.5)
        print(f"\n{Fore.LIGHTRED_EX}--- 戦闘可能なプレイヤーがいません !! ---")
        time.sleep(0.5)
        print(f"\n\t~~~ 戦略的撤退 !!!!!! ~~~\n{Style.RESET_ALL}")
        return "defeat"
    
    # 敵の生成
    enemy_all = Enemy()

    # enemy_all から選出
    enemy_team  = random.sample(enemy_all, k=enemy_count)

    # 出現エネミー確認
    time.sleep(0.3)
    max_name_width = max(wcswidth(char.name)     for char in enemy_team)
    max_hp_width   = max(wcswidth(str(char.hp))  for char in enemy_team)
    max_atk_width  = max(wcswidth(str(char.atk)) for char in enemy_team)
    max_mp_width   = max(wcswidth(str(char.mp))  for char in enemy_team)
    print(f"{Fore.LIGHTYELLOW_EX}\n============ 出現エネミー ============")
    for i, enemy in enumerate(enemy_team,start=1):
        name_padded = pad_to_width(enemy.name, max_name_width)
        hp  = str(enemy.hp).rjust(max_hp_width)
        atk = str(enemy.atk).rjust(max_atk_width)
        mp  = str(enemy.mp).rjust(max_mp_width)
        print(f"{i}. {name_padded}  ➡  HP:{hp} ATK:{atk} MP:{mp}")
    print(f"======================================{Style.RESET_ALL}")

    # ゲームループ
    while True:
        # 自陣のターン
        time.sleep(0.3)
        print("\n~~~~~~~~~~~~~ プレイヤーターン ~~~~~~~~~~~~~~")
        time.sleep(0.3)
        # 攻撃キャラ選択
        while True:
            try:
                # 生存キャラクターのみ表示
                flush_input()
                print("\n➡  行動するキャラクターを選択")
                # 表示インデント調整
                max_name_width  = max(wcswidth(char.name)       for char in player_team)
                max_hp_width    = max(wcswidth(str(char.hp))    for char in player_team)
                max_maxhp_width = max(wcswidth(str(char.maxhp)) for char in player_team)
                max_atk_width   = max(wcswidth(str(char.atk))   for char in player_team)
                max_mp_width    = max(wcswidth(str(char.mp))    for char in player_team)
                for i, char in enumerate(player_team, start=1):
                    # MPが0の場合は選択不可
                    if char.is_alive():
                        name_padded = pad_to_width(char.name, max_name_width)
                        hp = str(char.hp).rjust(max_hp_width)
                        maxhp = str(char.maxhp).rjust(max_maxhp_width)
                        atk = str(char.atk).rjust(max_atk_width)
                        mp = str(char.mp).rjust(max_mp_width)
                        print(f"{i}. {name_padded}（ HP：{hp}/{maxhp} ATK：{atk} MP：{mp} ）")
                time.sleep(0.3)
                choice = int(input("\n選択：")) - 1
                time.sleep(0.5)
                # 有効な入力か、生存しているかチェック
                if choice < 0 or choice >= len(player_team) or not player_team[choice].is_alive():
                    print("\n無効な選択です")
                else:
                    break
            except ValueError:
                print("\n無効な入力です")

        player_character = player_team[choice]
        # MP不足のため再選択
        if isinstance(player_character, (Healer, Support)) and player_character.mp <= 0:
            print(f"{Fore.RED}\n{player_character.name} はMPが不足しています\n別のキャラクターを選択してください{Style.RESET_ALL}")
            continue

        print(f"\n{Fore.YELLOW}➡  {player_character.name} の行動...\n{Style.RESET_ALL}")

        time.sleep(0.5)

        if isinstance(player_character, Support):
            """ サポーターのバフ処理 """
            support_targets = [c for c in  player_team if c.is_alive() and c != player_character]
            print("強化するキャラクターを選択\n")
            max_name_width = max(wcswidth(char.name)     for char in player_team)
            max_atk_width  = max(wcswidth(str(char.atk)) for char in player_team)
            max_mp_width   = max(wcswidth(str(char.mp))  for char in player_team)
            for i, char in enumerate(support_targets, start=1):
                # PTメンバーのリスト表示
                name_padded = pad_to_width(char.name, max_name_width)
                atk = str(char.atk).rjust(max_atk_width)
                mp = str(char.mp).rjust(max_mp_width)
                print(f"{i}.{name_padded}（ ATK：{atk} / MP：{mp} ） ")

            while True:
                try:
                    flush_input()
                    target_index = int(input("選択：")) - 1
                    if 0 <= target_index < len(support_targets):
                        target = support_targets[target_index]
                        time.sleep(0.5)
                        player_character.support(target)
                        break
                    else:
                        print("\n無効な入力です")
                except ValueError:
                    print("\n無効な入力です")

        # ヒーラーの回復処理
        elif isinstance(player_character, Healer):
            """ ヒーラー選択時の回復対象選択 """
            # 回復可能な味方（自分、HPが1以上MaxHP未満）
            heal_targets = [c for c in  player_team if c.is_alive() and c.hp < c.maxhp]
            if not heal_targets:
                print(f"{Fore.RED}回復可能なキャラクターがいません{Style.RESET_ALL}")
                continue    # 再度選択に戻る

            # 回復可能だった場合
            print("回復するキャラクターを選択\n")
            max_name_width  = max(wcswidth(char.name) for char in player_team)
            max_hp_width    = max(wcswidth(str(char.hp)) for char in player_team)
            max_maxhp_width = max(wcswidth(str(char.maxhp)) for char in player_team)
            for i, char in enumerate(heal_targets, start=1):
                # PTメンバーのリスト表示
                name_padded = pad_to_width(char.name, max_name_width)
                hp = str(char.hp).rjust(max_atk_width)
                maxhp = str(char.maxhp).rjust(max_mp_width)
                print(f"{i}.{name_padded}（ HP：{hp}/{maxhp} ） ")

            while True:
                try:
                    flush_input()
                    target_index = int(input("\n選択：")) - 1
                    if 0 <= target_index < len(heal_targets):
                        target = heal_targets[target_index]
                        time.sleep(0.5)
                        player_character.heal(target)
                        break
                    else:
                        print("\n無効な選択です")
                except ValueError:
                    print("\n無効な入力です")

        else:
            # 敵キャラクターリスト表示
            max_name_width = max(wcswidth(char.name)     for char in enemy_team)
            max_hp_width   = max(wcswidth(str(char.hp))  for char in enemy_team)
            max_atk_width  = max(wcswidth(str(char.atk)) for char in enemy_team)
            max_mp_width   = max(wcswidth(str(char.mp))  for char in enemy_team)
            for i, enemy in enumerate(enemy_team, start=1):
                if enemy.is_alive():
                    name_padded = pad_to_width(enemy.name, max_name_width)
                    hp  = str(enemy.hp).rjust(max_hp_width)
                    atk = str(enemy.atk).rjust(max_atk_width)
                    mp  = str(enemy.mp).rjust(max_mp_width)
                    print(f"{i}. {name_padded} （HP： {hp}  ATK： {atk}  MP： {mp}）")
                    
            if isinstance(player_character, Wizard):
                print("\n不思議な力が使えそうだ...")                
                if konami_code_listener():
                    if player_character.can_use_konami():
                        player_character.use_konami()
                        time.sleep(0.5)
                        print(f"\n\t{Fore.LIGHTMAGENTA_EX}\"あの\" 呪文を唱えた !!\n{Style.RESET_ALL}")
                        time.sleep(0.8)
                        for enemy in enemy_team:
                            Fore.LIGHTRED_EX
                            enemy.hp = 0
                            print(f"{Fore.LIGHTRED_EX}{enemy.name}は消滅した !{Style.RESET_ALL}")
                            time.sleep(0.5)

                        return "victory"
                    else:
                            print(f"\n{Fore.LIGHTBLUE_EX}しかし何もおこらなかった...{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.LIGHTBLUE_EX}詠唱に失敗した !! {Style.RESET_ALL}")
                    pass
                            

            # 攻撃対象の選択
            while True:
                try:
                    flush_input()
                    target_index = int(input("\n攻撃対象の番号を選択: ")) - 1
                    if target_index < 0 or target_index >= len(enemy_team) or not enemy_team[target_index].is_alive():
                        print("\n無効な選択です。再度選んでください。")
                    else:
                        break
                except ValueError:
                    print("無効な入力です。数字を入力してください。")

            target = enemy_team[target_index]
            time.sleep(0.5)
            player_character.attack(target)
            
        
        ##################################################
        # enemy_teamの中を走査して"curse"があれば持続ダメージ表示
        ##################################################


        # 撃破メッセージ
        if not target.is_alive():
            print(f"\n{Fore.LIGHTRED_EX}{target.name} を撃破 !{Style.RESET_ALL}")

        if all(not c.is_alive() for c in enemy_team):
            time.sleep(0.5)
            print(f"{Fore.YELLOW}\n\tエネミー消滅 !! あなたの勝利 !!\n{Style.RESET_ALL}")
            return "victory"

        time.sleep(1.0)
        # 敵陣のターン
        print("\n~~~~~~~~~~~~~~ エネミーターン ~~~~~~~~~~~~~~")
        time.sleep(1.0)

        alive_enemy = [character for character in enemy_team if character.is_alive()]

        if alive_enemy:
            enemy_choice = random.choice(alive_enemy)

        print(f"\n➡  {enemy_choice.name}の攻撃 !!")
        time.sleep(0.3)
        # ランダムでターゲット選択（タンクが存在する場合ヘイト値が高い）
        alive_players = [c for c in player_team if c.is_alive()]
        weights = [c.choice_weight for c in alive_players]
        target = random.choices(alive_players, weights=weights, k=1)[0]
        time.sleep(0.5)
        enemy_choice.attack(target)
        
        # 撃破メッセージ
        if not target.is_alive():
            print(f"\n\t\t{Fore.LIGHTRED_EX}{target.name} は力尽きた !!{Style.RESET_ALL}")
        
        time.sleep(0.3)

        # HPが0以下のキャラクターをリストから削除
        player_team = [character for character in player_team if character.is_alive()]
        enemy_team  = [character for character in enemy_team  if character.is_alive()]

        # 生死判定（ゲーム終了チェック）
        if all(not c.is_alive() for c in player_team):
            print(f"{Fore.BLUE}\nプレイヤー全滅 !! ゲームオーバー!!\n{Style.RESET_ALL}")
            return "defeat"
        # PTメンバーがヒーラー、サポーターのみになった場合ゲームオーバー
        alive_characters  = [c for c in player_team if c.is_alive()]
        attackable_player = [c for c in alive_characters if c.can_attack()]
        # 戦闘続行不能（ゲーム終了チェック）
        if alive_characters and not attackable_player:
            time.sleep(0.5)
            print(f"\n{Fore.LIGHTRED_EX}--- 戦闘可能なプレイヤーがいません !! ---")
            time.sleep(0.5)
            print(f"\n\t~~~ 戦略的撤退 !!!!!! ~~~\n{Style.RESET_ALL}")
            return "defeat"

