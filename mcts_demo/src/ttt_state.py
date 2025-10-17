# ------------------
# Tic-Tac-Toe State
# ------------------

from dataclasses import dataclass

from common.game_state import GameState


@dataclass(frozen=True)
class TTTState(GameState):
    board: tuple[int, ...]  # 0 = empty, 1 = X, -1 = O
    current_player_index: int  # 1 or -1

    def current_player(self) -> int:
        return self.current_player_index

    def legal_actions(self) -> list[int]:
        return [i for i, v in enumerate(self.board) if v == 0]

    def next_state(self, action: int) -> 'TTTState':
        new_board = list(self.board)
        new_board[action] = self.current_player_index
    
        return TTTState(board=tuple(new_board), current_player_index=-self.current_player_index)
    
        # if self.board[action] != 0:
        #     raise ValueError("Invalid action")

        # new_board = list(self.board)
        # new_board[action] = 1 if self.current_player_index == 1 else -1
        # return TTTState(board=tuple(new_board), current_player_index=-self.current_player_index)

    def is_terminal(self) -> bool:
        return self._check_winner() is not None or all(v != 0 for v in self.board)

    def reward(self, player: int) -> float:
        winner = self._check_winner()
        if winner is None:
            return 0.0  # Draw or ongoing
        
        return 1.0 if winner == player else -1.0
        # return 1.0 if (winner == 1 and player == 0) or (winner == -1 and player == 1) else -1.0

    def _check_winner(self) -> int | None:
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
            (0, 4, 8), (2, 4, 6)              # diagonals
        ]
        for a, b, c in lines:
            # if self.board[a] == self.board[b] == self.board[c] != 0:
            #     return self.board[a]
            s = self.board[a] + self.board[b] + self.board[c]
            if s == 3:
                return 1
            elif s == -3:
                return -1
        return None
    
    def __str__(self) -> str:
        symbols = {1:"X", -1:"O", 0:" "}
        rows = ["|".join(symbols[self.board[i * 3 + j]] for j in range(3)) for i in range(3)]
        return "\n-+-+-\n".join(rows)
