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
              player: Player) -> None:
        pass

    def symbol(self) -> str:
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
        super().__init__("", 0.0)
        self.ammo = ammo

    def consume_ammo(self,
                     n: int = 1) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass


class Structure(Entity):

    @abstractmethod
    def interact(self,
                 player: Player) -> None:
        pass

    def symbol(self) -> str:
        pass


class Enemy(Entity, Damageable, Attacker):

    def __init__(self,
                 lvl: int,
                 max_enemy_damage: float,
                 reward_coins: int):
        Entity.__init__(self, (0, 0))
        Damageable.__init__(self, 0.0, 0.0)
        self.lvl = lvl
        self.max_enemy_damage = max_enemy_damage
        self.reward_coins = reward_coins

    @abstractmethod
    def before_turn(self,
                    player: Player) -> None:
        pass

    def roll_enemy_damage(self) -> float:
        pass

    def symbol(self) -> str:
        pass


# Specific classes

class Player(Entity, Damageable, Attacker):

    def __init__(self,
                 lvl: int,
                 weapon: Weapon,
                 inventory: dict[str, int],
                 status: dict[str, int],
                 rage: float = 1.0,
                 accuracy: float = 1.0):
        Entity.__init__(self, (0, 0))
        Damageable.__init__(self, 0.0, 0.0)
        self.lvl = lvl
        self.weapon = weapon
        self.inventory = inventory
        self.status =status
        self.rage = rage
        self.accuracy = accuracy
        
    def move(self,
             d_row: int,
             d_col: int) -> None:
        pass

    def attack(self,
               target: Damageable) -> float:
        pass

    def choose_weapon(self,
                      new_weapon: Weapon) -> None:
        pass

    def apply_status_tick(self) -> float:
        pass

    def add_coins(self,
                 amount: int) -> None:
        pass

    def use_bonus(self,
                  bonus: Bonus) -> None:
        pass

    def buy_auto_if_needed(self,
                           bonus_factory: callable[[str], Bonus]) -> None:
        pass
    
    def symbol(self) -> str:
        pass


# Enemies

class Rat(Enemy):

    def __init__(self,
                 infection_chance: float = 0.25,
                 flee_chance_low_hp: float = 0.10,
                 flee_treshold: float = 0.15,
                 infection_damage_base: float = 5.0,
                 infection_turns: int = 3,
                 reward_coins: int = 200):
        super().__init__(1, 10.0, reward_coins)
        self.infection_chance = infection_chance
        self.flee_chance_low_hp = flee_chance_low_hp
        self.flee_treshold = flee_treshold
        self.infection_damage_base = infection_damage_base
        self.infection_turns = infection_turns

    def before_turn(self,
                    player: Player) -> None:
        pass

    def attack(self,
               target: Damageable) -> float:
        pass


class Spider(Enemy):
    
    def __init__(self,
                 poison_chance: float = 0.10,
                 summon_chance_low_hp: float = 0.10,
                 poison_damage_base: float = 15.0,
                 poison_turns: int = 2,
                 reward_coins: int = 250):
        super().__init__(1, 15.0, reward_coins)
        self.poison_chance = poison_chance
        self.summon_chance_low_hp = summon_chance_low_hp
        self.poison_damage_base = poison_damage_base
        self.poison_turns = poison_turns

    def before_turn(self,
                    player: Player) -> None:
        pass

    def attack(self,
               target: Damageable) -> float:
        pass


class Skeleton(Enemy):
    
    def __init__(self,
                 weapon: Weapon,
                 reward_coins: int = 150):
        super().__init__(1, 20.0, reward_coins)
        self.weapon = weapon

    def before_turn(self,
                    player: Player):
        pass

    def attack(self,
               target: Damageable) -> float:
        pass

    def drop_loot(self,
                  player: Player) -> Weapon | None:
        pass


# Weapons

class Fist(MeleeWeapon):
    
    def __init__(self,
                 name = "Кулак",
                 max_damage: float = 20):
        super().__init__(name, max_damage)

    def damage(self,
               rage: float) -> float:
        pass


class Stick(MeleeWeapon):

    def __init__(self,
                 durabilty: int,
                 name = "Палка",
                 max_damage: float = 25):
        super().__init__(name, max_damage)
        self.durabilty = durabilty

    def is_available(self) -> bool:
        pass

    def damage(self,
               rage: float) -> float:
        pass


class Bow(RangedWeapon):

    def __init__(self,
                 ammo: int,
                 name = "Лук",
                 max_damage: float = 35):
        super().__init__(ammo)
        self.name = name
        self.max_damage = max_damage

    def is_available(self) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass


class Revolver(RangedWeapon):

    def __init__(self,
                 ammo: int,
                 name = "Револьвер",
                 max_damage: float = 45):
        super().__init__(ammo)
        self.name = name
        self.max_damage = max_damage

    def is_available(self) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass


# Bonuses

class Medkit(Bonus):

    def __init__(self,
                 power: int):
        self.power = power

    def apply(self,
              player: Player) -> None:
        pass


class Rage(Bonus):

    def __init__(self,
                 multiplier: float):
        self.multiplier = float

    def apply(self,
              player: Player) -> None:
        pass

class Bullets(Bonus):
    
    def __init__(self,
                 amount: int):
        self.amount = amount

    def apply(self,
              player: Player) -> None:
        pass


class Accuracy(Bonus):

    def __init__(self,
                 multiplier: float,
                 price: int = 50):
        self.multiplier = multiplier
        self.price = price

    def apply(self,
              player: Player) -> None:
        pass


class Coins(Bonus):
    
    def __init__(self,
                 amount: int):
        self.amount = amount

    def apply(self,
              player: Player) -> None:
        pass


# Structures

class Tower(Structure):

    def __init__(self,
                 reveal_radius: int = 2):
        super().__init__((0, 0))
        self.reveal_radius = reveal_radius

    def interact(self,
                 player: Player,
                 board: Board):
        pass


# Board

class Board:

    def __init__(self,
                 rows: int,
                 cols: int,
                 grid: list[list[tuple[Entity | None, bool]]],
                 start: tuple[int, int] = (0, 0),
                 goal: tuple[int, int] = (0, 0)):
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.start = start
        self.goal = goal

    def place(self,
              entity: Entity,
              pos: tuple[int, int]) -> None:
        pass

    def entity_at(self,
                  pos: tuple[int, int]) -> Entity | None:
        pass

    def in_bounds(self,
                  pos: tuple[int, int]) -> bool:
        pass

    def render(self,
               player: Player):
        pass

# Initialization

def start(n: int,
          m: int,
          player_lvl: int) -> tuple[Board, Player]:
    pass

def game(board: Board,
         player: Player) -> None:
    pass

def main() -> None:
    pass
