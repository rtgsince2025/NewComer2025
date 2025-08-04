from character_base import Character
from colorama import Fore, Style, init
init()
import random

HP_BONUS   = 70
ATK_BONUS  = 15
MP_BONUS   = 15
MP_SUPPORT = 15
WIZARD_MP  = 10

class Soldier(Character):
    """
    派生クラス（剣士）
    """
    def __init__(self):
        super().__init__("剣士")
        self.role = "物理攻撃"
        self.hp -= 10
        self.base_atk = self.atk
        self.atk += ATK_BONUS
        self.mp = 1
        self.maxhp = self.hp
        self.maxmp = self.mp
        self.choice_weight = 1.0


    def calculate_damage(self, target):
        """剣士のダメージ計算（物理攻撃）"""
        return self.atk
    
    def reset_status(self):
        self.atk = self.base_atk + ATK_BONUS

class Wizard(Character):
    """
    派生クラス（魔法使い）
    """
    def __init__(self):
        super().__init__("魔法使い")
        self.role = "魔法攻撃"
        self.base_atk = self.atk
        self.mp += MP_BONUS
        self.maxhp = self.hp
        self.maxmp = self.mp
        self.choice_weight = 1.0
        self.konami_used_count = 0
        self.konami_max_count = 3

    def calculate_damage(self, target):
        """魔法使いのダメージ計算（魔法攻撃）"""
        if self.mp >= 10:
            self.mp -= 10
            return self.atk + WIZARD_MP
        elif self.mp > 0:
            damage = ATK_BONUS
            self.mp = 0
            print(f"{Fore.LIGHTRED_EX}\n{self.name} は残りのMPを振り絞った !!{Style.RESET_ALL}")
            return damage
        else:
            print(f"\n{self.name} のMPが不足しています !!")
            return 0

    def can_use_konami(self):
        return self.konami_used_count < self.konami_max_count
    
    def use_konami(self):
        self.konami_used_count += 1

    def can_attack(self):
        return self.mp > 0 and self.is_alive()

    def reset_status(self):
        self.atk = self.base_atk

class Tank(Character):
    """
    派生クラス（タンク）
    """
    def __init__(self):
        super().__init__("タンク")
        self.role = "引き付け"
        self.base_atk = self.atk
        self.hp += HP_BONUS
        self.mp = 1
        self.maxhp = self.hp
        self.maxmp = self.mp
        self.choice_weight = 7.0

    def calculate_damage(self, target):
        """タンクのダメージ計算（被撃率UP）"""
        return self.atk
    
    def reset_status(self):
        self.atk = self.base_atk

##################################################
class Sharman(Character):
    """実装叶わず、、、無念。"""
    def __init__(self) :
        super().__init__("シャーマン")
        self.role = "呪術師"
        self.hp   = random.randint(50, 70)
        self.atk  = random.randint(20, 30)
        self.mp   = random.randint(20, 40)
        self.base_atk = self.atk
        self.maxhp = self.hp
        self.maxmp = self.mp
        self.choice_weight = 0.5
        self.constant_damage = 10

    def attack(self, target):
        """シャーマンのダメージ計算（確率で持続ダメージ）"""
        if self.mp > 10:
            """MP>=10以上の時"""
            self.mp -= 10
            target.hp -= self.constant_damage
            probability = random.randint(70, 80)
            if random.randint(1, 100) <= probability:
                target.status["curse"] = {
                    "damage":int(self.atk//2),
                    "permanent": True
                }
            return self.constant_damage
        elif self.mp > 0:
            """0<MP<10の時"""
            self.mp = 0
            print(f"{Fore.LIGHTRED_EX}\n{self.name} は残りのMPを振り絞った !!{Style.RESET_ALL}")
            target.status["curse"] = {
                    "damage":int(self.atk//2),
                    "permanent":True
                }
            return 0
        else:
            """MPが0になると行動不可能"""
            print(f"\n{self.name} のMPが不足しています !!")
            return 0

    def  can_attack(self):
        return self.mp > 0 and self.is_alive()
    
    def reset_status(self):
        self.atk = self.base_atk 

##################################################

class Support(Character):
    """
    派生クラス（サポーター）
    """
    def __init__(self):
        super().__init__("サポーター")
        self.role = "強化"
        if self.mp < MP_SUPPORT:
            self.mp = 20    # MP15以下なら20に設定
        if self.atk < 20:
            self.atk = 20   # 下限保証
        self.base_atk = self.atk
        self.maxhp = self.hp
        self.maxmp = self.mp
        self.choice_weight = 1.0


    def attack(self, target):
        print(f"\n{self.name} は攻撃できません !!（強化専用ユニット）")
        return 0

    def can_support(self):
        return self.mp > 0 and self.is_alive()

    def support(self, target):
        """サポーターの強化量計算"""
        if self == target:
            print(f"{Fore.RED}\n自身は強化できません !!{Style.RESET_ALL}")
            return 0

        if self.mp >= 15:
            """通常バフ計算"""
            buff_atk = int(self.atk * 0.5)
            buff_mp  = 15
            self.mp -= 15
            target.atk += buff_atk

            # 最大MPを超過しないように調整
            buff_limit = min(buff_mp, target.maxmp - target.mp)
            target.mp  += buff_limit
            print(f"\n{Fore.LIGHTBLUE_EX}{target.name}を強化 !!  ATK：{target.atk} MP：{target.mp}に上昇 !!{Style.RESET_ALL}")

        elif self.mp > 0:
            """固定値バフ"""
            self.mp  = 0
            buff_atk = 5
            buff_mp  = 5
            target.atk += buff_atk
            buff_limit = min(buff_mp, target.maxmp - target.mp)
            target.mp += buff_limit
            print(f"{Fore.LIGHTRED_EX}\n{self.name} は残りのMPを振り絞った !!{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{target.name} に固定バフ !! ATK +{buff_atk}, MP +{buff_mp}!!{Style.RESET_ALL}")

        else:
            print(f"\n{self.name} のMPが不足しています !!")
            return 0
        
        return 1

    def can_attack(self):
        return False
    
    def reset_status(self):
        self.atk = self.base_atk


class Healer(Character):
    """
    派生クラス（ヒーラー）
    """
    def __init__(self):
        super().__init__("ヒーラー")
        self.role = "回復"
        self.base_atk = self.atk
        self.maxhp = self.hp
        self.maxmp = self.mp
        self.choice_weight = 1.0

    def attack(self, target):
        print(f"\n{self.name} は攻撃できません !!（回復専用ユニット）")
        return 0

    def can_heal(self):
        return self.mp > 0 and self.is_alive()

    def heal(self, target):
        """ヒーラーの回復量計算"""
        if self.mp >= 10:
            self.mp -= 10
            recovery = int(self.atk * 1.5)
        elif self.mp > 0:
            recovery = 20
            self.mp = 0
            print(f"{Fore.LIGHTRED_EX}\n{self.name} は残りのMPを振り絞った !!{Style.RESET_ALL}")
        else:
            print(f"\n{self.name} のMPが不足しています !!")
            return 0

        # 最大HPを超過しないよう調整
        recovery_limit = min(recovery, target.maxhp - target.hp)
        target.hp += recovery_limit
        print(f"\n{Fore.GREEN}{self.name} ➡  {target.name} を \"{recovery_limit}\" 回復した !! HP：{target.hp}/{target.maxhp}{Style.RESET_ALL}")
        return recovery

    def can_attack(self):
        return False
    
    def reset_status(self):
        self.atk = self.base_atk

class Party(list):
    """
    インスタンス生成
    """
    def __init__(self, members=None):
        if members is None:
            members = [Soldier(), Wizard(), Tank(), Support(), Healer(),]
        super().__init__(members)
