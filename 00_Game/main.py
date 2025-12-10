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
        return self.hp > 0

    def heal(self,
             amount: float) -> float:
        healed_amount = amount
        
        if self.hp + amount > self.max_hp:
            healed_amount = self.max_hp - self.hp
            self.hp = self.max_hp
        else:
            self.hp += amount

        return healed_amount

    def take_damage(self,
                    amount: float) -> float:
        damage_amount = amount
        
        if self.hp - amount < 0:
            damage_amount = self.hp
            self.hp = 0
        else:
            self.hp -= amount

        return damage_amount


class Attacker(ABC):

    @abstractmethod
    def attack(self,
               target: 'Damageable') -> float:
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

    @abstractmethod
    def is_available(self) -> bool:
        pass

    def symbol(self) -> str:
        return Fore.BLUE+"W"+Style.RESET_ALL


class MeleeWeapon(Weapon):

    def roll_damage(self):
        return randint(0, self.max_damage)

    def damage(self,
               rage: float) -> float:
        return self.roll_damage() * rage


class RangedWeapon(Weapon):
    
    def __init__(self,
                 position: tuple[int, int],
                 name: str,
                 max_damage: float, 
                 ammo: int):
        super().__init__(position, name, max_damage)
        self.ammo = ammo

    def consume_ammo(self, n: int = 1) -> bool:
        if self.ammo >= n:
            self.ammo -= n
            return True
        else:
            return False

    def roll_damage(self):
        return randint(0, self.max_damage)

    def damage(self,
               accuracy: float) -> float:
        return self.roll_damage() * accuracy
    
    def is_available(self):
        return self.ammo > 0


class Structure(Entity):

    @abstractmethod
    def interact(self,
                 player: 'Player') -> None:
        pass


class Enemy(Entity, Damageable, Attacker):

    def __init__(self,
                 position: tuple[int, int],
                 reward_coins: int,
                 max_enemy_damage: float,
                 lvl: int):
        Entity.__init__(self, position)
        Damageable.__init__(self, round(100 * (1 + lvl / 10), 1), round(100 * (1 + lvl / 10), 1))
        self.lvl = lvl
        self.reward_coins = reward_coins
        self.max_enemy_damage = int(max_enemy_damage)

    @abstractmethod
    def before_turn(self,
                    player: 'Player') -> None:
        pass

    def roll_enemy_damage(self) -> float:
        return randint(0, self.max_enemy_damage)

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
            "Accuracy": [],
            "Arrows": [],
            "Bullets": []
        }

        self.fight_queue = [] # TODO
        
        self.coins = 0
        self.rage = 1.0
        self.accuracy = 1.0
        self.status = {
            "infection": {
                "turns_left": 0,
                "damage_per_turn": 0.0
            },
            "poison": {
                "turns_left": 0,
                "damage_per_turn": 0.0
            }
        }
        self.fight = False
        
    def move(self,
             d_row: int,
             d_col: int,
             board: 'Board') -> None:
        self.position = (self.position[0] + d_row, self.position[1] + d_col)
        board.reveal(self.position)

    def attack(self,
               target: 'Damageable') -> float:
        if self.weapon.is_available():
            if isinstance(self.weapon, MeleeWeapon):
                damage_dealt = self.weapon.damage(self.rage)
            else:
                damage_dealt = self.weapon.damage(self.accuracy)
                self.weapon.consume_ammo()
            actual_damage = target.take_damage(damage_dealt)
            return actual_damage
        return 0.0
            
    def choose_weapon(self,
                      new_weapon: 'Weapon') -> None:
        self.weapon = new_weapon
        print(f"You have equipped a {Fore.BLUE}{type(new_weapon).__name__}{Style.RESET_ALL}!")

    def apply_status_tick(self) -> float:
        for i in list(self.status.keys()):
            if self.status[i]["turns_left"] > 0:
                damage = self.status[i]["damage_per_turn"]
                self.take_damage(damage)
                self.status[i]["turns_left"] -= 1
                if i == "infection":
                    print(f"{Fore.RED}Infection{Style.RESET_ALL} deals {Fore.RED}{damage} damage{Style.RESET_ALL} to you!")
                elif i == "poison":
                    print(f"{Fore.RED}Poison{Style.RESET_ALL} deals {Fore.RED}{damage} damage{Style.RESET_ALL} to you!")

    def add_coins(self,
                 amount: int) -> None:
        self.coins += amount
        print(f"{Fore.YELLOW}{amount} coins{Style.RESET_ALL} added! You now have {Fore.YELLOW}{self.coins} coins{Style.RESET_ALL}.")

    def use_bonus(self,
                  bonus: 'Bonus') -> None:
        """Unnecessary man in the middle method, functionality implemented in Bonus.apply()"""

    def buy_auto_if_needed(self,
                           bonus: str) -> 'Bonus':
        """Unnecessary, no useful bonuses can be bought automatically"""

    def symbol(self) -> str:
        return Fore.GREEN+"P"+Style.RESET_ALL
    
    def change_fight(self) -> None:
        if self.fight:
            self.fight = False
        else: self.fight = True

    def add_to_inventory(self,
                         bonus: 'Bonus') -> None:
        """Adds bonus to inventory"""
        
        key = type(bonus).__name__
        
        if key in ("Medkit", "Rage", "Accuracy"):
            self.inventory[key].append(bonus)
            print(f"{Fore.YELLOW}{type(bonus).__name__}{Style.RESET_ALL} added to Inventory!")
        
        elif key == "Coins":
            bonus.apply(self)
            
        elif key == "Arrows":
            if isinstance(self.weapon, Bow):
                self.weapon.ammo += bonus.amount
                print(f"{Fore.YELLOW}{bonus.amount} Arrows{Style.RESET_ALL} added to your {Fore.BLUE}Bow{Style.RESET_ALL}!")
            else:
                self.inventory["Arrows"].append(bonus)
                print(f"{Fore.YELLOW}Arrows{Style.RESET_ALL} added to Inventory!")
                
        elif key == "Bullets":
            if isinstance(self.weapon, Revolver):
                self.weapon.ammo += bonus.amount
                print(f"{Fore.YELLOW}{bonus.amount} Bullets{Style.RESET_ALL} added to your {Fore.BLUE}Revolver{Style.RESET_ALL}!")
            else:
                self.inventory["Bullets"].append(bonus)
                print(f"{Fore.YELLOW}Bullets{Style.RESET_ALL} added to Inventory!")
        
    def show_inventory(self,
                       board: 'Board') -> None:
        """Displays player's inventory"""
        
        print(f"\n{Fore.GREEN}--- Inventory ---{Style.RESET_ALL}")
        
        print(f"Weapon: {Fore.BLUE}{self.weapon.name}{Style.RESET_ALL} (Max Damage: {self.weapon.max_damage})" + (f" (Ammo: {self.weapon.ammo})" if type(self.weapon).__name__ in ("Bow", "Revolver") else ""))
        
        print(f"{Fore.YELLOW}Coins{Style.RESET_ALL}: {self.coins}\n")
        
        bonus_choice = input(f"""Usable bonuses:
1. {Fore.YELLOW}Medkit{Style.RESET_ALL}: {len(self.inventory["Medkit"])}
2. {Fore.YELLOW}Rage{Style.RESET_ALL}: {len(self.inventory["Rage"])}
3. {Fore.YELLOW}Accuracy{Style.RESET_ALL}: {len(self.inventory["Accuracy"])}
4. {Fore.YELLOW}Arrows{Style.RESET_ALL}: {sum(bonus.amount for bonus in self.inventory["Arrows"])}
5. {Fore.YELLOW}Bullets{Style.RESET_ALL}: {sum(bonus.amount for bonus in self.inventory["Bullets"])}
6. Close Inventory
Your choice: """)
        
        if not player.fight:
            clear()
            board.render(player)
            print()
        
        if bonus_choice.strip() == "1":
            if len(self.inventory["Medkit"]) > 0:
                print(f"{Fore.YELLOW}Medkits{Style.RESET_ALL}:")
                for i in range(len(self.inventory["Medkit"])):
                    print(f"{i+1}. Heals {self.inventory["Medkit"][i].power} HP")
                player_choice = input(f"Use Medkit (1-{len(self.inventory["Medkit"])}): ")
                medkit = self.inventory["Medkit"].pop(int(player_choice.strip())-1)
                medkit.apply(self)
            else:
                print("No Medkits in inventory!")
                
        elif bonus_choice.strip() == "2":
            if len(self.inventory["Rage"]) > 0:
                print(f"{Fore.YELLOW}Rage bonuses{Style.RESET_ALL}:")
                for i in range(len(self.inventory["Rage"])):
                    print(f"{i+1}. +{self.inventory["Rage"][i].multiplier} Rage")
                player_choice = input(f"Use Rage bonus (1-{len(self.inventory["Rage"])}): ")
                rage_bonus = self.inventory["Rage"].pop(int(player_choice.strip())-1)
                rage_bonus.apply(self)
            else:
                print("No Rage bonuses in inventory!")
                
        elif bonus_choice.strip() == "3":
            if len(self.inventory["Accuracy"]) > 0:
                print(f"{Fore.YELLOW}Accuracy bonuses{Style.RESET_ALL}:")
                for i in range(len(self.inventory["Accuracy"])):
                    print(f"{i+1}. +{self.inventory["Accuracy"][i].multiplier} Accuracy")
                player_choice = input(f"Use Accuracy bonus (1-{len(self.inventory["Accuracy"])}): ")
                accuracy_bonus = self.inventory["Accuracy"].pop(int(player_choice.strip())-1)
                accuracy_bonus.apply(self)
            else:
                print("No Accuracy bonuses in inventory!")
                
        elif bonus_choice.strip() == "4":
            if type(player.weapon).__name__ == "Bow":
                if len(self.inventory["Arrows"]) > 0:
                    print(f"Arrows: {sum(bonus.amount for bonus in self.inventory["Arrows"])}")
                    player_choice = input("Load Arrows? (y/n): ")
                    for i in range(len(self.inventory["Arrows"])):
                        arrows_bonus = self.inventory["Arrows"][i]
                        arrows_bonus.apply(self)
                    self.inventory["Arrows"] = []
                else:
                    print("No Arrows in inventory!")
            else:
                print("You don't have a Bow!")
                
        elif bonus_choice.strip() == "5":
            if type(player.weapon).__name__ == "Revolver":
                if len(self.inventory["Bullets"]) > 0:
                    print(f"Bullets: {sum(bonus.amount for bonus in self.inventory["Bullets"])}")
                    player_choice = input("Load Bullets? (y/n): ")
                    for i in range(len(self.inventory["Bullets"])):
                        bullets_bonus = self.inventory["Bullets"][i]
                        bullets_bonus.apply(self)
                    self.inventory["Bullets"] = []
                else:
                    print("No Bullets in inventory!")
            else:
                print("You don't have a Revolver!")
        
        print()       
        

class Rat(Enemy):

    def __init__(self,
                 position: tuple[int, int]):
        lvl = randint(1, 10)
        super().__init__(position, 200, 15 * (1 + lvl / 10), lvl)
        self.infection_chance = 0.25
        self.flee_chance_low_hp = 0.10
        self.flee_treshold = 0.15
        self.infection_damage_base = 5.0
        self.infection_turns = 3

    def before_turn(self,
                    player: 'Player') -> None:
        if self.hp / self.max_hp < self.flee_treshold:
            chance = randint(1, 100) / 100
            if chance <= self.flee_chance_low_hp:
                print(f"{Fore.RED}Rat{Style.RESET_ALL} fleed!")
                self.hp = 0
                return "fled"
        
        infection_chance_roll = randint(1, 100) / 100
        if infection_chance_roll <= self.infection_chance:
            if "infection" not in player.status:
                player.status["infection"] = {
                    "turns_left": player.status["infection"]["turns_left"] + self.infection_turns,
                    "damage_per_turn": self.infection_damage_base * (1 + self.lvl / 10)
                }
                print(f"{Fore.RED}Rat{Style.RESET_ALL} has infected you for {self.infection_turns} turns!")

    def attack(self,
               target: 'Damageable') -> float:
        damage = self.roll_enemy_damage()
        actual_damage = target.take_damage(damage)
        return actual_damage


class Spider(Enemy):
    
    def __init__(self,
                 position: tuple[int, int]):
        lvl = randint(1, 10)
        super().__init__(position, 250, 20 * (1 + lvl / 10), lvl)
        self.poison_chance = 0.10
        self.summon_chance_low_hp = 0.10
        self.poison_damage_base = 15.0
        self.call_treshold = 0.15
        self.poison_turns = 2

    def before_turn(self,
                    player: 'Player') -> None:
        if self.hp / self.max_hp < self.call_treshold:
            chance = randint(1, 100) / 100
            if chance <= self.summon_chance_low_hp:
                print(f"{Fore.RED}Spider{Style.RESET_ALL} has summoned a new {Fore.RED}Spider{Style.RESET_ALL}!")
                # TODO ЗЛОЕ
                
        poison_chance_roll = randint(1, 100) / 100
        if poison_chance_roll <= self.poison_chance:
            if "poison" not in player.status:
                player.status["poison"] = {
                    "turns_left": player.status["poison"]["turns_left"] + self.poison_turns,
                    "damage_per_turn": self.poison_damage_base * (1 + self.lvl / 10)
                }
                print(f"{Fore.RED}Spider{Style.RESET_ALL} has poisoned you for {self.poison_turns} turns!")
        

    def attack(self,
               target: 'Damageable') -> float:
        damage = self.roll_enemy_damage()
        actual_damage = target.take_damage(damage)
        return actual_damage


class Skeleton(Enemy):
    
    def __init__(self,
                 position: tuple[int, int],
                 weapon: 'Weapon'):
        lvl = randint(1, 10)
        super().__init__(position, 150, 10 * (1 + lvl / 10), lvl)
        self.weapon = weapon

    def before_turn(self,
                    player: 'Player'):
        """Does nothing"""

    def attack(self,
               target: 'Damageable') -> float:
    
        if self.weapon.is_available():
            if type(self.weapon).__name__ in ("Fist", "Stick"):
                damage_dealt = self.weapon.damage(1)
            else:
                damage_dealt = self.weapon.damage(1)
                self.weapon.consume_ammo()
            actual_damage = target.take_damage(damage_dealt)
            return actual_damage

    def drop_loot(self,
                  player: 'Player') -> 'Weapon' | None:
        if type(self.weapon).__name__ != "Fist":
            print(f"The {Fore.RED}Skeleton{Style.RESET_ALL} dropped a {Fore.BLUE}{type(self.weapon).__name__}{Style.RESET_ALL}!")
            player_ammo_str = f" (Ammo: {player.weapon.ammo})" if type(player.weapon).__name__ in ("Bow", "Revolver") else ""
            new_ammo_str = f" (Ammo: {self.weapon.ammo})" if type(self.weapon).__name__ in ("Bow", "Revolver") else ""
            weapon_choice = input(f"\nWould you like to swap your {Fore.BLUE}{type(player.weapon).__name__}{Style.RESET_ALL}{player_ammo_str} for a {Fore.BLUE}{type(self.weapon).__name__}{Style.RESET_ALL}{new_ammo_str}? (y/n): ")
            if weapon_choice.strip().lower() == "y":
                player.choose_weapon(self.weapon)
            return self.weapon
        return None



class Fist(MeleeWeapon):
    
    def __init__(self, 
                 position: tuple[int, int]):
        super().__init__(position, "Fist", 20)
    
    def is_available(self):
        return True

class Stick(MeleeWeapon):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, "Stick", 25)
        self.durability = randint(10, 20)
    
    def is_available(self):
        return self.durability > 0


class Bow(RangedWeapon):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, "Bow", 35, randint(10, 15))


class Revolver(RangedWeapon):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position, "Revolver", 45, randint(5, 10))



class Medkit(Bonus):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.power = randint(10, 40)

    def apply(self,
              player: 'Player') -> None:
        healed_amount = player.heal(self.power)
        print(f"{Fore.GREEN}{healed_amount} HP{Style.RESET_ALL} restored!")


class Rage(Bonus):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.multiplier = randint(1, 10) / 10
        self.price = 50

    def apply(self,
              player: 'Player') -> None:
        player.rage += self.multiplier
        print(f"{Fore.YELLOW}Rage{Style.RESET_ALL} increased to {player.rage}!")

class Arrows(Bonus):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.amount = randint(1, 20)

    def apply(self,
              player: 'Player') -> None:
        if isinstance(player.weapon, Bow):
            player.weapon.ammo += self.amount
            print(f"{Fore.YELLOW}{self.amount} Arrows{Style.RESET_ALL} added to your {Fore.BLUE}Bow{Style.RESET_ALL}!")

class Bullets(Bonus):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.amount = randint(1, 10)

    def apply(self,
              player: 'Player') -> None:
        if isinstance(player.weapon, Revolver):
            player.weapon.ammo += self.amount
            print(f"{Fore.YELLOW}{self.amount} Bullets{Style.RESET_ALL} added to your {Fore.BLUE}Revolver{Style.RESET_ALL}!")


class Accuracy(Bonus):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.multiplier = randint(1, 10) / 10
        self.price = 50

    def apply(self,
              player: 'Player') -> None:
        player.accuracy += self.multiplier
        print(f"{Fore.YELLOW}Accuracy{Style.RESET_ALL} increased to {player.accuracy}!")


class Coins(Bonus):
    
    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.amount = randint(50, 100)

    def apply(self,
              player: 'Player') -> None:
        player.add_coins(self.amount)



class Tower(Structure):

    def __init__(self,
                 position: tuple[int, int]):
        super().__init__(position)
        self.reveal_radius = 2

    def interact(self,
                 player: 'Player',
                 board: 'Board'):
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_position = (player.position[0]+i, player.position[1]+j)
                if board.in_bounds(new_position):
                    board.reveal(new_position)

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
              entity: 'Entity' | None,
              pos: tuple[int, int]) -> None:
        if isinstance(entity, Entity):
            self.grid[pos[0]][pos[1]] = (entity, True)
        else:
            self.grid[pos[0]][pos[1]] = (None, True)
         
    def entity_at(self,
                  pos: tuple[int, int]) -> 'Entity' | None:
        return self.grid[pos[0]][pos[1]][0]
    
    def reveal(self,
               pos: tuple[int, int]) -> None:
        """Reveals cell at position"""
        self.grid[pos[0]][pos[1]] = (self.grid[pos[0]][pos[1]][0], True)

    def in_bounds(self,
                  pos: tuple[int, int]) -> bool:
        return (0 <= pos[0] <= (self.rows-1) and 0 <= pos[1] <= (self.cols-1))

    def render(self, player: 'Player'):
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
        print(f"HP: {Fore.GREEN}{player.hp}/{player.max_hp}{Style.RESET_ALL} | Weapon: {Fore.BLUE}{player.weapon.name}{Style.RESET_ALL} | Coins: {Fore.YELLOW}{player.coins}{Style.RESET_ALL}")


def fight(player: 'Player',
          enemy: 'Enemy',
          board: 'Board'):
    """Fighting scene"""

    print(f"\n{Fore.GREEN}Player{Style.RESET_ALL} HP: {Fore.GREEN}{player.hp}/{player.max_hp}{Style.RESET_ALL}")
    print(f"{Fore.RED}{type(enemy).__name__}{Style.RESET_ALL} HP: {Fore.RED}{enemy.hp}/{enemy.max_hp}{Style.RESET_ALL}")
    
    while player.is_alive() and enemy.is_alive():
        result = enemy.before_turn(player)
        if result == "fled":
            board.place(None, player.position)
            break
        player_choice = input("""\nChoose your action:
1. Attack
2. Use Bonus
Action: """).strip().lower()
        if player_choice == "1":
            damage_dealt = round(player.attack(enemy), 1)
            print(f"\nYou dealt {Fore.GREEN}{damage_dealt} damage{Style.RESET_ALL} to the {Fore.RED}{type(enemy).__name__}{Style.RESET_ALL}!")
            if enemy.is_alive():
                print(f"{Fore.GREEN}Player{Style.RESET_ALL} HP: {Fore.GREEN}{player.hp}/{player.max_hp}{Style.RESET_ALL}")
                print(f"{Fore.RED}{type(enemy).__name__}{Style.RESET_ALL} HP: {Fore.RED}{enemy.hp}/{enemy.max_hp}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}{type(enemy).__name__} defeated!{Style.RESET_ALL}")
                if isinstance(enemy, Skeleton):
                    enemy.drop_loot(player)
                print(f"You received {Fore.YELLOW}{enemy.reward_coins} coins{Style.RESET_ALL}!")
                player.add_coins(enemy.reward_coins)
                board.place(None, player.position)
                break
            damage_dealt = round(enemy.attack(player), 1)
            print(f"\nThe {Fore.RED}{type(enemy).__name__}{Style.RESET_ALL} dealt {Fore.RED}{damage_dealt} damage{Style.RESET_ALL} to you!")
            if player.is_alive():
                print(f"{Fore.GREEN}Player{Style.RESET_ALL} HP: {Fore.GREEN}{player.hp}/{player.max_hp}{Style.RESET_ALL}")
                print(f"{Fore.RED}{type(enemy).__name__}{Style.RESET_ALL} HP: {Fore.RED}{enemy.hp}/{enemy.max_hp}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}You died!{Style.RESET_ALL}")
                exit()
            if not player.weapon.is_available():
                player.choose_weapon(Fist((0, 0)))
            if isinstance(enemy, Skeleton):
                if not enemy.weapon.is_available():
                    enemy.weapon = Fist((0, 0))
            player.apply_status_tick()
        
        elif player_choice == "2":
            player.show_inventory(board)
    

# TODO add save/load functionality

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
                skeleton_weapon = [Fist((0, 0)), Stick((0, 0)), Bow((0, 0)), Revolver((0, 0))]
                enemies = [Rat((x, y)), Spider((x, y)), Skeleton((x, y), skeleton_weapon[randint(0, 3)])]
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


def game(board: 'Board',
         player: 'Player') -> None:
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
            player.show_inventory(board)
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
                entity.interact(player, board)
                input("Press Enter to continue...\n")
                
            elif isinstance(entity, Bonus):
                print(f"\nYou have found a bonus: {Fore.YELLOW}{type(entity).__name__}{Style.RESET_ALL}!")
                if isinstance(entity, Coins):
                    entity.apply(player)
                    board.place(None, player.position)
                else:
                    player.add_to_inventory(entity)
                board.place(None, player.position)
                input("Press Enter to continue...\n")
                
            elif isinstance(entity, Weapon):
                print(f"\nYou have found a {Fore.BLUE}{type(entity).__name__}{Style.RESET_ALL}!")
                player_ammo_str = f" (Ammo: {player.weapon.ammo})" if type(player.weapon).__name__ in ("Bow", "Revolver") else ""
                new_ammo_str = f" (Ammo: {entity.ammo})" if type(entity).__name__ in ("Bow", "Revolver") else ""
                weapon_choice = input(f"\nWould you like to swap your {Fore.BLUE}{type(player.weapon).__name__}{Style.RESET_ALL}{player_ammo_str} for a {Fore.BLUE}{type(entity).__name__}{Style.RESET_ALL}{new_ammo_str}? (y/n): ")
                if weapon_choice.strip().lower() == "y":
                    if type(player.weapon).__name__ != "Fist":
                        board.place(player.weapon, player.position)
                    else:
                        board.place(None, player.position)
                    player.choose_weapon(entity)
                
            elif isinstance(entity, Enemy):
                print(f"\nYou have encountered a {Fore.RED}{type(entity).__name__} {entity.lvl} lvl.{Style.RESET_ALL}!")
                player.change_fight()
                fight(player, entity, board)
                player.change_fight()
                input("Press Enter to continue...\n")
                
                
        if player.position == board.goal:
            clear()
            board.render(player)
            print(f"\n{Fore.CYAN}You Won!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Coins{Style.RESET_ALL}: {player.coins}")
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
    try:
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
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}Game exited.{Style.RESET_ALL}")
