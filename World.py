from Graph import Graph
from util import values_to_keys


class World(object):
    def __init__(self, environment):
        self.environment = environment
        V = [v for v in environment['V']]
        E = environment['E']
        self.broken_nodes = []
        self.graph = Graph(V, E)

    def valid_action(self, src, dst):
        return dst not in self.broken_nodes and self.graph.valid_move(src, dst)

    def create_labels(self, agents_locations):
        nl = {}
        for v, item in self.environment['V'].items():
            s = ""
            if v in self.broken_nodes:
                s += 'X\n'
            s += f"v:{v}\np:{item['people']}"
            if v in agents_locations:
                s += f"\n{agents_locations[v]}"
            nl[v] = s
        return nl

    def display(self, agents_locations):
        self.graph.display(self.create_labels(values_to_keys(agents_locations)))

    def get_people(self, dst):
        return self.environment[dst]["people"]

    def get_weight(self, v1, v2):
        return self.graph.get_weight(v1, v2)

    def handle_brittle(self, node):
        if self.environment[node]["brittle"]:
            self.broken_nodes.append(node)

    def clear_people(self, node):
        self.environment[node]["people"] = 0
