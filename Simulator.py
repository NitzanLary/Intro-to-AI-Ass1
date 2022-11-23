from typing import List
from Agents import Agent
from World import World
from util import read_file


class Simulator(object):
    def __init__(self, agents: List[Agent], path: str):
        self.agents = agents
        env = read_file(path)
        self.world = World(env)

    def display(self):
        self.world.display({a.name: a.location for a in self.agents})

    def start(self):
        while self.agents:
            for agent in self.agents:
                dst = agent.act(self.world)
                if dst and self.world.valid_action(agent.location, dst):
                    self.handle_move(agent, dst)
                print(agent)
                self.display()
            self.agents = [a for a in self.agents if not a.terminated]

    def handle_move(self, agent, dst):
        w = self.world.get_weight(agent.location, dst)
        p = self.world.get_people(dst)
        agent.evacuated += p
        agent.actions += 1
        agent.score += 1000 * p - w
        agent.time += w
        agent.location = dst
        self.world.handle_brittle(dst)
        self.world.clear_people(dst)
