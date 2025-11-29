from abc import ABC, abstractmethod
from random import shuffle, randint
from math import floor



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


class Bonus(Entity):

    @abstractmethod
    def apply(self,
              player: Player) -> None:
        pass

    def symbol(self) -> str:
        return "B"


class Weapon(Entity):

    def __init__(self,
                 position: tuple[int, int],
                 name: str,
                 max_damage: float):
        super().__init__(position)
        self.name = name
        self.max_damage = max_damage

    @abstractmethod
    def roll_damage(self) -> float:
        pass

    def is_available(self) -> bool:
        pass

    def symbol(self) -> str:
        return "W"


class MeleeWeapon(Weapon):

    def damage(self,
               rage: float) -> float:
        pass


class RangedWeapon(Weapon):
    
    def __init__(self,
                 position: tuple[int, int],
                 name: str,
                 max_damage:
                     float, ammo: int):
        super().__init__(position, name, max_damage)
        self.ammo = ammo

    def consume_ammo(self, n: int = 1) -> bool:
        pass

    def damage(self, accuracy: float) -> float:
        pass


class Structure(Entity):

    @abstractmethod
    def interact(self,
                 player: Player) -> None:
        pass


class Enemy(Entity, Damageable, Attacker):

    def __init__(self,
                 reward_coins: int):
        Entity.__init__(self, (0, 0))
        Damageable.__init__(self, 0.0, 0.0)
        self.lvl = randint(1, 10)
        self.reward_coins = reward_coins

    @abstractmethod
    def before_turn(self,
                    player: Player) -> None:
        pass

    def roll_enemy_damage(self) -> float:
        pass

    def symbol(self) -> str:
        return "E"



class Player(Entity, Damageable, Attacker):

    def __init__(self,
                 lvl: int,
                 weapon: Weapon,
                 inventory: dict[str, list[Bonus]],
                 status: dict[str, int],
                 rage: float = 1.0,
                 accuracy: float = 1.0):
        Entity.__init__(self, (0, 0))
        Damageable.__init__(self, 150 * (1 + lvl / 10), 150 * (1 + lvl / 10))
        self.lvl = lvl
        self.weapon = weapon
        self.inventory = inventory
        self.status = status
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
        return "P"



class Rat(Enemy):

    def __init__(self,
                 infection_chance: float = 0.25,
                 flee_chance_low_hp: float = 0.10,
                 flee_treshold: float = 0.15,
                 infection_damage_base: float = 5.0,
                 infection_turns: int = 3,
                 reward_coins: int = 200):
        super().__init__(reward_coins)
        self.max_enemy_damage = 15 * (1 + self.lvl / 10)
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
        super().__init__(reward_coins)
        self.max_enemy_damage = 20 * (1 + self.lvl / 10)
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
        super().__init__(reward_coins)
        self.max_enemy_damage = 10 * (1 + self.lvl / 10)
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



class Fist(MeleeWeapon):
    
    def __init__(self, position: tuple[int, int], name: str = "Кулак", max_damage: float = 20):
        super().__init__(position, name, max_damage)

    def damage(self, rage: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)

class Stick(MeleeWeapon):
    
    def __init__(self,
                 position: tuple[int, int],
                 name: str = "Палка",
                 max_damage: float = 25):
        super().__init__(position, name, max_damage)
        self.durability = randint(10, 20)

    def is_available(self) -> bool:
        pass

    def damage(self, rage: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)


class Bow(RangedWeapon):

    def __init__(self,
                 position: tuple[int, int],
                 name = "Лук",
                 max_damage: float = 35):
        super().__init__(position, name, max_damage, randint(10, 15))

    def is_available(self) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)


class Revolver(RangedWeapon):

    def __init__(self,
                 position: tuple[int, int],
                 name = "Револьвер",
                 max_damage: float = 45):
        super().__init__(position, name, max_damage, randint(5, 10))

    def is_available(self) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)



class Medkit(Bonus):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.power = randint(10, 40)

    def apply(self,
              player: Player) -> None:
        pass


class Rage(Bonus):

    def __init__(self,
                 position: tuple[int, int],
                 price: int = 50):
        super().__init__(position)
        self.multiplier = randint(1, 10) / 10

    def apply(self,
              player: Player) -> None:
        pass

class Arrows(Bonus):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.amount = randint(1, 20)

    def apply(self,
              player: Player) -> None:
        pass

class Bullets(Bonus):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.amount = randint(1, 10)

    def apply(self,
              player: Player) -> None:
        pass


class Accuracy(Bonus):

    def __init__(self,
                 position: tuple[int, int],
                 price: int = 50):
        super().__init__(position)
        self.multiplier = randint(1, 10) / 10
        self.price = price

    def apply(self,
              player: Player) -> None:
        pass


class Coins(Bonus):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.amount = randint(50, 100)

    def apply(self,
              player: Player) -> None:
        pass



class Tower(Structure):

    def __init__(self,
                 position: tuple[int, int],
                 reveal_radius: int = 2):
        super().__init__(position)
        self.reveal_radius = reveal_radius

    def interact(self,
                 player: Player,
                 board: Board):
        pass

    def symbol(self) -> str:
        return "T"



class Board:

    def __init__(self,
                 rows: int,
                 cols: int,
                 grid: list[list[tuple[Entity | None, bool]]],
                 start: tuple[int, int] = (0, 0),
                 goal: tuple[int, int] = None):
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.start = start
        if goal is None:
            self.goal = (rows - 1, cols - 1)
        else: self.goal = goal

    def place(self,
              entity: Entity,
              pos: tuple[int, int]) -> None:
        self.grid[pos[0]][pos[1]] = entity

    def entity_at(self,
                  pos: tuple[int, int]) -> Entity | None:
        return self.grid[pos[0]][pos[1]]

    def in_bounds(self,
                  pos: tuple[int, int]) -> bool:
        if 0 <= pos[0] <= (self.rows-1) and 0 <= pos[1] <= (self.cols-1):
            return True
        else: return False

    def render(self,
               player: Player):
        print("-" * (self.cols * 2 + 1))
        for x in range(self.rows):
            print("|", end = "")
            for y in range(self.cols):
                if player.position == (x, y):
                    print(player.symbol)
                else:
                    if self.grid[x][y][1]:
                        if self.grid[x][y][1]:
                            if self.grid[x][y][0] is None:
                                print(" ")
                            else: print(self.grid[x][y][0])
                        else: print("X")
        print("-" * (self.cols * 2 + 1))


def start(n: int,
          m: int,
          player_lvl: int) -> tuple[Board, Player]:
    
    available_cells = n*m-2
    tower_cells = floor(n*m * 0.01)
    weapon_cells = floor(n*m * 0.05)
    bonus_cells = floor(n*m * 0.3)
    enemy_cells = floor(n*m * 0.15)
    empty_cells = available_cells - tower_cells - weapon_cells - bonus_cells - enemy_cells
    
    grid_to_be_filled = ["T"] * tower_cells + ["W"] * weapon_cells + ["B"] * bonus_cells + ["E"] * enemy_cells + [" "] * empty_cells
    shuffle(grid_to_be_filled)
    grid_to_be_filled = [" "] + grid_to_be_filled + [" "]
    
    grid = [[None for _ in range(n)] for _ in range(m)]

    for x in range(m):
        for y in range(n):
            cell = grid_to_be_filled[x*n+y]
            if cell == "T": cell = Tower((x, y))
            if cell == "W":
                weapons = [Stick((x, y)), Bow((x, y)), Revolver((x, y))]
                cell = weapons[randint(0, 2)]
            if cell == "B":
                bonuses = [Medkit((x, y)), Rage((x, y)), Arrows((x, y)), Bullets((x, y)), Accuracy((x, y)), Coins((x, y))]
                cell = bonuses[randint(0, 5)]
            if cell == "E":
                enemies = [Rat((x, y)), Spider((x, y)), Skeleton((x, y))]
                cell = enemies[randint(0, 2)]
            if cell == " ": cell = None
            grid[x][y] = (cell, False)
    
    
    board = Board(
        rows = m, 
        cols = n,
        grid = grid
    )
    
    player = Player(
        lvl = player_lvl,
        weapon = Fist((0, 0)),
        inventory = {},
        status = {}
    )
    
    return (board, player)


def game(board: Board,
         player: Player) -> None:
    pass

def main() -> None:
    pass


start(5, 5, 1)

