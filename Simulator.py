from typing import List

import Fringes
from Agents import *
from World import World
from util import read_file

PROMPT = """
Human: 1
Stupid greedy: 2
Saboteur: 3
Greedy search agent: 4
A* agent: 5
Real time A* agent: 6
A* with company (like saboteur): 7
"""


class Simulator:
    def __init__(self, path: str):
        self.agents = []
        env = read_file(path)
        self.world = World(env)
        for agent in self.agents:
            agent.set_world(self.world)

    def display(self):
        self.world.display({a.name: a.state for a in self.agents})

    def start(self):
        self.get_inputs()
        self.set_args()
        self.start_rounds()

    def start_rounds(self):
        self.display()
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

    def get_inputs(self):
        agents = []
        num_of_agents = int(input("Enter number of agents: "))
        for i in range(num_of_agents):
            agent_no = input(PROMPT)
            agent_location = input("Enter start location: ")
            agent = self.get_agent_from_input(agent_no, agent_location)
            agents.append(agent)
        self.agents = agents

    def get_agent_from_input(self, agent_no, agent_location):
        if agent_no == '1':
            return HumanAgent(agent_location, "Human")
        if agent_no == '2':
            return StupidGreedy(agent_location, "StupidGreedy")
        if agent_no == '3':
            return SaboteurAgent(agent_location, "Saboteur")
        if agent_no == '4':
            return InformedSearchAgent(agent_location, "PureHeuristic", InformedSearchAgent.MST_heuristic,
                                       Fringes.PriorityQueue())
        if agent_no == '5':
            limit = int(input("Enter Limit: "))
            return InformedSearchAgent(agent_location, "A*", InformedSearchAgent.A_star_func, Fringes.PriorityQueue(),
                                       limit)
        if agent_no == '6':
            L = int(input("Enter L: "))
            return RTInformedSearchAgent(agent_location, "RT_A*", InformedSearchAgent.A_star_func,
                                         Fringes.PriorityQueue(),
                                         limit=L)
        return Bonus(agent_location, "A*", InformedSearchAgent.A_star_func, Fringes.PriorityQueue())

    def set_args(self):
        for agent in self.agents:
            agent.set_goal_state(lambda state: sum(state.people_status.values()) == 0)
            agent.set_world(self.world)
