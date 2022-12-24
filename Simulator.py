from typing import List

import Fringes
from Agents import *
from World import World
from util import read_file

PROMPT = """
Adversarial - 1
Semi-cooperative - 2
fully cooperative - 3
"""


class Simulator:
    def __init__(self, path: str):
        self.agents = []
        env = read_file(path)
        self.world = World(env)
        # self.agents = [Agent('0', "A1"), Agent('0', "A2")]
        self.agents = [Agent('0', "A1")]

    def display(self):
        self.world.display({agent.name: agent.location for agent in self.agents})

    def start(self):
        self.set_args()
        self.start_rounds()

    def start_rounds(self):
        self.display()
        states = []
        # curr_states = (StateNode(self.agents[0].location, self.world), StateNode(self.agents[1].location, self.world))
        while not self.is_terminated(): # and curr_states not in states
            # states.append(tuple(curr_states))
            curr_states = []
            # todo: end game with the right conditions
            for agent in self.agents:
                dst = agent.act()
                self.handle_move(dst)
                print(agent)
                self.display()
                curr_states.append(StateNode(agent.location, self.world))
            curr_states = tuple(curr_states)

    def handle_move(self, dst):
        self.world.handle_brittle(dst)

    def set_args(self):
        for agent in self.agents:
            agent.set_terminal_test(lambda state: sum(state.people_status.values()) == 0)
            agent.set_world(self.world)
            agent.set_cutoff_test(14)
            agent.set_eval_function(Agent.MST_heuristic)

    def is_terminated(self):
        pass
