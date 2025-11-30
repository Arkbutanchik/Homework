from abc import ABC, abstractmethod
from random import shuffle, randint
import os
import argparse
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
        self.inventory = {
            "Medkit": [],
            "Rage": [],
            "Accuracy": []
        }
        
        self.coins = 0
        self.rage = 1.0
        self.accuracy = 1.0
        self.status = {}
        self.fight = False
        self.arrows = 0 # store arrows if bow is not equipped
        self.bullets = 0 # store bullets if revolver is not equipped
        
    def move(self,
             d_row: int,
             d_col: int,
             board: Board) -> None:
        self.position = (self.position[0] + d_row, self.position[1] + d_col)
        board.reveal(self.position)

    def attack(self,
               target: Damageable) -> float:
        pass

    def choose_weapon(self,
                      new_weapon: Weapon) -> None:
        self.weapon = new_weapon
        print(f"You have equipped a {Fore.BLUE}{type(new_weapon).__name__}{Style.RESET_ALL}!")

    def apply_status_tick(self) -> float:
        pass

    def add_coins(self,
                 amount: int) -> None:
        self.coins += amount
        print(f"{Fore.YELLOW}{amount} coins{Style.RESET_ALL} added! You now have {Fore.YELLOW}{self.coins} coins{Style.RESET_ALL}.")

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

    def add_to_inventory(self,
                         bonus: Bonus) -> None:
        """Adds bonus to inventory"""
        
        key = type(bonus).__name__
        
        if key in ("Medkit", "Rage", "Accuracy"):
            self.inventory[key].append(bonus)
            print(f"{Fore.YELLOW}{type(bonus).__name__}{Style.RESET_ALL} added to Inventory!")
        
        elif key == "Coins":
            self.add_coins(bonus.amount)
            
        elif key == "Arrows":
            if isinstance(self.weapon, Bow):
                self.weapon.ammo += bonus.amount
                print(f"{Fore.YELLOW}{bonus.amount} Arrows{Style.RESET_ALL} added to your {Fore.BLUE}Bow{Style.RESET_ALL}!")
            else:
                self.arrows += bonus.amount
                print(f"{Fore.YELLOW}{bonus.amount} Arrows{Style.RESET_ALL} added to Inventory!")
                
        elif key == "Bullets":
            if isinstance(self.weapon, Revolver):
                self.weapon.ammo += bonus.amount
                print(f"{Fore.YELLOW}{bonus.amount} Bullets{Style.RESET_ALL} added to your {Fore.BLUE}Revolver{Style.RESET_ALL}!")
            else:
                self.bullets += bonus.amount
                print(f"{Fore.YELLOW}{bonus.amount} Bullets{Style.RESET_ALL} added to Inventory!")
        
    def show_inventory(self) -> None:
        """Displays player's inventory"""
        
        print(f"\n{Fore.LIGHTGREEN_EX}--- Inventory ---{Style.RESET_ALL}")
        print(f"Weapon: {Fore.BLUE}{self.weapon.name}{Style.RESET_ALL} (Max Damage: {self.weapon.max_damage})")
        for key, items in self.inventory.items():
            print(f"{Fore.YELLOW}{key}{Style.RESET_ALL}: {len(items)}")
        print(f"{Fore.YELLOW}Coins{Style.RESET_ALL}: {self.coins}")
        print(f"{Fore.YELLOW}Arrows{Style.RESET_ALL}: {self.arrows}")
        print(f"{Fore.YELLOW}Bullets{Style.RESET_ALL}: {self.bullets}")
        print(f"{Fore.LIGHTGREEN_EX}-----------------{Style.RESET_ALL}\n")


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
              entity: Entity | None,
              pos: tuple[int, int]) -> None:
        if isinstance(entity, Entity):
            self.grid[pos[0]][pos[1]] = (entity, True)
        else:
            self.grid[pos[0]][pos[1]] = (None, True)
         
    def entity_at(self,
                  pos: tuple[int, int]) -> Entity | None:
        return self.grid[pos[0]][pos[1]][0]
    
    def reveal(self,
               pos: tuple[int, int]) -> None:
        """Reveals cell at position"""
        self.grid[pos[0]][pos[1]] = (self.grid[pos[0]][pos[1]][0], True)

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
                    if revealed or DEBUG_SHOW_UNOPENED_CELLS:
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
    
    if DEBUG_DISABLE_CLEARS:
        return
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
            grid[x][y] = (cell, False)
    
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
    while True:
        clear()
        board.render(player)
        player_input = input("""
Enter your move:
1. W (up)
2. A (left)
3. S (down)
4. D (right)
5. E (inventory)
Move: """).strip().lower()
        if player_input in ("w", "a", "s", "d"):
            if player_input == "w" and board.in_bounds((player.position[0]-1, player.position[1])):
                d_row, d_col = -1, 0
            elif player_input == "a" and board.in_bounds((player.position[0], player.position[1]-1)):
                d_row, d_col = 0, -1
            elif player_input == "s" and board.in_bounds((player.position[0]+1, player.position[1])):
                d_row, d_col = 1, 0
            elif player_input == "d" and board.in_bounds((player.position[0], player.position[1]+1)):
                d_row, d_col = 0, 1
            else: 
                input("Move out of bounds. Press Enter to change direction...")
                continue
            player.move(d_row, d_col, board)
        elif player_input == "e":
            clear()
            board.render(player)
            player.show_inventory()
            input("Press Enter to continue...")
            continue
        else:
            input("Invalid input. Press Enter to move...")
            continue
        
        clear()
        board.render(player)
        
        entity = board.entity_at(player.position)
        if entity is not None and not DEBUG_DISABLE_INTERACTIONS:
            
            if isinstance(entity, Structure):
                print(f"\nYou have encountered a {Fore.MAGENTA}{type(entity).__name__}{Style.RESET_ALL}!")
                
            elif isinstance(entity, Bonus):
                print(f"\nYou have found a bonus: {Fore.YELLOW}{type(entity).__name__}{Style.RESET_ALL}!")
                player.add_to_inventory(entity)
                board.place(None, player.position)
                
            elif isinstance(entity, Weapon):
                print(f"\nYou have found a {Fore.BLUE}{type(entity).__name__}{Style.RESET_ALL}!")
                weapon_choice = input(f"Would you like to swap your {Fore.BLUE}{type(player.weapon).__name__}{Style.RESET_ALL} for a {Fore.BLUE}{type(entity).__name__}{Style.RESET_ALL}? (y/n): ")
                if weapon_choice.strip().lower() == "y":
                    player.choose_weapon(entity)
                    board.place(None, player.position)
                
            elif isinstance(entity, Enemy):
                print(f"\nYou have encountered an {Fore.RED}{type(entity).__name__}{Style.RESET_ALL}!")
            
        input("\nPress Enter to continue...")
        
        if player.position == board.goal:
            clear()
            board.render(player)
            print(f"\n{Fore.CYAN}You Won!{Style.RESET_ALL}")
            break

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--skip-intro", action = "store_true")
parser.add_argument("-c", "--disable-clears", action = "store_true")
parser.add_argument("-s", "--show-unopened-cells", action = "store_true")
parser.add_argument("-d", "--disable-interactions", action = "store_true")
args = parser.parse_args()

DEBUG_SKIP_INTRO = args.skip_intro # skips intro and starts game directly
DEBUG_DISABLE_CLEARS = args.disable_clears # disables console clears
DEBUG_SHOW_UNOPENED_CELLS = args.show_unopened_cells # shows all cells as revealed
DEBUG_DISABLE_INTERACTIONS = args.disable_interactions # disables interactions with cells

if __name__ == "__main__":
    clear()
    
    if DEBUG_SKIP_INTRO:
        board, player = start(6, 6, 1)
        game(board, player)
    else:
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
