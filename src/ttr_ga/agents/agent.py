import random


class Agent:
    """Abstract base class for all AI agents"""
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        
    def choose_action(self, game_state):
        # Should be implemented by specific agent types
        raise NotImplementedError
        
    def observe_outcome(self, action, new_state, reward):
        # Called after action is taken to update agent's knowledge
        pass
    
class RandomAgent(Agent):
    """A simple agent that chooses actions randomly"""
    def choose_action(self, game_state):
        valid_actions = game_state.get_valid_actions()
        return random.choice(valid_actions)