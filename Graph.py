from typing import Dict
import networkx as nx
import matplotlib.pyplot as plt


class Graph(object):
    def __init__(self, vertices: Dict, edges: Dict):
        self.broken_nodes = []
        self.vertices_info = vertices
        self.G = nx.Graph()
        self.G.add_nodes_from(vertices.keys())
        self.G.add_edges_from((str(e["v1"]), str(e["v2"]), {"weight": e["w"]}) for e in edges.values())
        self.pos = nx.spring_layout(self.G)  # for drawing

    def get_weight(self, v1, v2):
        assert v2 in self.G[v1]
        return self.G[v1][v2]["weight"]

    def valid_move(self, src, dst):
        return dst in self.G[src] and dst not in self.broken_nodes

    def __str__(self):
        return f"info:\n" \
               f"{self.vertices_info}"

    def display(self, agents_locations):
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels={e: v["weight"] for e, v in self.G.edges.items()},
                                     font_size=20)
        nx.draw_networkx(self.G, self.pos, with_labels=False)
        nl = self.create_labels(self.vals_to_keys(agents_locations))
        nx.draw_networkx_labels(self.G, self.pos, labels=nl, font_size=16)
        plt.show()

    def create_labels(self, agents_locations):
        nl = {}
        for v, item in self.vertices_info.items():
            s = ""
            if v in self.broken_nodes:
                s += 'X\n'
            s += f"v:{v}\np:{item['people']}"
            if v in agents_locations:
                s += f"\n{agents_locations[v]}"
            nl[v] = s
        return nl

    def get_people(self, dst):
        return self.vertices_info[dst]["people"]

    def handle_brittle(self, node):
        if self.vertices_info[node]["brittle"]:
            self.broken_nodes.append(node)

    def clear_people(self, node):
        self.vertices_info[node]["people"] = 0

    def vals_to_keys(self, agents_locations):
        new_dic = {}
        for k, v in agents_locations.items():
            new_dic[v] = new_dic.get(v, []) + [k]
        return new_dic
