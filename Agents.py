import math
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from Fringes import Fringe
from World import World, StateNode

SUCCESS = 1
FAILURE = 0


class Agent(ABC):
    def __init__(self, state, name: str):
        self.score, self.state, self.actions, self.evacuated, self.time = 0, state, 0, 0, 0
        self.name = name
        self.goal_state = None
        self.terminated = 0
        self.world = None

    def set_goal_state(self, goal_state: Callable[[StateNode], bool]):
        self.goal_state = goal_state

    def set_world(self, world: World):
        self.world = world

    def handle_move(self, dst):
        w = self.world.get_weight(self.state, dst)
        p = self.world.get_people(dst)
        self.evacuated += p
        self.actions += 1
        self.score += 1000 * p - w
        self.time += w
        self.state = dst
        self.world.clear_people(dst)

    @abstractmethod
    def act(self, world: World):
        pass

    def __str__(self):
        return f"name: {self.name} " \
               f"score: {self.score} " \
               f"state: {self.state} " \
               f"time: {self.time} " \
               f"evacuated: {self.evacuated} " \
               f"actions: {self.actions}"


class HumanAgent(Agent):
    def act(self, world: World):
        if self.goal_state(
                StateNode(self.state, None, world, world.get_people_status(), world.get_broken_vertices_status())):
            print("Woohoo!")
            self.terminated = 1
        while (move := int(input("Insert next vertex to move, 'Enter' for no-op "))) >= 0 and not world.valid_action(
                self.state, str(move)):
            pass
        move = str(move)
        self.handle_move(move)
        return move


class StupidGreedy(Agent):

    def act(self, world: World):
        if self.goal_state(StateNode(self.state, None, self.world, self.world.get_people_status(),
                                     self.world.get_broken_vertices_status())):
            print("Woohoo!")
            self.terminated = 1
            return
        path = self.calculate_path(world)
        if len(path) < 2:
            self.terminated = 1
            return
        next_move = path[1]
        if not world.valid_action(self.state, next_move):
            self.actions += 1
            return
        self.handle_move(next_move)
        return next_move

    def calculate_path(self, world: World):
        current_path = []
        shortest_v_value = math.inf
        broken_vertices = world.get_broken_vertices_status()
        for v, n_people in world.get_people_status().items():
            if n_people > 0 and v not in broken_vertices:
                dist, path = world.get_shortest_path(self.state, v)
                if path and dist < shortest_v_value:
                    shortest_v_value = dist
                    current_path = path
        return current_path


class SaboteurAgent(Agent):
    def act(self, world: World):
        if self.goal_state(StateNode(self.state, None, self.world, self.world.get_people_status(),
                                     self.world.get_broken_vertices_status())):
            print("Woohoo!")
            self.terminated = 1
            return
        path = self.calculate_path(world)
        if len(path) < 2:
            self.terminated = 1
            return
        next_move = path[1]
        if not world.valid_action(self.state, next_move):
            self.actions += 1
            return
        self.time += self.world.get_weight(self.state, next_move)
        self.state = next_move
        return next_move

    def calculate_path(self, world: World):
        current_path = []
        broken_nodes = world.get_broken_vertices_status()
        shortest_v_value = math.inf
        for v in world.get_brittle_vertices():
            if v not in broken_nodes:
                dist, path = world.get_shortest_path(self.state, v)
                if path and dist < shortest_v_value:
                    shortest_v_value = dist
                    current_path = path
        return current_path


class InformedSearchAgent(Agent):
    def __init__(self, state, name: str, f: Callable[[Any, Any, World], float], fringe: Fringe):
        Agent.__init__(self, state, name)
        self.f = f
        self.fringe = fringe
        self.closed = []
        self.sequence = []
        self.calculated = False

    def act(self, world):
        if not self.calculated:
            node, status = self.calculate_path()  # StateNode(self.state, parent=None, world=self.world)
            if not status:
                print("Failure")
                self.terminated = 1
                return
            self.reconstruct_path(node)
            self.calculated = True
        if not self.sequence:
            self.terminated = 1
            return
        next_move = self.sequence.pop()
        self.handle_move(next_move)
        if self.goal_state(
                StateNode(next_move, None, world, world.get_people_status(), world.get_broken_vertices_status())):
            print("Woohoo!")
        return next_move

    def calculate_path(self):
        node = StateNode(self.state, None, self.world, self.world.get_people_status(),
                         self.world.get_broken_vertices_status())
        self.fringe.push(node)
        while not self.fringe.is_empty():
            node = self.fringe.pop()
            if self.goal_state(node):
                return node, SUCCESS
            if node not in self.closed:
                self.closed.append(node)
                self.fringe.push_all(self.expand(node))
                # if self.fringe.get_added_so_far() >
        return node, FAILURE

    def expand(self, node: StateNode) -> iter:
        return map(lambda n: StateNode(n, node, self.world, node.people_status, node.broken_nodes_status,
                                       f_value=self.f(node, n, self.world),
                                       g_value=node.g_value + self.world.get_weight(node.state, n)),
                   self.world.get_neighbors(node.state))

    def reconstruct_path(self, node: StateNode):
        while node.parent:
            self.sequence.append(node.state)
            node = node.parent

    @staticmethod
    def get_path_to_closest_nodes(c, world: World, nodes_list: list):
        shortest_v_value = math.inf
        current_path = []
        for v in nodes_list:
            dist, path = world.get_shortest_path(c, v)
            if path and dist < shortest_v_value:
                shortest_v_value = dist
                current_path = path
        return shortest_v_value, current_path

    @staticmethod
    # construct a shortest path from c to all vertices with people in them
    def MST_heuristic(p: StateNode, c, world: World):
        # get all vertices with people in them
        v_with_people = [v for v, n_people in p.people_status.items() if n_people > 0]
        return world.get_MST_size(around_nodes=v_with_people + [c])
        # current_closest_v = c
        # path_sum = 0  # sum of all edges in the path
        # while v_with_people:
        #     shortest_v_value, current_path = InformedSearchAgent.get_path_to_closest_nodes(current_closest_v,
        #                                                                                    world, v_with_people)
        #     if not current_path:
        #         return math.inf
        #     current_closest_v = current_path[-1]
        #     v_with_people.remove(current_closest_v)
        #     path_sum += shortest_v_value
        # return path_sum

    @staticmethod
    def A_star_func(p: StateNode, c, world: World):
        return InformedSearchAgent.MST_heuristic(p, c, world) + p.g_value + world.get_weight(p.state, c)
