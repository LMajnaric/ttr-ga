from importlib import import_module
import pytest
from ttr_ga.player import Deck

class TestDeck:
    @pytest.fixture
    def deck_with_specific_cards(self):
        """Set up a test deck with specific cards"""
        deck = Deck()
        
        # Ensure the deck has some specific cards for testing
        deck.train_cards = ['red', 'blue', 'green', 'yellow', 'black', 'wild', 'wild', 'wild', 'orange', 'white']
        deck.face_up_cards = ['red', 'blue', 'green', 'yellow', 'black']
        
        return deck
    
    def test_draw_train_card(self, deck_with_specific_cards):
        """Test drawing a train card from the deck"""
        deck = deck_with_specific_cards
        initial_count = len(deck.train_cards)
        card = deck.draw_train_card()
        
        assert card == 'white'  # Should be the first card
        assert len(deck.train_cards) == initial_count - 1
    
    def test_replace_face_up_card(self, deck_with_specific_cards):
        """Test replacing a face-up card"""
        deck = deck_with_specific_cards
        deck.replace_face_up_card(0)
        
        # The 0th card should now be the first card from the train_cards
        assert deck.face_up_cards[0] == 'white'
        assert len(deck.face_up_cards) == 5  # Should still have 5 face-up cards
    
    def test_three_wilds_replacement(self, deck_with_specific_cards):
        """Test that 3+ wilds in face-up cards triggers replacement"""
        deck = deck_with_specific_cards
        # Set up 3 wilds in the face-up cards
        deck.face_up_cards = ['wild', 'wild', 'wild', 'red', 'blue']
        
        # Add method to check and replace wilds
        deck.check_and_replace_wilds()
        
        # Count wilds after replacement
        wild_count = deck.face_up_cards.count('wild')
        
        assert wild_count < 3  # Should have fewer than 3 wilds now
        assert len(deck.face_up_cards) == 5  # Should still have 5 face-up cards
    
    @pytest.mark.parametrize("face_up_cards,expected_replacement", [
        (['wild', 'wild', 'red', 'blue', 'green'], False),  # 2 wilds - no replacement
        (['wild', 'wild', 'wild', 'blue', 'green'], True),  # 3 wilds - replacement
        (['wild', 'wild', 'wild', 'wild', 'green'], True),  # 4 wilds - replacement
    ])
    def test_wild_card_replacement_scenarios(self, monkeypatch, face_up_cards, expected_replacement):
        """Test various scenarios for wild card replacement"""
        deck = Deck()
        deck.face_up_cards = face_up_cards.copy()
        
        # Mock the shuffling and drawing to make test deterministic
        def mock_shuffle(cards):
            pass  # Do nothing when shuffling
            
        replacement_cards = ['red', 'blue', 'green', 'yellow', 'black']
        
        draw_count = 0
        def mock_draw():
            nonlocal draw_count
            card = replacement_cards[draw_count % len(replacement_cards)]
            draw_count += 1
            return card
        
        monkeypatch.setattr(deck, "draw_train_card", mock_draw)
        monkeypatch.setattr(import_module("random"), "shuffle", mock_shuffle)
        
        # Original face-up cards
        original_cards = face_up_cards.copy()
        
        # Check and replace wilds
        deck.check_and_replace_wilds()
        
        # Check if replacement happened
        cards_changed = (deck.face_up_cards != original_cards)
        assert cards_changed == expected_replacement