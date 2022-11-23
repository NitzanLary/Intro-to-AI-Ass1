from typing import List
from Agents import Agent
from Graph import Graph
from util import read_file


class World(object):
    def __init__(self, environment):
        V = environment['V']
        E = environment['E']
        self.graph = Graph(V, E)


class Simulator(object):
    def __init__(self, agents: List[Agent], path: str):
        self.agents = agents
        env = read_file(path)
        self.graph = Graph(env['V'], env['E'])

    def display(self):
        self.graph.display({a.name: a.location for a in self.agents})

    def start(self):
        while self.agents:
            for agent in self.agents:
                dst = agent.act(self.graph)
                if dst and self.graph.valid_move(agent.location, dst):
                    self.handle_move(agent, dst)
                print(agent)
                self.display()
            self.agents = [a for a in self.agents if not a.terminated]

    def handle_move(self, agent, dst):
        w = self.graph.get_weight(agent.location, dst)
        p = self.graph.get_people(dst)
        agent.evacuated += p
        agent.actions += 1
        agent.score += 1000 * p - w
        agent.time += w
        agent.location = dst
        self.graph.handle_brittle(dst)
        self.graph.clear_people(dst)
