import math
import random
from typing import Callable
from common.game_state import GameState
from common.mcts_node import MCTSNode


class MCTS:
    def __init__(self, c_puct: float=math.sqrt(2), rollout_policy: Callable | None=None):
        self.c = c_puct
        # Default rollout policy: random legal action
        self.rollout_policy = rollout_policy or (lambda x: random.choice(x.legal_actions()))

    def search(self, root_state: GameState, n_sim: int = 1000) -> int:
        root_node = MCTSNode(state=root_state)

        for _ in range(n_sim):
            node = root_node

            # Selection
            while not node.state.is_terminal() and node.is_fully_expanded():
                node = node.best_child(self.c)

            # Expansion
            if not node.state.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            # Simulation
            rollout_value = self.rollout(node.state, node.player_to_move)

            # Backpropagation
            node.backup(rollout_value)

        # Choose the action with the highest visit count
        best_child = max(root_node.children, key=lambda n: n.N)
        return best_child.action_from_parent
    
    def rollout(self, state: GameState, player: int) -> float:
        current_state = state

        while not current_state.is_terminal():
            action = self.rollout_policy(current_state)
            current_state = current_state.next_state(action)

        return current_state.reward(player)
