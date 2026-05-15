class Node:
    def __init__(self):
        self.has_fuel:bool

class Edge:
    def __init__(self):
        pass

class Plane:
    def __init__(self):
        self.tank_capacity: float
        self.base_fuel: float
        self.cruise_speed: float
        self.empty_mass: float
        self.fuel_current_mass: float = self.tank_capacity

    def count_current_mass(self) -> float:
        m = self.empty_mass + self.fuel_current_mass
        return m

class Graph:
    def __init__(self):
        pass

