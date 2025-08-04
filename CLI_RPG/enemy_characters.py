from character_base import Character

ATK_BONUS = 5
HP_BONUS  = 40
MP_BONUS  = 10

class Goblin(Character):
    """
    派生クラス（ゴブリン）
    """
    def __init__(self):
        super().__init__("ゴブリン")
        self.atk += ATK_BONUS
        self.mp = 1

    def calculate_damage(self, target):
        """ゴブリンのダメージ計算（物理攻撃）"""
        return self.atk
    

class Witch(Character):
    """
    派生クラス（ウィッチ）
    """
    def __init__(self):
        super().__init__("ウィッチ")
        self.mp += MP_BONUS

    def calculate_damage(self, target):
        """ウィッチのダメージ計算（魔法攻撃）"""
        if self.mp >= 10:
            self.mp -= 10
            return self.atk + 10
        elif self.mp > 0:
            damage = 5
            self.mp = 0
            print(f"\n{self.name} は残りのMPを振り絞った!!!")
            return damage
        else:
            print(f"\n{self.name} のMPが不足しています!!!")
            return 0
        

class WolfMan(Character):
    """
    派生クラス（オオカミ男）
    """
    def __init__(self):
        super().__init__("オオカミ男")
        self.atk += int(ATK_BONUS*2)
        self.hp -= 30
        self.mp = 1

    def calculate_damage(self, target):
        """狼男のダメージ計算（物理攻撃）"""
        return self.atk

class Skeleton(Character):
    """
    派生クラス（スケルトン）
    """
    def __init__(self):
        super().__init__("スケルトン")
        self.hp -= 15
        self.atk += ATK_BONUS
        self.mp = 1

    def calculate_damage(self, target):
        """スケルトンのダメージ計算（物理攻撃）"""
        return self.atk


class Golem(Character):
    """
    派生クラス（ゴーレム）
    """
    def __init__(self):
        super().__init__("ゴーレム")
        self.hp += HP_BONUS
        self.atk = 15 
        self.mp = 1

    def calculate_damage(self, target):
        """ゴーレムのダメージ計算（物理攻撃）"""
        return self.atk

class Enemy(list):
    """
    インスタンス生成
    """
    def __init__(self, members=None):
        if members is None:
            members = [Goblin(), Witch(), WolfMan(), Skeleton(), Golem()]
        super().__init__(members)