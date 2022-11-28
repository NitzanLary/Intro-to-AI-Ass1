from abc import ABC, abstractmethod
import heapq

from World import StateNode


class Fringe(ABC):

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def push(self, state_node: StateNode):
        pass

    def push_all(self, iterable):
        for elem in iterable:
            self.push(elem)

    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def is_empty(self):
        pass


class PriorityQueue(Fringe):
    def __init__(self):
        self.queue = []

    def initialize(self):
        self.queue = []

    def push(self, state_node):
        return heapq.heappush(self.queue, (state_node.f_value, state_node))

    def pop(self):
        f_value, node = heapq.heappop(self.queue)
        return node

    def is_empty(self):
        return len(self.queue) == 0
