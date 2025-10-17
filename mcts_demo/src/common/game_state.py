class GameState:
    '''Abstract interface for a turn-based perfect-information game.'''
    def current_player(self) -> int:
        '''Returns the index of the current player to move.'''
        raise NotImplementedError
    
    def legal_actions(self) -> list[int]:
        '''Returns a list of legal actions for the current player.'''
        raise NotImplementedError
    
    def next_state(self, action: int) -> 'GameState':
        '''Returns the next game state after the current player takes the given action.'''
        raise NotImplementedError
    
    def is_terminal(self) -> bool:
        '''Returns True if the game is over, False otherwise.'''
        raise NotImplementedError
    
    def reward(self, player: int) -> float:
        '''Returns the reward for the given player at the end of the game.'''
        raise NotImplementedError
