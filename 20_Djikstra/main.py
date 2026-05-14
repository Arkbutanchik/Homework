import json
import heapq
import math


class Node:
    def __init__(self, id, scatter_coeff, sensor, threshold):
        self.id = id
        self.scatter_coeff = scatter_coeff
        self.sensor = sensor
        self.threshold = threshold


class Edge:
    def __init__(self, u, v, length_m, material, attenuation, noise_coeff, directed):
        self.u = u
        self.v = v
        self.length_m = length_m
        self.material = material
        self.attenuation = attenuation
        self.noise_coeff = noise_coeff
        self.directed = directed

    def travel_time_ms(self, material_speeds: dict) -> float:
        speed = material_speeds[self.material]
        return self.length_m / speed

    def other(self, node_id: str) -> str:
        if node_id == self.u:
            return self.v
        elif node_id == self.v and not self.directed:
            return self.u
        return None

    def propagate_energy(self, E_in: float) -> float:
        return E_in * math.exp(-self.attenuation * self.length_m)

    def propagate_noise(self, noise_in: float) -> float:
        return noise_in + self.noise_coeff


class State:
    def __init__(self, cost, node_id, time_ms, energy, noise, parent):
        self.cost = cost
        self.node_id = node_id
        self.time_ms = time_ms
        self.energy = energy
        self.noise = noise
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost


class SignalSystem:
    def __init__(self):
        self.start = None
        self.R_ms = None
        self.initial_energy = None
        self.alpha = None
        self.beta = None
        self.gamma = None
        self.materials = {}
        self.nodes: dict[str, Node] = {}
        self.adjacency: dict[str, list[Edge]] = {}

    def load_from_json(self, path: str):
        with open(path) as f:
            data = json.load(f)

        self.start = data["start"]
        self.R_ms = data["R_ms"]
        self.initial_energy = data["initial_energy"]
        self.alpha = data["alpha"]
        self.beta = data["beta"]
        self.gamma = data["gamma"]
        self.materials = data["materials"]

        for v in data["vertices"]:
            node = Node(
                id=v["id"],
                scatter_coeff=v["scatter_coeff"],
                sensor=v["sensor"],
                threshold=v["threshold"],
            )
            self.nodes[node.id] = node
            self.adjacency[node.id] = []

        for e in data["edges"]:
            edge = Edge(
                u=e["u"],
                v=e["v"],
                length_m=e["length_m"],
                material=e["material"],
                attenuation=e["attenuation"],
                noise_coeff=e["noise_coeff"],
                directed=e["directed"],
            )
            self.adjacency[edge.u].append(edge)
            if not edge.directed:
                self.adjacency[edge.v].append(edge)

    def compute_cost(self, time_ms, noise, energy):
        return self.gamma * time_ms + self.alpha * noise + self.beta * (1.0 / energy)

    def dijkstra(self):
        best_cost = {nid: float("inf") for nid in self.nodes}
        best_state = {}

        init_energy = self.initial_energy
        init_cost = self.compute_cost(0.0, 0.0, init_energy)

        best_cost[self.start] = init_cost
        best_state[self.start] = State(
            cost=init_cost,
            node_id=self.start,
            time_ms=0.0,
            energy=init_energy,
            noise=0.0,
            parent=None,
        )

        heap = [best_state[self.start]]

        while heap:
            cur = heapq.heappop(heap)

            if cur.cost > best_cost[cur.node_id]:
                continue

            for edge in self.adjacency[cur.node_id]:
                neighbor_id = edge.other(cur.node_id)
                if neighbor_id is None:
                    continue

                neighbor_node = self.nodes[neighbor_id]

                new_time = cur.time_ms + edge.travel_time_ms(self.materials)
                if new_time > self.R_ms:
                    continue

                E_after_edge = edge.propagate_energy(cur.energy)
                E_new = E_after_edge * (1 - neighbor_node.scatter_coeff)

                if E_new <= 0:
                    continue

                new_noise = edge.propagate_noise(cur.noise)
                new_cost = self.compute_cost(new_time, new_noise, E_new)

                if new_cost < best_cost[neighbor_id]:
                    best_cost[neighbor_id] = new_cost
                    state = State(
                        cost=new_cost,
                        node_id=neighbor_id,
                        time_ms=new_time,
                        energy=E_new,
                        noise=new_noise,
                        parent=cur.node_id,
                    )
                    best_state[neighbor_id] = state
                    heapq.heappush(heap, state)

        self._best_state = best_state
        return best_state

    def restore_path(self, node_id: str) -> list[str]:
        path = []
        cur = node_id
        while cur is not None:
            path.append(cur)
            state = self._best_state.get(cur)
            cur = state.parent if state else None
        return list(reversed(path))

    def run(self, output_path: str):
        best_state = self.dijkstra()

        lines = [f"R = {self.R_ms} ms", "достижимые датчики"]
        results = []

        for nid, node in sorted(self.nodes.items()):
            if not node.sensor:
                continue
            state = best_state.get(nid)
            if state is None or state.cost == float("inf"):
                continue
            if state.time_ms > self.R_ms:
                continue
            if state.energy < node.threshold:
                continue

            path_str = " → ".join(self.restore_path(nid))
            results.append(f"{nid}:\ntime = {state.time_ms}\nenergy = {state.energy}\nnoise = {state.noise}\ncost = {state.cost}\npath = {path_str}")

        lines.append("\n".join(results) if results else "нет достижимых датчиков")

        result = "\n".join(lines)
        print(result)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)


system = SignalSystem()
system.load_from_json("20_Djikstra/data.json")
system.run("20_Djikstra/result.txt")
