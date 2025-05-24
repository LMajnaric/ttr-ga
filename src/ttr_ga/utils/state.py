class GameState:
    """Represents the complete state of the game"""
    def __init__(self, board, players, current_player_idx, deck):
        self.board = board
        self.players = players
        self.current_player_idx = current_player_idx
        self.deck = deck
        self.game_over = False
        self.final_round = False
        self.final_round_trigger_player = None
        
    def get_current_player(self):
        """Get the current player"""
        return self.players[self.current_player_idx]
    
    def get_valid_actions(self):
        """Return all valid actions for the current player"""
        # This would be used by AI agents to know what moves are legal
        valid_actions = []
        
        # Always valid to draw train cards or tickets
        valid_actions.append({"action_type": "draw_train_cards"})
        valid_actions.append({"action_type": "draw_tickets"})
        
        # Check for claimable routes
        player = self.get_current_player()
        
        for u, v, data in self.board.graph.edges(data=True):
            if 'claimed' not in data:  # Route not claimed
                color = data['color']
                length = data['length']
                
                # Check if player has enough cards
                if player.hand.count(color) >= length:
                    valid_actions.append({
                        "action_type": "claim_route",
                        "city1": u,
                        "city2": v,
                        "color": color
                    })
        
        return valid_actions
    
    def clone(self):
        """Create a deep copy of the game state (useful for AI simulations)"""
        # This is a placeholder - a real implementation would need deep copies
        new_state = GameState(self.board, self.players, self.current_player_idx, self.deck)
        new_state.game_over = self.game_over
        new_state.final_round = self.final_round
        new_state.final_round_trigger_player = self.final_round_trigger_player
        return new_state
    
    # TODO: apply valid action
    def apply_action(self, action):
        # Apply action and return new state
        pass