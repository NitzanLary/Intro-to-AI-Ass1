from typing import Dict, List
import networkx as nx
import matplotlib.pyplot as plt


class Graph(object):
    def __init__(self, vertices: List, edges: Dict):
        self.G = nx.Graph()
        self.G.add_nodes_from(vertices)
        self.G.add_edges_from((str(e["v1"]), str(e["v2"]), {"weight": e["w"]}) for e in edges.values())
        self.pos = nx.spring_layout(self.G)  # for drawing

    def get_weight(self, v1, v2):
        assert v2 in self.G[v1]
        return self.G[v1][v2]["weight"]

    def valid_move(self, src, dst):
        return dst in self.G[src]

    def display(self, nodes_labels):
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels={e: v["weight"] for e, v in self.G.edges.items()},
                                     font_size=20)
        nx.draw_networkx(self.G, self.pos, with_labels=False)
        nx.draw_networkx_labels(self.G, self.pos, labels=nodes_labels, font_size=16)
        plt.show()



