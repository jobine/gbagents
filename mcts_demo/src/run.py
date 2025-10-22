import random
from common.game_state import GameState
from common.mcts import MCTS
from ttt_state import TTTState

def play_game(mcts_iters: int=1000, seed: int=0, opponent: str='random') -> int:
    random.seed(seed)
    state: GameState = TTTState(board=(0, 0, 0, 0, 0, 0, 0, 0, 0), current_player_index=1)
    mcts = MCTS()
    move_num = 1

    while not state.is_terminal():
        if state.current_player() == 1:
            # X uses MCTS
            print("MCTS Player's turn (X):")
            action = mcts.search(root_state=state, n_sim=mcts_iters)
        else:
            # O uses random policy
            print("Random Player's turn (O):")
            if opponent == 'random':
                # action = random_policy(state)
                action = random.choice(state.legal_actions())
            else:
                action = mcts.search(root_state=state, n_sim=mcts_iters)

        state = state.next_state(action)
        print(f'\nMove {move_num} ({"X" if state.current_player() == -1 else "O"} just played @{action}):')
        print(state)
        move_num += 1

    winner = state._check_winner()
    if winner is None:
        print("It's a draw!")
        return 0
    else:
        print(f'Result: Player {"X" if winner == 1 else "O"} wins!')
        return winner


if __name__ == '__main__':
    print('\n=== Demo: MCTS (X) vs Random (O) ===\n')
    _ = play_game(mcts_iters=10, seed=42, opponent='random')

    # print('\n=== Demo: MCTS (X) vs MCTS (O) ===\n')
    # _ = play_game(mcts_iters=800, seed=42, opponent='mcts')
