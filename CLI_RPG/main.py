import random
import time
import msvcrt
from battlesystem import battle
from player_characters import Party
from colorama import Fore, Style
from wcwidth import wcswidth

def pad_to_width(text, width):
    pad_len = width - wcswidth(text)
    return text + ' ' * pad_len

def flush_input():
    while msvcrt.kbhit():
        msvcrt.getch()  # 入力バッファに残っているキーを読み捨てる

def choose_difficule():
    print("\n" "--------- 難易度を選択 ---------")
    print("" "1.Easy\t | 敵：1,2体  味方：2人")
    print("" "2.Normal | 敵：2,3体  味方：3人")
    print("" "3.Hard\t | 敵：  3体  味方：3人")
    print("" "4.Hell\t | 敵：3,4体  味方：4人")
    print("" "5.Extra\t | 敵：  5体  味方：5人")
    print("" "--------------------------------")
    time.sleep(0.5)
    while True:
        try:
            choice = int(input("\n選択肢を入力："))
            if choice in [1,2,3,4,5]:
                return choice
            else:
                print("選択肢の中から選んでください")
        except ValueError:
            print("数字を入力してください")

def get_difficult(choice):
    if choice == 1:
        enemy_count = random.choice([1,2])
        party_size = 2
    if choice == 2:
        enemy_count = random.choice([2,3])
        party_size = 3
    if choice == 3:
        enemy_count = random.choice([3])
        party_size = 3
    if choice == 4:
        enemy_count = random.choice([3,4])
        party_size = 4
    if choice == 5:
        enemy_count = random.choice([5])
        party_size = 5
    
    return enemy_count, party_size

def main():
    """
    メインループ
    """
    print(f"{Fore.LIGHTGREEN_EX}\n ～ ターン制ダンジョンRPG ～{Style.RESET_ALL}")
    time.sleep(0.8)
    # 難易度選択
    level = choose_difficule()
    enemy_count, party_size = get_difficult(level)
    time.sleep(0.5)
    # PT編成
    player_all_characters = Party() # キャラクター一覧 
    max_name_width  = max(wcswidth(char.name) for char in player_all_characters)
    max_role_width  = max(wcswidth(char.role) for char in player_all_characters)
    max_hp_width    = max(wcswidth(str(char.hp))    for char in player_all_characters)
    max_maxhp_width = max(wcswidth(str(char.maxhp)) for char in player_all_characters)
    max_atk_width   = max(wcswidth(str(char.atk))   for char in player_all_characters)
    max_mp_width    = max(wcswidth(str(char.mp))    for char in player_all_characters)
    print("\n================= キャラクター一覧 =================")
    for i, char in enumerate(player_all_characters, start=1):
        name_padded = pad_to_width(char.name, max_name_width)
        role_padded = pad_to_width(char.role, max_role_width)
        hp    = str(char.hp).rjust(max_hp_width)
        maxhp = str(char.maxhp).rjust(max_maxhp_width)
        atk   = str(char.atk).rjust(max_atk_width)
        mp    = str(char.mp).rjust(max_mp_width)
        print(f"{i}. {name_padded} {role_padded} ➡  HP：{hp}/{maxhp} ATK：{atk} MP：{mp} ")
    print("====================================================")

    print(f"\nPT編成を行ってください（{party_size}人）")
    print("● カンマ(,)区切りで入力")
    while True:
        flush_input()
        selected_index = input("選択：").split(',')

        # 入力値を整形
        try:
            selected_index = [int(index.strip()) - 1 for index in selected_index]
        except ValueError:
            print("数字で入力してください\n")
            continue
        
        if len(selected_index) != party_size:
            print(f"{party_size}人編成してください\n")
            continue
        if len(set(selected_index)) != party_size:
            print("キャラクターが重複しています\n")
            continue
        if any(index < 0 or index >= len(player_all_characters) for index in selected_index):
            print("有効な数字を入力してください\n")
            continue
        break
    
    # 出撃メンバー
    player_team = []
    for index in selected_index:
        player_team.append(player_all_characters[index])

    # ステータス確認
    max_name_width  = max(wcswidth(char.name) for char in player_team)
    max_role_width  = max(wcswidth(char.role) for char in player_team)
    max_hp_width    = max(wcswidth(str(char.hp))    for char in player_team)
    max_maxhp_width = max(wcswidth(str(char.maxhp)) for char in player_team)
    max_atk_width   = max(wcswidth(str(char.atk))   for char in player_team)
    max_mp_width    = max(wcswidth(str(char.mp))    for char in player_team)
    print("\n------------------- 出撃パーティ -------------------")
    for i, char in enumerate(player_team, start=1):
        name_padded = pad_to_width(char.name, max_name_width)
        role_padded = pad_to_width(char.role, max_role_width)
        hp    = str(char.hp).rjust(max_hp_width)
        maxhp = str(char.maxhp).rjust(max_maxhp_width)
        atk   = str(char.atk).rjust(max_atk_width)
        mp    = str(char.mp).rjust(max_mp_width)
        print(f"{i}. {name_padded} {role_padded} ➡  HP：{hp}/{maxhp} ATK：{atk} MP：{mp} ")
    print("----------------------------------------------------")
    print(f"{Fore.LIGHTMAGENTA_EX}\n\tダンジョン攻略開始 !!!{Style.RESET_ALL}")
    time.sleep(1.0)

    # ダンジョンカウンター
    floor = 0

    # ダンジョンloop
    while True:
        time.sleep(1.0)
        mode = ["Easy", "Normal", "Hard", "Hell", "Extra"][level - 1]
        floor += 1
        print(f"{Fore.LIGHTCYAN_EX}\n\t-------- 第 {floor} 層 --------{Style.RESET_ALL}")
        result = battle(player_team, enemy_count,  mode)

        if result == "defeat":
            time.sleep(0.5)
            print(f"{Fore.LIGHTYELLOW_EX}\n\t=== 最高到達点階層 ===")
            print(f"\n\t\t第 {floor - 1} 層\n")
            print(f"\t======================{Style.RESET_ALL}")
            break

        print(f"{Fore.LIGHTCYAN_EX}\n\t------ {floor} 層踏破 !! ------{Style.RESET_ALL}")
        time.sleep(0.5)
        print(f"{Fore.LIGHTGREEN_EX}\n\tHP と MP が 50% 回復 !!{Style.RESET_ALL}")
        for member in player_team:
            # ステータスリセット
            member.reset_status()
            if member.hp > 0:
                # MPとHPをそれぞれ50％回復
                recover_hp = int(member.maxhp * 0.5)
                recover_mp = int(member.maxmp * 0.5)
                member.hp  = min(member.maxhp, member.hp + recover_hp)
                member.mp  = min(member.maxmp, member.mp + recover_mp)
                
        player_team = [member for member in player_team if member.hp > 0]
        time.sleep(1.0)


if __name__ == "__main__":
    main()