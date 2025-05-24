from ttr_ga.common import CITIES, ROUTES, COLORS
from ttr_ga.board import Board
from ttr_ga.player import HumanPlayer, Player, Deck
import networkx as nx
import random

from ttr_ga.utils.state import GameState

def setup_game(players, deck):
    for player in players:
        player.draw_initial_cards(deck)
        player.draw_ticket_cards(deck)

    print("Initial face-up train cards:", deck.face_up_cards)
    

def game_loop(players, board, deck):
    """Main game loop using GameState for tracking"""
    # Initialize game state
    game_state = GameState(board, players, 0, deck)
    turn_number = 1
    
    while not game_state.game_over:
        current_player_idx = game_state.current_player_idx
        current_player = players[current_player_idx]
        
        print(f"\nTurn {turn_number}: {current_player.name}'s turn:")
                
        # Get action from player (human or AI)
        action = current_player.choose_action(game_state)
        
        # Execute the action
        result = execute_action(current_player, action, game_state)
        
        # Check for final round trigger
        if isinstance(result, tuple) and result[1] == "final_round":
            game_state.final_round = True
            game_state.final_round_trigger_player = current_player_idx
        
        # Display game state
        print(current_player.name, "hand:", current_player.hand)
        print("Face-up cards:", deck.face_up_cards)
        
        # Check for game end conditions
        if current_player.trains <= 2:
            print(f"{current_player.name} has used all trains! Game entering final round.")
            game_state.final_round = True
            game_state.final_round_trigger_player = current_player_idx
        
        # Final round logic - game ends when we get back to the player who triggered it
        if game_state.final_round and game_state.current_player_idx == game_state.final_round_trigger_player:
            game_state.game_over = True
        
        # Move to next player
        game_state.current_player_idx = (current_player_idx + 1) % len(players)

        # Increment turn number if we've looped through all players
        if game_state.current_player_idx == 0:
            turn_number += 1
    
    print("\nGame over! Calculating final scores...")
    
    # Calculate final scores
    for player in players:
        # Get points for completed tickets
        ticket_score = check_tickets(player, board)
        print(f"{player.name} completed tickets: {ticket_score} points")
        
        # Get points for longest path
        longest_path_score = longest_continuous_path(player, board)
        print(f"{player.name} longest path: {longest_path_score} points")
        
        # Update final score
        player.score += ticket_score + longest_path_score
        print(f"{player.name}'s final score: {player.score}")
    
    # Determine winner
    winner = max(players, key=lambda p: p.score)
    print(f"\n{winner.name} wins with {winner.score} points!")


def check_tickets(player, board):
    score = 0
    for (city1, city2, points) in player.tickets:
        if nx.has_path(board.graph, city1, city2):
            score += points
        else:
            score -= points
    return score

# TODO: resolve placeholder for longest cont path
def longest_continuous_path(player, board):
    """Calculate the longest continuous path for a player"""
    # Create a subgraph containing only this player's claimed routes
    player_graph = nx.Graph()
    
    for u, v, data in board.graph.edges(data=True):
        if 'claimed' in data and data['claimed'] == player.name:
            player_graph.add_edge(u, v)
    
    if not player_graph.nodes():
        return 0  # No routes claimed
    
    # Find all simple paths between all pairs of nodes
    max_length = 0
    
    # This is a brute-force approach and could be optimized
    for source in player_graph.nodes():
        for target in player_graph.nodes():
            if source != target:
                try:
                    paths = list(nx.all_simple_paths(player_graph, source, target))
                    for path in paths:
                        path_length = len(path) - 1  # Number of edges in path
                        max_length = max(max_length, path_length)
                except nx.NetworkXNoPath:
                    continue
    
    # Calculate bonus points (10 for the longest path in the game)
    # This is a placeholder - in a real game, you'd compare across all players
    return max_length + (10 if max_length > 0 else 0)

def execute_action(player, action, game_state):
    """Execute a player's action and update the game state"""
    action_type = action["action_type"]
    
    if action_type == "draw_train_cards":
        if action["method"] == "blind":
            # Draw blind cards
            for _ in range(action["count"]):
                if game_state.deck.train_cards:
                    player.hand.append(game_state.deck.draw_train_card())
        
        elif action["method"] == "mixed":
            # First draw blind card
            if game_state.deck.train_cards:
                player.hand.append(game_state.deck.draw_train_card())
            
            # Then handle face-up card selection
            print("Choose a face-up card (0-4):", game_state.deck.face_up_cards)
            face_up_choice = int(input("Enter your choice: "))
            
            if 0 <= face_up_choice < len(game_state.deck.face_up_cards):
                player.hand.append(game_state.deck.face_up_cards[face_up_choice])
                game_state.deck.replace_face_up_card(face_up_choice)
        
        elif action["method"] == "face_up":
            print("Choose a face-up card (0-4):", game_state.deck.face_up_cards)
            face_up_choice = int(input("Enter your choice: "))
            
            if 0 <= face_up_choice < len(game_state.deck.face_up_cards):
                card = game_state.deck.face_up_cards[face_up_choice]
                player.hand.append(card)
                game_state.deck.replace_face_up_card(face_up_choice)
                
                # If wild card was drawn, no second card
                if card != "wild" and action.get("count", 0) > 1:
                    print("Choose a second face-up card (0-4):", game_state.deck.face_up_cards)
                    face_up_choice2 = int(input("Enter your choice: "))
                    
                    if 0 <= face_up_choice2 < len(game_state.deck.face_up_cards):
                        player.hand.append(game_state.deck.face_up_cards[face_up_choice2])
                        game_state.deck.replace_face_up_card(face_up_choice2)
    
    elif action_type == "claim_route":
        city1 = action["city1"]
        city2 = action["city2"]
        color = action["color"]
        
        # Get route data
        edge_data = game_state.board.graph.get_edge_data(city1, city2)
        if not edge_data:
            print(f"No route exists between {city1} and {city2}")
            return False
        
        # Find the first unclaimed edge with matching color
        for key, route in edge_data.items():
            # Check if route color matches requested color or if "any" color is allowed
            if (route["color"] == color or route["color"] == "any") and "claimed" not in route:
                length = route["length"]
                
                # Count regular cards and wild cards
                regular_cards = player.hand.count(color)
                wild_cards = player.hand.count("wild")
                
                # Check if player has enough cards (regular + wild)
                if regular_cards + wild_cards >= length:
                    # Use regular cards first, then wild cards as needed
                    cards_to_use = min(regular_cards, length)
                    wilds_to_use = length - cards_to_use
                    
                    # Remove cards from hand
                    for _ in range(cards_to_use):
                        player.hand.remove(color)
                    for _ in range(wilds_to_use):
                        player.hand.remove("wild")
                    
                    # Update player stats
                    player.trains -= length
                    player.score += player.calculate_route_score(length)
                    
                    # Mark route as claimed
                    route["claimed"] = player.name
                    print(f"{player.name} claimed route from {city1} to {city2}")
                    return True
                else:
                    print(f"Not enough {color} cards and wild cards to claim this route")
                    return False
        
        # If we get here, no matching unclaimed route was found
        print(f"Cannot claim route from {city1} to {city2} with {color} cards")
        return False
    
    elif action_type == "draw_tickets":
        if len(game_state.deck.ticket_cards) > 0:
            # Let the player class handle the ticket drawing
            return_tickets = player.draw_ticket_cards(game_state.deck)
            
            # Return unwanted tickets to the deck
            game_state.deck.ticket_cards.extend(return_tickets)
            random.shuffle(game_state.deck.ticket_cards)
        else:
            print("No ticket cards remaining")

