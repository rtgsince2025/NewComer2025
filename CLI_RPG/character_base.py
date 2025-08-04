import math
import time
import random
from colorama import Fore, Style, init
init()

class Character:
    """
    基底クラス
    """
    def __init__(self, name):
        self.name = name
        self.role = "職分"
        self.hp   = random.randint(70, 100)
        self.atk  = random.randint(15, 30)
        self.mp   = random.randint(20, 40)
        self.maxhp = self.hp    # 初期HPを最大HPとする
        self.maxmp = self.mp    # 初期MPを最大MPとする
        self.choice_weight = 1.0
        self.status = {}        # 状態異常

    def attack(self, target):
        """
        攻撃メソッド（クリティカル処理のみ）
        """
        # 10%の確率でクリティカル
        if self.mp > 0:
            critical_damage = random.random() < 0.1
        else:
            critical_damage = False
        
        damage = self.calculate_damage(target)

        if critical_damage:
            damage *= 1.4
            damage = math.floor(damage)
            time.sleep(0.3)
            print(f"{Fore.LIGHTRED_EX}\nクリティカル発生 !{Style.RESET_ALL}")
        # ダメージ適用
        target.hp -= damage
        time.sleep(0.3)
        print(f"\n{self.name}の攻撃 ➡  {target.name}に {Fore.RED}\"{damage}\"{Style.RESET_ALL} ダメージ !!")
        return damage
    
    ##################################################
    def status_effects(self):
        """
        状態異常時の発生ダメージ処理（にするはずだったもの）
        """
        if self.status.get("curse", False):
            source = self.status.get("curse_source", None)
            if source:
                damage  = source.constant_damage + source.atk // 2
                print(f"{Fore.MAGENTA}{self.name}は呪いで{damage}ダメージ受けた !{Style.RESET_ALL}")
                time.sleep(0.3)
    ##################################################

    def continuous_damage(self):
        return 

    def can_attack(self):
        return self.mp > 0

    def calculate_damage(self, target):
        """
        ダメージ計算（派生クラスにてoverride）
        """
        pass

    def is_alive(self):
        """
        生死判定
        """
        return self.hp > 0