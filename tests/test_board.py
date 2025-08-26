import pytest

from ttr_ga.player import Player
from ttr_ga.board import Board


class TestBoard:
    @pytest.fixture
    def board(self):
        """Create a fresh board for each test"""
        return Board()
    
    @pytest.fixture
    def players(self):
        """Create test players with predefined hands"""
        player1 = Player("Test Player 1")
        player2 = Player("Test Player 2")
        
        # Add some cards to the players' hands for testing
        player1.hand = ['red', 'red', 'red', 'blue', 'blue', 'green', 'wild', 'wild']
        player2.hand = ['yellow', 'yellow', 'black', 'black', 'wild', 'wild']
        
        return [player1, player2]
    
    def test_claim_route_success(self, board, players):
        """Test that a player can claim an unclaimed route"""
        player1 = players[0]
        
        # Pick a route that requires 2 red cards
        city1, city2 = "New York", "Boston"
        
        # Set the route length and color in the board's graph
        board.graph.add_edge(city1, city2, color='red', length=2)
        
        # Claim the route
        result = board.claim_route(player1, city1, city2)
        
        assert result is True
        # Check that cards were removed from player's hand
        assert player1.hand.count('red') == 1  # Started with 3, used 2
        # Check that the route is marked as claimed
        assert 'claimed' in board.graph[city1][city2][0]
        assert board.graph[city1][city2][0]['claimed'] == player1.name
    
    def test_claim_route_double_route_2_players(self, board, players):
        """Test that only one of the double routes can be claimed in a 2-player game"""
        player1, player2 = players
        city1, city2 = "New York", "Washington"  # Adjust to actual cities
        
        # Add two parallel routes
        board.graph.add_edge(city1, city2, key=0, color='red', length=2)
        board.graph.add_edge(city1, city2, key=1, color='blue', length=2)
        
        # First player claims one route
        result1 = board.claim_route(player1, city1, city2, player_count=2)
        assert result1 is True
        
        # Second player attempts to claim the other route
        result2 = board.claim_route(player2, city1, city2, player_count=2)
        assert result2 is False  # Should fail in 2-player game
    
    @pytest.mark.parametrize("player_count,expected_result", [
        (2, False),  # In 2-player game, second claim should fail
        (4, True)    # In 4-player game, second claim should succeed
    ])
    def test_claim_route_double_route_player_count(self, board, players, player_count, expected_result):
        """Test double route claiming with different player counts"""
        player1, player2 = players
        city1, city2 = "New York", "Washington"
        
        # Add two parallel routes
        board.graph.add_edge(city1, city2, key=0, color='red', length=2)
        board.graph.add_edge(city1, city2, key=1, color='blue', length=2)
        
        # First player claims one route
        board.claim_route(player1, city1, city2, player_count=player_count)
        
        # Second player attempts to claim the other route
        result = board.claim_route(player2, city1, city2, player_count=player_count)
        assert result is expected_result
    
    def test_claim_route_player_cant_claim_both_routes(self, board, players):
        """Test that a player cannot claim both routes of a double route"""
        player1 = players[0]
        city1, city2 = "New York", "Washington"
        
        # Add two parallel routes
        board.graph.add_edge(city1, city2, key=0, color='red', length=2)
        board.graph.add_edge(city1, city2, key=1, color='blue', length=2)
        
        # Player claims first route
        result1 = board.claim_route(player1, city1, city2, player_count=4)
        assert result1 is True
        
        # Same player attempts to claim second route
        result2 = board.claim_route(player1, city1, city2, player_count=4)
        assert result2 is False  # Should fail regardless of player count

    def test_claim_route_triggers_final_round(self, board, players):
        """Claiming a route with few trains left should trigger final round"""
        player1 = players[0]
        player1.trains = 2

        city1, city2 = "Chicago", "Detroit"
        board.graph.add_edge(city1, city2, color='blue', length=1)

        result = board.claim_route(player1, city1, city2)

        assert result == (True, "final_round")
