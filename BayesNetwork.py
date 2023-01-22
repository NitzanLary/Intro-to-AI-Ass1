import itertools
from typing import Tuple, Dict, Any, List

import networkx as nx

from Graph import Graph


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


WEATHER_LIST = ["mild", "stormy", "extreme"]


class BayesNetwork:
    def __init__(self, env_graph: Graph, b_probs: Dict[Any, float], p1: float, p2: float,
                 p_weather: Tuple[float, float, float]):
        """
        A Bayes Network for the given environment graph.
        B(v) is the probability that the vertex v is broken.
        They are conditional independent, and are effected by the weather.
        E(v) is the probability that the vertex v has people.
        They are noisy-OR distributed, and are effected by brittleness of the vertex's neighbors.
        :param env_graph: The environment graph
        :param b_probs: Dictionary of vertices and their probability of breaking given weather = mild
        :param p1: Factor of weight between vertices and their neighbors in the noisy-OR distribution
        :param p2: Factor of probability of having people in a vertex
        :param p_weather: Probability of weather being mild, stormy, or extreme
        """
        self.env_graph = env_graph
        self.b_probs = b_probs
        self.p1 = p1
        self.p2 = p2
        self.p_weather = p_weather
        self.bayes_net = self.create_bayes_net()
        self.b_cpt = self.create_b_cpt()
        self.e_cpt = self.create_e_cpts()

    def create_bayes_net(self):
        """
        Creates a bayes network for the given environment graph.
        :return: The bayes network
        """
        bayes_net = nx.DiGraph()
        bayes_net.add_node("Weather")
        for v in self.env_graph.nodes:
            current_node = "B({})".format(v)
            bayes_net.add_node(current_node)
            bayes_net.add_edge("Weather", current_node)
            for n in self.env_graph.neighbors(v):
                bayes_net.add_edge("B({})".format(n), "E({})".format(v))
            bayes_net.add_edge("B({})".format(v), "E({})".format(v))
        return bayes_net

    def create_b_cpt(self) -> Dict[str, Tuple[float, float, float]]:
        """
        Creates the conditional probability table for the brittle nodes.
        :return: The conditional probability table
        """
        cpt = {}
        for v in self.env_graph.nodes:
            b_given_mild = self.b_probs[v]
            b_given_stormy = min([1, b_given_mild * 2])
            b_given_extreme = min([1, b_given_mild * 3])
            cpt["B({})".format(v)] = (b_given_mild, b_given_stormy, b_given_extreme)
        return cpt

    def create_e_cpts(self) -> Dict[str, Dict[HashableDict, float]]:
        """
        Creates the conditional probability tables for the people nodes, based on the brittleness of their neighbors.
        This is a noisy-OR distribution.
        :return: The conditional probability tables for each people node
        """
        cpts = {}
        for v in self.env_graph.nodes:
            e_v = "E({})".format(v)
            cpts[e_v] = {}
            neighbors = list(self.env_graph.neighbors(v))
            neighbors_and_self = list(self.bayes_net.predecessors(e_v))
            # for each truth assignment to neighbors and self as a dict:
            for truth_assignment in [HashableDict(zip(neighbors_and_self, x)) for x in
                                     itertools.product([0, 1], repeat=len(neighbors_and_self))]:
                # calculate the probability of the truth assignment as a noisy-OR distribution, where p1 is the
                # factor of weight between vertices and their neighbors and p2 is the factor of probability of having
                # people in a vertex
                prob = 1
                for neighbor, b in truth_assignment.items():
                    n = self.random_variable_index(neighbor)
                    if b == 1 and n != v:
                        prob *= min([1, self.p1 * self.env_graph.get_weight(v, n)])
                    elif b == 1 and n == v:
                        prob *= self.p2
                cpts[e_v][truth_assignment] = 1 - prob
        return cpts

    def random_variable_index(self, node: str) -> str:
        """
        Returns the index of the random variable in the node.
        :param node: The node
        :return: The index of the random variable in the node
        """
        return node.split("(")[1].split(")")[0]

    def print_b_cpt(self):
        """
        Prints the conditional probability table for the brittle nodes.
        :return: None
        """
        for node, cpt in self.b_cpt.items():
            print("{}: {}".format(node, cpt))

    def print_e_cpt(self):
        """
        Prints the conditional probability table for the people nodes.
        :return: None
        """
        for node, cpt in self.e_cpt.items():
            print("{}: {}".format(node, cpt))

    def enumerate_ask(self, X: str, evidence: Dict[str, int], domain=None) -> Tuple:
        """
        Enumerates the variable given the evidence.
        :param domain: The domain of the variable
        :param X: The variable to enumerate
        :param evidence: The evidence
        :return: The probability of the variable given the evidence
        """
        if domain is None:
            domain = [0, 1]
        qx = [0.0] * len(domain)
        topological_order = list(nx.topological_sort(self.bayes_net))
        for i, xi in enumerate(domain):
            qx[i] = self.enumerate_all(tuple(topological_order), evidence | {X: xi})
        qx_sum = sum(qx)
        return tuple([x / qx_sum for x in qx]) if qx_sum != 0 else tuple(qx)

    def enumerate_all(self, variables: Tuple[str], evidence: Dict[str, int]) -> float:
        """
        Enumerates all the variables given the evidence.
        :param variables: The variables to enumerate
        :param evidence: The evidence
        :return: The probability of the variables given the evidence
        """
        if len(variables) == 0:
            return 1.0
        Y = variables[0]
        if Y in evidence:
            return self.get_prob(Y, evidence[Y], evidence) * self.enumerate_all(variables[1:], evidence)
        else:
            domain = WEATHER_LIST if Y.startswith("Weather") else [0, 1]
            return sum([self.get_prob(Y, y, evidence) * self.enumerate_all(variables[1:], evidence | {Y: y}) for y in
                        domain])

    def get_prob(self, Y, param, evidence) -> float:
        """
        Gets the probability of a variable given the evidence.
        :param Y: The variable
        :param param: The parameter of the variable
        :param evidence: The evidence
        :return: The probability of the variable given the evidence
        """
        # print("Y: {}, param: {}, evidence: {}".format(Y, param, evidence))
        if Y.startswith("B"):
            prob = self.b_cpt[Y][WEATHER_LIST.index(evidence["Weather"])]
            return prob if param == 1 else 1 - prob
        elif Y.startswith("E"):
            # print("--Y: {}, param: {}, evidence: {}".format(Y, param, evidence))
            # print(list(self.bayes_net.predecessors(Y)))
            # print(self.e_cpt[Y])
            prob = self.e_cpt[Y][HashableDict({k: evidence[k] for k in self.bayes_net.predecessors(Y)})]
            return prob if param == 1 else 1 - prob
        else:
            return self.p_weather[WEATHER_LIST.index(param)]

    # the probability that each of the vertices contains people
    def get_people_prob(self, evidence: Dict[str, int]) -> Dict[str, float]:
        people_prob = {}
        for v in self.env_graph.nodes:
            people_prob[v] = self.enumerate_ask("E({})".format(v), evidence)[1]
        return people_prob

    # the probability that each of the vertices is broken
    def get_broken_prob(self, evidence: Dict[str, int]) -> Dict[str, float]:
        broken_prob = {}
        for v in self.env_graph.nodes:
            broken_prob[v] = self.enumerate_ask("B({})".format(v), evidence)[1]
        return broken_prob

    # the distribution of the weather variable
    def get_weather_prob(self, evidence: Dict[str, int]) -> Tuple:
        return self.enumerate_ask("Weather", evidence, domain=WEATHER_LIST)

    # the probability that a certain path (set of edges) is free from blockages
    def get_path_prob(self, path: List[Tuple[str, str]], evidence: Dict[str, int]) -> float:
        prob = 1
        for edge in path:
            prob *= self.enumerate_ask("B({})".format(edge[0]), evidence)[0]
        return prob

    def get_evidence_from_user(self) -> Dict[str, int]:
        """
        Gets the evidence or some of it from the user.
        :return: The evidence
        """
        evidence = {}
        for v in self.env_graph.nodes:
            ans = int(input("Is vertex {} broken? (0/1) or -1 for unknown ".format(v)))
            if ans == 0 or ans == 1:
                evidence["B({})".format(v)] = ans
            ans = int(input("Is there a person in vertex {}? (0/1) or -1 for unknown ".format(v)))
            if ans == 0 or ans == 1:
                evidence["E({})".format(v)] = ans
        ans = input("What is the weather? ({}): ".format(WEATHER_LIST))
        if ans in WEATHER_LIST:
            evidence["Weather"] = ans
        return evidence

    def get_evidence_from_string(self, s: str) -> Dict[str, int]:
        """
        Gets the evidence or some of it from a string of the following form:
        "B(A)=0,B(B)=1,B(C)=1,E(A)=U,E(B)=0,E(C)=1,Weather=Rainy"
        Where U means unknown.
        :param s: The string
        :return: The evidence
        """
        evidence = {}
        for e in s.split(","):
            k, v = e.split("=")
            if v == "U":
                continue
            evidence[k] = int(v) if k.startswith("B") or k.startswith("E") else v
        return evidence
