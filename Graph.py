import math
from typing import Dict, List
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


class Graph:
    def __init__(self, vertices: List, edges: Dict):
        self.G = nx.Graph()
        self.G.add_nodes_from(vertices)
        self.G.add_edges_from((str(e["v1"]), str(e["v2"]), {"weight": e["w"]}) for e in edges.values())
        self.pos = nx.spring_layout(self.G)  # for drawing

    def get_weight(self, v1, v2):
        assert v2 in self.G[v1]
        return self.G[v1][v2]["weight"]

    def get_neighbors(self, v1):
        return self.G.neighbors(v1)

    def valid_move(self, src, dst):
        return dst in self.G[src]

    def display(self, nodes_labels):
        # nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        # nt.from_nx(self.G)
        # nt.show("Graph.html")
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels={e: v["weight"] for e, v in self.G.edges.items()},
                                     font_size=20)
        nx.draw_networkx(self.G, self.pos, with_labels=False)
        nx.draw_networkx_labels(self.G, self.pos, labels=nodes_labels, font_size=16)
        plt.show()

    def get_shortest_path(self, v1, v2, without=()):
        without_nodes = self.G.copy()
        without_nodes.remove_nodes_from(set(without) - {v1})
        if nx.has_path(without_nodes, v1, v2):
            return nx.single_source_dijkstra(without_nodes, v1, v2)
        return math.inf, []

    def change_to_infinite(self, node):
        for v1, v2 in nx.edges(self.G, node):
            self.G[v1][v2]["weight"] = float("inf")

    def get_MST_size(self, around_nodes: list):
        full_graph_around_nodes = nx.Graph()
        for i, v_i in enumerate(around_nodes):
            for j, v_j in enumerate(around_nodes[i + 1:]):
                dist, path = self.get_shortest_path(v_i, v_j)
                full_graph_around_nodes.add_edge(v_i, v_j, weight=dist)
        mst = nx.minimum_spanning_tree(full_graph_around_nodes)
        # pos = nx.spring_layout(full_graph_around_nodes)
        # subax1 = plt.subplot(121)
        # nx.draw(full_graph_around_nodes, pos=pos, with_labels=True)
        # nx.draw_networkx_edge_labels(mst, pos=pos)
        # subax2 = plt.subplot(122)
        # pos = nx.spring_layout(mst)
        # nx.draw(mst, pos=pos, with_labels=True)
        # nx.draw_networkx_edge_labels(mst, pos=pos)
        #
        # plt.show()
        return mst.size()
