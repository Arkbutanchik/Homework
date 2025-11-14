from abc import ABC, abstractmethod


# Abstract classes

class Entity(ABC):

    def __init__(self,
                 position: tuple[int, int]):
        self.position = position

    @abstractmethod
    def symbol(self) -> str:
        pass


class Damageable(ABC):

    def __init__(self,
                 hp: float,
                 max_hp: float):
        self.hp = hp
        self.max_hp = max_hp

    def is_alive(self) -> bool:
        pass

    def heal(self,
             amount: float) -> float:
        pass

    def take_damage(self,
                    amount: float) -> float:
        pass


class Attacker(ABC):

    @abstractmethod
    def attack(self,
               target: Damageable) -> float:
        pass


class Bonus(ABC):

    @abstractmethod
    def apply(self,
              player: 'Player') -> None:
        pass


class Weapon(ABC):

    def __init__(self,
                 name: str,
                 max_damage: float):
        self.name = name
        self.max_damage = max_damage

    @abstractmethod
    def roll_damage(self) -> float:
        pass

    def is_available(self) -> bool:
        pass


class MeleeWeapon(Weapon):

    def damage(self,
               rage: float) -> float:
        pass


class RangedWeapon(Weapon):

    def __init__(self,
                 ammo: int):
        self.ammo = ammo

    def consume_ammo(self,
                     n: int = 1) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass


class Structure(ABC, Entity):

    @abstractmethod
    def interact(self,
                 player: 'Player') -> None:
        pass


class Enemy(ABC, Entity, Damageable, Attacker):

    def __init__(self,
                 lvl: int,
                 max_enemy_damage: float,
                 reward_coins: int):
        self.lvl = lvl
        self.max_enemy_damage = max_enemy_damage
        self.reward_coins = reward_coins
    
    @abstractmethod
    def before_turn(self,
                    player: 'Player') -> None:
        pass

    def roll_enemy_damage(self) -> float:
        pass
