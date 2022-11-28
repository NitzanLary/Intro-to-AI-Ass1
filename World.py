from functools import total_ordering
from typing import Dict, Set

from Graph import Graph
from util import values_to_keys


class World:
    def __init__(self, environment):
        self.environment = environment
        V = [v for v in environment['V']]
        E = environment['E']
        self.broken_nodes = set()
        self.graph = Graph(V, E)

    def valid_action(self, src, dst):
        return dst not in self.broken_nodes and self.graph.valid_move(src, dst)

    def create_labels(self, agents_locations):
        nl = {}
        for v, item in self.environment['V'].items():
            s = ""
            if v in self.broken_nodes:
                s += 'X\n'
            elif v in self.get_brittle_vertices():
                s += 'B\n'
            s += f"v:{v}\np:{item['people']}"
            if v in agents_locations:
                s += f"\n{agents_locations[v]}"
            nl[v] = s
        return nl

    def display(self, agents_locations):
        print(agents_locations)
        self.graph.display(self.create_labels(values_to_keys(agents_locations)))

    def get_people(self, dst):
        return self.environment['V'][dst]["people"]

    def get_weight(self, v1, v2):
        return self.graph.get_weight(v1, v2)

    def get_neighbors(self, v1):
        return self.graph.get_neighbors(v1)

    def handle_brittle(self, node):
        if self.environment['V'][node]["brittle"]:
            self.broken_nodes.add(node)

    def clear_people(self, node):
        self.environment['V'][node]["people"] = 0

    def get_people_status(self):
        return {v: self.environment['V'][v]["people"] for v in self.environment['V']}

    def get_broken_vertices_status(self):
        return self.broken_nodes.copy()

    def get_shortest_path(self, v1, v2):
        return self.graph.get_shortest_path(v1, v2, self.broken_nodes)

    def get_brittle_vertices(self):
        return filter(lambda node: self.environment['V'][node]["brittle"], self.environment['V'])

    def simulate_people_status(self, v, previous_ps: Dict):
        res = previous_ps.copy()
        res[v] = 0
        return res

    def simulate_broken_vertices(self, v, previous_bvs):
        res = previous_bvs.copy()
        if self.environment['V'][v]["brittle"] and v not in res:
            res.add(v)
        return res

    def get_MST_size(self):
        return self.graph.get_MST_size()


@total_ordering
class StateNode:
    def __init__(self, state, parent, world: World, people_status: Dict, broken_nodes_status: Set, f_value=0,
                 g_value=0):
        self.state = state
        self.f_value = f_value
        self.g_value = g_value
        self.parent = parent
        self.people_status = world.simulate_people_status(state, people_status)
        self.broken_nodes_status = world.simulate_broken_vertices(state, broken_nodes_status)

    def __eq__(self, other):
        return self.state == other.state and self.people_status == other.people_status and self.broken_nodes_status == other.broken_nodes_status

    def __gt__(self, other):
        return True
