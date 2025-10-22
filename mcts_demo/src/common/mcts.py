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

            # DEBUG:
            # print(f'--- Simulation {_ + 1} ---')
            # print(f'Node: {node}')
            # print(f'State:\n{node.state}\n')
            # end DEBUG

            # Selection
            while not node.state.is_terminal() and node.is_fully_expanded():
                node = node.best_child(self.c)

            # Expansion
            if not node.state.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            # Early exit for terminal state
            if node.state.is_terminal():
                winner = node.state._check_winner()
                if winner == root_state.current_player() and node.parent == root_node:
                    print(f'Early termination: found winning move at iteration {_ + 1}')
                    return node.action_from_parent

            # Simulation
            rollout_value = self.rollout(node.state, node.player_to_move)

            # Backpropagation
            node.backup(rollout_value)

        # Choose the action with the highest visit count
        if not root_node.children:
            raise ValueError("No children found from root node after simulations.")
        
        # # DEBUG:
        # print("Root Node:")
        # print(root_node)
        # # end DEBUG

        best_child = max(root_node.children, key=lambda n: n.N)
        # best_child = root_node.best_child(self.c)
        
        # DEBUG:
        print("=====All Children======")
        for child in root_node.children:
            print(child)
        print("========================")

        # print("Best Child:")
        # print(best_child)

        # print(max(root_node.children, key=lambda n: n.N))
        # end DEBUG

        return best_child.action_from_parent
    
    def rollout(self, state: GameState, player: int) -> float:
        current_state = state

        while not current_state.is_terminal():
            action = self.rollout_policy(current_state)
            current_state = current_state.next_state(action)

        return current_state.reward(player)
