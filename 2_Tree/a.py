import json
from collections import deque





def generate_id(first_name: str, second_name: str, position_name: str) -> str:
    def pad(s: str) -> str:
        s = s.lower()
        return s[:3] if len(s) >= 3 else s + "0"
    return pad(first_name) + pad(second_name) + pad(position_name)


class Position:
    def __init__(self, position_name: str, first_name: str = "", second_name: str = "", parent: Position | None = None) -> None:
        self.first_name = first_name
        self.second_name = second_name
        self.name = position_name
        self.parent =parent
        self.subordinates: list[Position] = []
        self.id = generate_id(first_name, second_name, position_name)







class Company:
    def __init__(self, root: Position) -> None:
        self.root = root

    @classmethod
    def from_json(cls, file_path: str) -> Company:
        with open(file_path, encoding="utf-8") as file:
            records = json.load(file)

        nodes: dict[str, Position] = {}
        for record in records:
            node = Position(record["name"], record.get("first_name", ""), record.get("second_name", ""))
            nodes[record["name"]] = node

        root = None
        for record in records:
            node = nodes[record["name"]]
            if record["parent"] is None:
                root=node
            else:
                parent_node=nodes[record["parent"]]
                node.parent = parent_node
                parent_node.subordinates.append(node)


        return cls(root)


    #бфс
    def find_by_name(self, name: str) -> Position|None:
        if self.root is None:
            return None
        queue= deque()
        queue.append(self.root)
        while len(queue) >0:
            current = queue.popleft()
            if current.name==name:
                return current
            for subordinate in current.subordinates:
                queue.append(subordinate)
        return None

    def insert_position(self, position_name: str, parent_name: str, first_name: str = "",second_name: str = "") -> None:
        parent = self.find_by_name(parent_name)
        if parent is None:
            print("направление не найдено")
            return

        new_position = Position(position_name, first_name,second_name, parent)
        parent.subordinates.append(new_position)

    def print_structure(self) -> None:
        self.print_node(self.root, 0)

    def print_node(self, node: Position, depth: int) -> None:
        
        if node:
            prefix = "- - " * depth
            employee = f"{node.second_name} {node.first_name}".strip()
            print(f"{prefix}{node.name} ({employee})")

            for subordinate in node.subordinates:
                self.print_node(subordinate, depth + 1)
    def close_position(self, position_name: str) -> None:
        position = self.find_by_name(position_name)

        if position is None:
            print("направление не найдено")
            return
        if position.parent is None:
            print("нельзя закрыть корневую позицию")
            return

        position.parent.subordinates.remove(position)



    #бфс
    def remove_employee(self, first_name: str, second_name: str) -> None:
        if self.root is None:
            return
        queue = deque()
        queue.append(self.root)

        while len(queue) > 0:

            current = queue.popleft()
            if current.first_name == first_name and current.second_name == second_name:
                current.first_name = ""
                current.second_name = ""
                current.id = generate_id("", "", current.name)
                return
            for subordinate in current.subordinates:
                queue.append(subordinate)

        print(f"Сотрудник не найден")

    def hire_employee(self, position_name: str, first_name: str, second_name: str) -> None:
        position = self.find_by_name(position_name)

        if position is None:
            print("направление не найдено")
            return
        

        if not (position.first_name == "" and position.second_name == ""):
            print("должность занята")
            return

        position.first_name = first_name
        position.second_name = second_name
        position.id = generate_id(first_name, second_name, position_name)


    def move_position(self, position_name: str, new_parent_name: str) -> None:
        position = self.find_by_name(position_name)
        new_parent = self.find_by_name(new_parent_name)


        if position is None:
            print("направления не найдено")
            return
        if new_parent is None:
            print("направления не найдено")
            return
        if position.parent is None:
            print("нельзя перенести корневую позицию")
            return

        old_parent = position.parent
        for subordinate in position.subordinates:
            subordinate.parent = old_parent
            old_parent.subordinates.append(subordinate)


        old_parent.subordinates.remove(position)

        position.subordinates = []
        position.parent = new_parent
        new_parent.subordinates.append(position)




company = Company.from_json("10_Tree/data.json")
company.print_structure()

company.insert_position("Математика", "Курсы", "Мария", "Козлова")
company.print_structure()
company.close_position("Лагеря")
company.remove_employee("Анна", "Сидорова")

company.hire_employee("Информатика", "Елена", "Громова")

company.hire_employee("Информатика", "Сладкий", "Кокосик")
company.print_structure()



company2 = Company.from_json("10_Tree/data.json")
company2.move_position("Информатика", "Лагеря")
company2.print_structure()