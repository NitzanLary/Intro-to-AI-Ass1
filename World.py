from functools import total_ordering
from typing import Dict, Set, Union

from Graph import Graph
from util import values_to_keys


class World:
    def __init__(self, environment, agents_locations: list):
        self.environment = environment
        V = [v for v in environment['V']]
        E = environment['E']
        self.broken_nodes = set()
        self.graph = Graph(V, E)
        self.agents_locations = agents_locations

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
        self.graph.display(self.create_labels(values_to_keys(agents_locations)))

    def get_people(self, dst):
        return self.environment['V'][dst]["people"]

    def get_weight(self, v1, v2):
        return self.graph.get_weight(v1, v2)

    def get_neighbors(self, v1):
        return (n for n in self.graph.get_neighbors(v1) if n not in self.broken_nodes)

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

    def get_agents_locations(self, agent_index):
        return self.agents_locations[agent_index], self.agents_locations[abs(agent_index - 1)]

    def set_agent_location(self, agent, location):
        self.agents_locations[agent] = location

    def simulate_people_status(self, v1, v2, previous_ps: Dict):
        res = previous_ps.copy()
        res[v1] = 0
        res[v2] = 0
        return res

    def simulate_broken_vertices(self, v1, v2, previous_bvs):
        res = previous_bvs.copy()
        if self.environment['V'][v1]["brittle"] and v1 not in res:
            res.add(v1)
        if self.environment['V'][v2]["brittle"] and v1 not in res:
            res.add(v2)
        return res

    def get_MST_size(self, around_nodes=None, without_nodes=()):
        if not around_nodes:
            around_nodes = list(self.environment['V'].keys())
        return self.graph.get_MST_size(around_nodes, without_nodes)

@total_ordering
class StateNode:

    def __init__(self, location1, location2, world: World, parent: Union["StateNode", None] = None):
        self.location1, self.location2 = location1, location2
        self.parent = parent
        if parent:
            self.people_status = world.simulate_people_status(location1, location2, parent.people_status)
            self.broken_nodes_status = world.simulate_broken_vertices(location1, location2, parent.broken_nodes_status)
        else:
            self.people_status = world.get_people_status()
            self.broken_nodes_status = world.get_broken_vertices_status()
        print(self.location1, self.location2)

    def __eq__(self, other):
        return self.location1 == other.location1 and self.location2 == other.location2 and self.people_status == other.people_status and self.broken_nodes_status == other.broken_nodes_status

    def __lt__(self, other):
        assert type(other) is StateNode
        return self.location1 < other.location1

    def __str__(self):
        return f"StateNode(state={self.location1}, people_status={self.people_status}, broken_nodes_status={self.broken_nodes_status})"

    def __repr__(self):
        return self.__str__()
