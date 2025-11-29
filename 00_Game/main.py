from abc import ABC, abstractmethod
from random import shuffle, randint
import os
from colorama import Fore, Style

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
              player: 'Player') -> None:
        pass

    def symbol(self) -> str:
        return Fore.YELLOW+"B"+Style.RESET_ALL


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
        return Fore.BLUE+"W"+Style.RESET_ALL


class MeleeWeapon(Weapon):

    def damage(self,
               rage: float) -> float:
        pass


class RangedWeapon(Weapon):
    
    def __init__(self,
                 position: tuple[int, int],
                 name: str,
                 max_damage: float, 
                 ammo: int):
        super().__init__(position, name, max_damage)
        self.ammo = ammo

    def consume_ammo(self, n: int = 1) -> bool:
        pass

    def damage(self, accuracy: float) -> float:
        pass


class Structure(Entity):

    @abstractmethod
    def interact(self,
                 player: 'Player') -> None:
        pass


class Enemy(Entity, Damageable, Attacker):

    def __init__(self,
                 position: tuple[int, int],
                 reward_coins: int):
        Entity.__init__(self, position)
        Damageable.__init__(self, 0.0, 0.0)
        self.lvl = randint(1, 10)
        self.reward_coins = reward_coins

    @abstractmethod
    def before_turn(self,
                    player: 'Player') -> None:
        pass

    def roll_enemy_damage(self) -> float:
        pass

    def symbol(self) -> str:
        return Fore.RED+"E"+Style.RESET_ALL



class Player(Entity, Damageable, Attacker):

    def __init__(self,
                 lvl: int):
        Entity.__init__(self, (0, 0))
        Damageable.__init__(self, 150 * (1 + lvl / 10), 150 * (1 + lvl / 10))
        self.lvl = lvl
        self.weapon = Fist((0, 0))
        self.inventory = {}
        self.coins = 0
        self.rage = 1.0
        self.accuracy = 1.0
        self.status = {}
        self.fight = False
        
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
                           bonus: str) -> Bonus:
        pass

    def symbol(self) -> str:
        return Fore.GREEN+"P"+Style.RESET_ALL
    
    def change_fight(self) -> None:
        pass



class Rat(Enemy):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, 200)
        self.max_enemy_damage = 15 * (1 + self.lvl / 10)
        self.infection_chance = 0.25
        self.flee_chance_low_hp = 0.10
        self.flee_treshold = 0.15
        self.infection_damage_base = 5.0
        self.infection_turns = 3

    def before_turn(self,
                    player: Player) -> None:
        pass

    def attack(self,
               target: Damageable) -> float:
        pass


class Spider(Enemy):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, 250)
        self.max_enemy_damage = 20 * (1 + self.lvl / 10)
        self.poison_chance = 0.10
        self.summon_chance_low_hp = 0.10
        self.poison_damage_base = 15.0
        self.call_treshold = 0.15
        self.poison_turns = 2

    def before_turn(self,
                    player: Player) -> None:
        pass

    def attack(self,
               target: Damageable) -> float:
        pass


class Skeleton(Enemy):
    
    def __init__(self,
                 position: tuple[int, int],
                 weapon: Weapon):
        super().__init__(position, 150)
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
    
    def __init__(self, 
                 position: tuple[int, int]):
        super().__init__(position, "Кулак", 20)

    def damage(self, rage: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)

class Stick(MeleeWeapon):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, "Палка", 25)
        self.durability = randint(10, 20)

    def is_available(self) -> bool:
        pass

    def damage(self, rage: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)


class Bow(RangedWeapon):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, "Лук", 35, randint(10, 15))

    def is_available(self) -> bool:
        pass

    def damage(self,
               accuracy: float) -> float:
        pass
    
    def roll_damage(self):
        return randint(0, self.max_damage)


class Revolver(RangedWeapon):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, "Револьвер", 45, randint(5, 10))

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
                 position: tuple[int, int]):
        super().__init__(position)
        self.multiplier = randint(1, 10) / 10
        self.price = 50

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
                 position: tuple[int, int]):
        super().__init__(position)
        self.multiplier = randint(1, 10) / 10
        self.price = 50

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
                 position: tuple[int, int]):
        super().__init__(position)
        self.reveal_radius = 2

    def interact(self,
                 player: Player,
                 board: 'Board'):
        pass

    def symbol(self) -> str:
        return Fore.MAGENTA+"T"+Style.RESET_ALL



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
        return (0 <= pos[0] <= (self.rows-1) and 0 <= pos[1] <= (self.cols-1))

    def render(self, player: Player):
        print("-" * (self.cols * 2 + 1))
        for x in range(self.rows):
            print("|", end="")
            for y in range(self.cols):
                entity, revealed = self.grid[x][y]
                if player.position == (x, y):
                    print(player.symbol() + "|", end="")
                else:
                    if revealed:
                        if entity is None:
                            print(" |", end="")
                        else:
                            print(entity.symbol() + "|", end="")
                    else:
                        print("X|", end="")
            print()
        print("-" * (self.cols * 2 + 1))

def startup() -> str:
    """Shows startup screen"""
    
    logo = f"""
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;165;0m████████▄   ▄█     ▄████████\x1b[0m      \x1b[38;2;240;240;240m ▄██████▄     ▄████████\x1b[0m      \x1b[38;2;255;165;0m   ▄███████▄    ▄████████    ▄████████  ▄█     ▄████████    ▄█    █▄    \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;140;0m███   ▀███ ███    ███    ███\x1b[0m      \x1b[38;2;220;220;220m███    ███   ███    ███\x1b[0m      \x1b[38;2;255;140;0m  ███    ███   ███    ███   ███    ███ ███    ███    ███   ███    ███   \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;115;0m███    ███ ███▌   ███    █▀ \x1b[0m      \x1b[38;2;200;200;200m███    ███   ███    ███\x1b[0m      \x1b[38;2;255;115;0m  ███    ███   ███    █▀    ███    ███ ███▌   ███    █▀    ███    ███   \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;90;0m███    ███ ███▌  ▄███▄▄▄    \x1b[0m      \x1b[38;2;180;180;180m███    ███  ▄███▄▄▄▄██▀\x1b[0m      \x1b[38;2;255;90;0m  ███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀ ███▌   ███         ▄███▄▄▄▄███▄▄ \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;65;0m███    ███ ███▌ ▀▀███▀▀▀    \x1b[0m      \x1b[38;2;160;160;160m███    ███ ▀▀███▀▀▀▀▀  \x1b[0m      \x1b[38;2;255;65;0m▀█████████▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███▌ ▀███████████ ▀▀███▀▀▀▀███▀  \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;40;0m███    ███ ███    ███    █▄ \x1b[0m      \x1b[38;2;140;140;140m███    ███ ▀███████████\x1b[0m      \x1b[38;2;255;40;0m  ███          ███    █▄  ▀███████████ ███           ███   ███    ███   \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;255;15;0m███   ▄███ ███    ███    ███\x1b[0m      \x1b[38;2;120;120;120m███    ███   ███    ███\x1b[0m      \x1b[38;2;255;15;0m  ███          ███    ███   ███    ███ ███     ▄█    ███   ███    ███   \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;200;0;0m████████▀  █▀     ██████████\x1b[0m      \x1b[38;2;100;100;100m ▀██████▀    ███    ███\x1b[0m      \x1b[38;2;200;0;0m ▄████▀        ██████████   ███    ███ █▀    ▄████████▀    ███    █▀    \x1b[0m
{" "*((os.get_terminal_size().columns-135)//2)}\x1b[38;2;160;0;0m                            \x1b[0m       \x1b[38;2;80;80;80m            ███    ███ \x1b[0m      \x1b[38;2;160;0;0m                           ███    ███                                  \x1b[0m
"""
    print(logo)
    print(os.get_terminal_size().columns * "-")
    
    difficulty = input(f"""\nChoose difficulty level:
                       
1. {Fore.GREEN}Easy{Style.RESET_ALL}
2. {Fore.YELLOW}Normal{Style.RESET_ALL}
3. {Fore.RED}Hard{Style.RESET_ALL}

Difficulty: """).strip().lower()
    
    return difficulty

def clear():
    """Clears console output"""
    
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def start(n: int,
          m: int,
          player_lvl: int) -> tuple[Board, Player]:
    
    available_cells = n*m-2
    tower_cells = round(n*m * 0.01)
    weapon_cells = round(n*m * 0.05)
    bonus_cells = round(n*m * 0.3)
    enemy_cells = round(n*m * 0.15)
    empty_cells = available_cells - tower_cells - weapon_cells - bonus_cells - enemy_cells
    
    grid_to_be_filled = ["T"] * tower_cells + ["W"] * weapon_cells + ["B"] * bonus_cells + ["E"] * enemy_cells + [" "] * empty_cells
    shuffle(grid_to_be_filled)
    grid_to_be_filled = [" "] + grid_to_be_filled + [" "]
    
    grid = [[None for _ in range(n)] for _ in range(m)]

    for x in range(m):
        for y in range(n):
            cell = grid_to_be_filled[x*n+y]
            if cell == "T": 
                cell = Tower((x, y))
            if cell == "W":
                weapons = [Stick((x, y)), Bow((x, y)), Revolver((x, y))]
                cell = weapons[randint(0, 2)]
            if cell == "B":
                bonuses = [Medkit((x, y)), Rage((x, y)), Arrows((x, y)), Bullets((x, y)), Accuracy((x, y)), Coins((x, y))]
                cell = bonuses[randint(0, 5)]
            if cell == "E":
                enemies = [Rat((x, y)), Spider((x, y)), Skeleton((x, y), Fist((0, 0)))]
                cell = enemies[randint(0, 2)]
            if cell == " ": 
                cell = None
            grid[x][y] = (cell, True)
    
    grid[0][0] = (None, True)
    grid[m-1][n-1] = (None, True)
    
    board = Board(
        rows = m, 
        cols = n,
        grid = grid
    )
    
    player = Player(lvl = player_lvl)
    
    return (board, player)


def game(board: Board,
         player: Player) -> None:
    board.render(player)

def main() -> None:
    pass


if __name__ == "__main__":
    clear()
    
    difficulty = startup()
    print()
    if difficulty in ("1", "easy"):
        board_size = (randint(5, 7), randint(5, 7))
        player_lvl = 1
        print(f"Starting game on {Fore.GREEN}Easy{Style.RESET_ALL} difficulty.")
    elif difficulty in ("2", "normal"):
        board_size = (randint(8, 11), randint(8, 11))
        player_lvl = 2
        print(f"Starting game on {Fore.YELLOW}Normal{Style.RESET_ALL} difficulty.")
    elif difficulty in ("3", "hard"):
        board_size = (randint(12, 15), randint(12, 15))
        player_lvl = 3
        print(f"Starting game on {Fore.RED}Hard{Style.RESET_ALL} difficulty.")
    else:
        print(f"Invalid input, starting game on {Fore.YELLOW}Normal{Style.RESET_ALL} difficulty.")
        board_size = (randint(8, 11), randint(8, 11))
        player_lvl = 2
    
    input("\nPress Enter to start the game...")
    clear()
    
    board, player = start(board_size[0], board_size[1], player_lvl)
    game(board, player)
