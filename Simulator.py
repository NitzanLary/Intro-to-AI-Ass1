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
        a1_loc, a2_loc = '0', '0'
        self.agents = [MiniMaxAgent(a1_loc, 0), MiniMaxAgent(a2_loc, 1)]
        # self.agents = [SemiCooperativeAgent(a1_loc, 0), SemiCooperativeAgent(a2_loc, 1)]
        self.locations = [a1_loc, a2_loc]
        self.world = World(env, self.locations)
        # self.agents = [Agent('0', "A1")]

    def display(self):
        self.world.display({str(agent.name): agent.location for agent in self.agents})

    def start(self):
        self.set_args()
        self.start_rounds()

    def start_rounds(self):
        self.display()
        states = []
        curr_states = StateNode(self.locations[0], self.locations[1], self.world)
        while not self.is_terminated() and curr_states not in states:
            # states.append(curr_states)
            # todo: end game with the right conditions
            for agent_num, agent in enumerate(self.agents):
                dst = agent.act()
                self.handle_move(dst, agent_num)
                print(agent)
                self.display()
            loc1, loc2 = self.locations
            # curr_states = StateNode(loc1, loc2, self.world)

    def handle_move(self, dst, agent):
        self.world.handle_brittle(dst)
        self.locations[agent] = dst

    def set_args(self):
        for agent in self.agents:
            agent.set_terminal_test(lambda state: sum(state.people_status.values()) == 0)
            agent.set_world(self.world)
            agent.set_cutoff_test(10)
            agent.set_eval_function(MiniMaxAgent.MST_heuristic)

    def is_terminated(self):
        pass
