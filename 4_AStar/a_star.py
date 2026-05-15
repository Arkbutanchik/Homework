import heapq

class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


class Graph:
    def __init__(self):
        self.nodes = {} # name -> Point
        self.graph = {} # name -> list[tuple]
    
    def add_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = Point(node_id)
            self.graph[node_id] = []
    
    def add_edge(self, from_id, to_id, length, direction):
        self.add_node(from_id)
        self.add_node(to_id)
        self.graph[from_id].append((to_id, length))

        if not direction:
            self.graph[to_id].append((from_id, length))

    def a_star(self, start, end):
        queue = [(0, start)]

        route = {}
        distance = {point: float("inf") for point in self.nodes}
        distance[start] = 0
        h_distances = {point: float("inf") for point in self.nodes}
        h_distances[start] = 0

        while queue:
            h_distance, current_point = heapq.heappop(queue)

            if current_point == end:
                return self.reconstuct_path(route, end), distance[end]
            
            for neighbor, length in self.graph[current_point]:
                new_distance = distance[current_point] + length

                if new_distance < distance[neighbor]:
                    route[neighbor] = current_point
                    distance[neighbor] = new_distance
                    new_h_distance = new_distance + self.heuristic(neighbor, end)
                    h_distances[neighbor] = new_h_distance
                    heapq.heappush(queue, (new_h_distance, neighbor))
        
        return None, float("inf") 


    def heuristic(self, neighbor: str, end: str):
        import math
        neighbor = self.nodes[neighbor]
        end = self.nodes[end]
        return math.hypot(end.x - neighbor.x, end.y - neighbor.y)


    def reconstuct_path(self, route, end):
        path = []
        current = end
        while current:
            path.append(current)
            current = route[current]
        path.reverse()
        return path