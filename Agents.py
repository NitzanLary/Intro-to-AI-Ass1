from abc import ABC, abstractmethod

from World import World


class Agent(ABC):
    def __init__(self, location, name: str):
        self.score, self.location, self.actions, self.evacuated, self.time = 0, location, 0, 0, 0
        self.name = name
        self.terminated = 0

    @abstractmethod
    def act(self, world: World):
        pass

    def __str__(self):
        return f"name: {self.name} " \
               f"score: {self.score} " \
               f"location: {self.location} " \
               f"time: {self.time} " \
               f"evacuated: {self.evacuated} " \
               f"actions: {self.actions}"


class HumanAgent(Agent):

    def act(self, world: World):
        move = input("Insert next vertex to move, 'Enter' for no-op ")

        if int(move) < 0:
            self.terminated = 1
            return
        return move


class SearchAgent(Agent):
    def __init__(self, location, name: str):
        Agent.__init__(self, location, name)
        self.fringe = []

    def act(self, world: World):
        pass
