import math
from collections.abc import Callable
from itertools import chain
from typing import Any

from World import World, StateNode

epsilon = 0.0001


class Agent:
    def __init__(self, initial_location, name: str):
        self.name = name
        self.location = initial_location
        self.score, self.evacuated = 0, 0
        self.world, self.eval, self.terminal_test, self.cutoff_test = None, None, None, None

    def set_world(self, world: World):
        self.world = world

    def set_terminal_test(self, terminal_state: Callable[[StateNode], bool]):
        self.terminal_test = terminal_state

    def set_cutoff_test(self, max_depth):
        self.cutoff_test = lambda d: d > max_depth

    def set_eval_function(self, eval_func: Callable[[StateNode], float]):
        self.eval = eval_func

    def handle_move(self, dst):
        if dst == self.location:
            return
        p = self.world.get_people(dst)
        self.evacuated += p
        self.score += p
        self.location = dst
        self.world.clear_people(dst)

    def act(self):
        action = self.alpha_beta__search()
        self.handle_move(action)
        return action

    def alpha_beta__search(self):
        state = StateNode(self.location, self.world, None)
        v, final_action = self.max_value(state, -float("inf"), float("inf"), depth=1, score=0)
        action = self.reconstruct_path(final_action)
        # returning only next move instead of State
        return action.location

    def max_value(self, state: StateNode, alpha, beta, depth, score) -> (float, Any):
        # a leaf, return the actual score
        if self.terminal_test(state):
            return score, state
        # max depth reached, return the heuristic static evaluation of state
        if self.cutoff_test(depth):
            return self.eval(state, self.world) + score, state
        v, action = -float("inf"), state
        # max between all possible action, including no-op (which is basically staying in place)
        for child in chain(self.world.get_neighbors(state.location), [state.location]):
            current_score = score + self.world.get_people(child) - epsilon
            value = self.min_value(StateNode(child, self.world, state), alpha, beta, depth + 1, current_score)
            v, action = max((v, action), value)
            if v >= beta:
                return v, state
            alpha = max(v, alpha)
        return v, action

    def min_value(self, state: StateNode, alpha, beta, depth, score) -> (float, Any):
        if self.terminal_test(state):
            return score, state
        if self.cutoff_test(depth):
            return self.eval(state, self.world) + score, state
        v, action = float("inf"), state
        for child in chain(self.world.get_neighbors(state.location), [state.location]):
            current_score = score - self.world.get_people(child) - epsilon
            value = self.max_value(StateNode(child, self.world, state), alpha, beta, depth + 1, current_score)
            v, action = min((v, action), value)
            if v <= alpha:
                return v, action
            beta = min(v, beta)
        return v, action

    def reconstruct_path(self, node: StateNode):
        p = []
        while node.parent:
            p.append(node)
            node = node.parent
        # print(list(a.location for a in p[-1::-1]))
        return p.pop()

    @staticmethod
    def MST_heuristic(state: StateNode, world: World):
        if state.location in state.broken_nodes_status:
            return math.inf
        v_with_people = [v for v, n_people in state.people_status.items() if n_people > 0]
        return world.get_MST_size(around_nodes=v_with_people + [state.location],
                                  without_nodes=state.broken_nodes_status)

    def __str__(self):
        return f"name: {self.name} " \
               f"score: {self.score} " \
               f"location: {self.location} " \
               f"evacuated: {self.evacuated} "
