import pytest
from ttr_ga.board import Board
from ttr_ga.player import Player
from ttr_ga.game import check_tickets, longest_continuous_path 



class TestScoring:
    @pytest.fixture
    def board_with_routes(self):
        """Set up a board with claimed routes for testing"""
        board = Board()
        player_name = "Test Player"
        
        # Create a simple network: A-B-C-D and B-E
        board.graph.add_edge("A", "B", color='red', length=2, claimed=player_name)
        board.graph.add_edge("B", "C", color='blue', length=3, claimed=player_name)
        board.graph.add_edge("C", "D", color='green', length=1, claimed=player_name)
        board.graph.add_edge("B", "E", color='yellow', length=2, claimed=player_name)
        
        # Add a separate claimed route F-G
        board.graph.add_edge("F", "G", color='black', length=4, claimed=player_name)
        
        return board
    
    @pytest.fixture
    def player(self):
        """Create a test player"""
        return Player("Test Player")
    
    def test_check_tickets_completed(self, board_with_routes, player):
        """Test that completed tickets are scored correctly"""
        # Add tickets that are completed
        player.tickets = [("A", "D", 10), ("A", "E", 5)]
        
        score = check_tickets(player, board_with_routes)
        
        assert score == 15  # 10 + 5 points for completed tickets
    
    def test_check_tickets_incomplete(self, board_with_routes, player):
        """Test that incomplete tickets are penalized correctly"""
        # Add a mix of completed and incomplete tickets
        player.tickets = [("A", "D", 10), ("A", "G", 15)]
        
        score = check_tickets(player, board_with_routes)
        
        assert score == 10 - 15  # 10 for completed, -15 for incomplete
    
    @pytest.mark.parametrize("tickets,expected_score", [
        ([("A", "D", 10), ("A", "E", 5)], 15),  # All completed
        ([("A", "D", 10), ("F", "G", 15)], 10 + 15),  # All completed different components
        ([("A", "D", 10), ("A", "F", 15)], 10 - 15),  # One incomplete
        ([("F", "G", 8)], 8),  # Single completed
        # Remove the nonexistent cities test or add these cities to the graph
    ])
    def test_check_tickets_scenarios(self, board_with_routes, player, tickets, expected_score):
        """Test various ticket checking scenarios"""
        player.tickets = tickets
        score = check_tickets(player, board_with_routes)
        assert score == expected_score
    
    def test_longest_continuous_path(self, board_with_routes, player):
        """Test longest continuous path calculation"""
        score = longest_continuous_path(player, board_with_routes)
        
        # The longest path is A-B-C-D with length 2+3+1 = 6
        # This should give a score based on the game's scoring table
        expected_score = 13 
        assert score == expected_score