import Fringes
from Fringes import PriorityQueue
from Graph import Graph
import Agents

import json

from Simulator import Simulator
from World import StateNode


def main():
    # agent = Agents.HumanAgent('1', "Human")
    # agent = Agents.StupidGreedy(state='1', name="Stupid")
    # agent.set_goal_state(lambda t: sum(t.people_status.values()) == 0)
    # saboteur = Agents.SaboteurAgent('1', "Saboteur")
    # saboteur.set_goal_state(lambda t: False)
    # stupid = Agents.InformedSearchAgent('1', 'Stupid', Agents.InformedSearchAgent.stupid_greedy_heuristic, Fringes.PriorityQueue())
    stupid = Agents.InformedSearchAgent('0', 'Heuristic', Agents.InformedSearchAgent.A_star_func,
                                        Fringes.PriorityQueue())

    stupid.set_goal_state(lambda t: sum(t.people_status.values()) == 0)
    s = Simulator(agents=[stupid], path="env2.json")
    s.display()
    s.start()


if __name__ == '__main__':
    main()
