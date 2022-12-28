import math
from abc import abstractmethod
from collections.abc import Callable
from itertools import chain
from typing import Any

from World import World, StateNode


class Agent:
    def __init__(self, initial_location, name: int):
        # name will indicate the agent's index
        self.name = name
        self.location = initial_location
        self.score, self.evacuated = 0, 0
        self.world, self.eval, self.terminal_test, self.cutoff_test = None, None, None, None

    @abstractmethod
    def act(self):
        pass

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

    def reconstruct_path(self, node: StateNode):
        cur_node = node
        while node.parent:
            cur_node = node
            node = node.parent
        return cur_node

    def __str__(self):
        return f"name: {self.name} " \
               f"score: {self.score} " \
               f"location: {self.location} " \
               f"evacuated: {self.evacuated} "


class MiniMaxAgent(Agent):

    def act(self):
        action = self.alpha_beta_search()
        self.handle_move(action)
        return action

    def alpha_beta_search(self):
        loc1, loc2 = self.world.get_agents_locations(self.name)
        state = StateNode(loc1, loc2, self.world)
        v, final_action = self.max_value(state, alpha=-float("inf"), beta=float("inf"), depth=1, score=0)
        action = self.reconstruct_path(final_action)
        # returning only next move instead of State
        return action.location1

    def max_value(self, state: StateNode, alpha, beta, depth, score) -> (float, Any):
        # a leaf, return the actual score
        if self.terminal_test(state):
            return score + 1 / depth, state
        # max depth reached, return the heuristic static evaluation of state
        if self.cutoff_test(depth):
            return score + 1 / depth, state
        v, action = -float("inf"), state
        # max between all possible action, including no-op (which is basically staying in place)
        for child in chain(self.world.get_neighbors(state.location1), [state.location1]):
            current_score = score + self.world.get_people(child)
            value = self.min_value(StateNode(child, state.location2, self.world, state), alpha, beta, depth + 1,
                                   current_score)
            v, action = max((v, action), value)
            if v >= beta:
                return v, state
            alpha = max(v, alpha)
        return v, action

    def min_value(self, state: StateNode, alpha, beta, depth, score) -> (float, Any):
        if self.terminal_test(state):
            return score + 1 / depth, state
        if self.cutoff_test(depth):
            return score + 1 / depth, state
        v, action = float("inf"), state
        for child in chain(self.world.get_neighbors(state.location2), [state.location2]):
            current_score = score - self.world.get_people(child)
            value = self.max_value(StateNode(state.location1, child, self.world, state), alpha, beta, depth + 1,
                                   current_score)
            v, action = min((v, action), value)
            if v <= alpha:
                return v, action
            beta = min(v, beta)
        return v, action

    @staticmethod
    def MST_heuristic(state: StateNode, world: World):
        if state.location1 in state.broken_nodes_status:
            return math.inf
        v_with_people = [v for v, n_people in state.people_status.items() if n_people > 0]
        return world.get_MST_size(around_nodes=v_with_people + [state.location1],
                                  without_nodes=state.broken_nodes_status)


class SemiCooperativeAgent(Agent):

    def act(self):
        loc1, loc2 = self.world.get_agents_locations(self.name)
        state = StateNode(loc1, loc2, self.world)
        v, action = self.max_my_value(state, depth=1, my_score=0, other_score=0)
        action = self.reconstruct_path(action)
        self.handle_move(action.location1)
        return action.location1

    def max_my_value(self, state: StateNode, depth, my_score, other_score) -> (float, Any):
        # a leaf, return the actual score
        if self.terminal_test(state):
            return [my_score + 1 / depth, other_score + 1 / depth], state
        # max depth reached, return the heuristic static evaluation of state
        if self.cutoff_test(depth):
            return [my_score + 1 / depth, other_score + 1 / depth], state
        v, action = [-float("inf"), -float("inf")], state
        # max between all possible action, including no-op (which is basically staying in place)
        for child in chain(self.world.get_neighbors(state.location1), [state.location1]):
            my_score += self.world.get_people(child)
            value = self.max_other_value(StateNode(child, state.location2, self.world, state), depth + 1,
                                         my_score, other_score)
            [score1, score2], state = value
            v, action = max((v, action), ([score1, score2], state))
        return v, action

    def max_other_value(self, state: StateNode, depth, my_score, other_score) -> (float, Any):
        # a leaf, return the actual score
        if self.terminal_test(state):
            return [my_score + 1 / depth, other_score + 1 / depth], state
        # max depth reached, return the heuristic static evaluation of state
        if self.cutoff_test(depth):
            return [my_score + 1 / depth, other_score + 1 / depth], state
        v, action = [-float("inf"), -float("inf")], state
        # max between all possible action, including no-op (which is basically staying in place)
        for child in chain(self.world.get_neighbors(state.location2), [state.location2]):
            other_score += self.world.get_people(child)
            value = self.max_my_value(StateNode(state.location1, child, self.world, state), depth + 1,
                                      my_score, other_score)
            [score1, score2], cur_state = value
            if score2 > v[1]:
                v, action = [score1, score2], cur_state
        return v, action


class FullyCooperativeAgent(Agent):
    def act(self):
        loc1, loc2 = self.world.get_agents_locations(self.name)
        state = StateNode(loc1, loc2, self.world)
        v, action = self.max_my_value(state, depth=1, score=0)
        action = self.reconstruct_path(action)
        self.handle_move(action.location1)
        return action.location1

    def max_my_value(self, state: StateNode, depth, score) -> (float, Any):
        # a leaf, return the actual score
        if self.terminal_test(state):
            return score + 1 / depth, state
        # max depth reached, return the heuristic static evaluation of state
        if self.cutoff_test(depth):
            return score + 1 / depth, state
        v, action = 0, state
        # max between all possible action, including no-op (which is basically staying in place)
        for child in chain(self.world.get_neighbors(state.location1), [state.location1]):
            score += self.world.get_people(child)
            value = self.max_other_value(StateNode(child, state.location2, self.world, state), depth + 1, score)
            v, action = max((v, action), value)
        return v, action

    def max_other_value(self, state: StateNode, depth, score) -> (float, Any):
        # a leaf, return the actual score
        if self.terminal_test(state):
            return score + 1 / depth, state
        # max depth reached, return the heuristic static evaluation of state
        if self.cutoff_test(depth):
            return score + 1 / depth, state
        v, action = 0, state
        # max between all possible action, including no-op (which is basically staying in place)
        for child in chain(self.world.get_neighbors(state.location2), [state.location2]):
            score += self.world.get_people(child)
            value = self.max_my_value(StateNode(state.location1, child, self.world, state), depth + 1, score)
            v, action = max((v, action), value)
        return v, action


