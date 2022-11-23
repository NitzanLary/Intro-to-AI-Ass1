from Graph import Graph
from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, location, name: str):
        self.score, self.location, self.actions, self.evacuated, self.time = 0, location, 0, 0, 0
        self.name = name
        self.terminated = 0

    @abstractmethod
    def act(self, graph: Graph):
        pass

    def __str__(self):
        return f"name: {self.name} " \
               f"score: {self.score} " \
               f"location: {self.location} " \
               f"time: {self.time} " \
               f"evacuated: {self.evacuated} " \
               f"actions: {self.actions}"


class HumanAgent(Agent):

    def act(self, graph: Graph):
        move = input("Insert next vertex to move, 'Enter' for no-op ")
        if int(move) < 0:
            self.terminated = 1
            return
        return move


# class StupidGreedy(Agent):
#     def __init__(self, location, name: str):
#         Agent.__init__(self, location, name)
#         self.
#
#     def act(self, graph: Graph):
