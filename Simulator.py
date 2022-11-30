from typing import List
from Agents import Agent
from World import World
from util import read_file


class Simulator:
    def __init__(self, agents: List[Agent], path: str):
        self.agents = agents
        env = read_file(path)
        self.world = World(env)
        for agent in self.agents:
            agent.set_world(self.world)

    def display(self):
        self.world.display({a.name: a.state for a in self.agents})

    def start(self):
        while self.agents:
            for agent in self.agents:
                dst = agent.act(self.world)
                if dst:
                    self.handle_move(dst)
                print(agent)
                self.display()
            self.agents = [a for a in self.agents if not a.terminated]

    def handle_move(self, dst):
        self.world.handle_brittle(dst)

