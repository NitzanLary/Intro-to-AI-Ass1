from Graph import Graph
import Agents

import json

from Simulator import Simulator


def main():
    s = Simulator(agents=[Agents.HumanAgent('1', "Human")], path="env.json")
    s.display()
    s.start()


if __name__ == '__main__':
    main()
