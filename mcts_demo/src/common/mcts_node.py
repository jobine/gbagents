from __future__ import annotations

import math
from common.game_state import GameState


class MCTSNode:
    __slots__ = ('state', 'parent', 'action_from_parent', 'children', 'N', 'W', 'untried_actions', 'player_to_move')

    def __init__(self, state: GameState, parent: MCTSNode | None=None, action_from_parent: int | None=None):
        self.state = state
        self.parent = parent
        self.action_from_parent = action_from_parent
        self.children: list[MCTSNode] = []
        self.N = 0  # Visit count
        self.W = 0.0  # Total value
        self.untried_actions = state.legal_actions()
        self.player_to_move = state.current_player()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0
    
    def best_child(self, c: float=1.4) -> MCTSNode:
        # UTC score = Q/N + c * sqrt(ln(N_parent) / N)
        assert self.children, "No children to select from"

        ln_parent_N = math.log(self.N)

        def utc(child: MCTSNode) -> float:
            Q = child.W
            N = child.N + 1e-9  # Prevent division by zero
            return (Q / N) + c * math.sqrt(ln_parent_N / N)
        
        return max(self.children, key=utc)
    
    def expand(self) -> MCTSNode:
        action = self.untried_actions.pop()
        next_state = self.state.next_state(action)
        child_node = MCTSNode(state=next_state, parent=self, action_from_parent=action)
        self.children.append(child_node)
        return child_node
    
    def backup(self, value_from_current_player: float):
        '''Backpropagate value up the tree.
        value_from_current_player is the rollout value from the perspective of self.player_to_move.
        As we go up one level, the player perspective flips (zero-sum, two-player).'''
        node = self
        value = value_from_current_player

        while node is not None:
            node.N += 1
            node.W += value
            value = -value  # Switch perspective for zero-sum game
            node = node.parent
