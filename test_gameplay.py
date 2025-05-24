# test_gameplay.py
"""Interactive test for Ticket to Ride gameplay"""

import os
from ttr_ga.board import Board
from ttr_ga.player import HumanPlayer, Deck
from ttr_ga.game import game_loop, GameState, execute_action, check_tickets, longest_continuous_path

def clear_screen():
    """Clear the console screen"""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Mac and Linux
    else:
        os.system('clear')

def display_player_info(player, deck):
    """Display a player's hand, tickets, and other information"""
    print(f"\n{player.name}'s Information:")
    print(f"Trains remaining: {player.trains}")
    print(f"Current score: {player.score}")
    
    print("\nYour train cards:")
    # Group cards by color for easier reading
    card_counts = {}
    for card in player.hand:
        card_counts[card] = card_counts.get(card, 0) + 1
    
    for color, count in card_counts.items():
        print(f"  {color}: {count}")
    
    print("\nYour tickets:")
    for i, ticket in enumerate(player.tickets):
        city1, city2, points = ticket
        print(f"  {i+1}. {city1} to {city2} ({points} points)")
    
    print("\nFace-up cards:")
    for i, card in enumerate(deck.face_up_cards):
        print(f"  {i}. {card}")
    print(f"  Train deck: {len(deck.train_cards)} cards remaining")
    print(f"  Ticket deck: {len(deck.ticket_cards)} cards remaining")

def display_board_status(board):
    """Display a simplified view of the board status"""
    print("\nClaimed routes:")
    claimed_found = False
    for city1, city2, data in board.graph.edges(data=True):
        for key in data:
            route = data[key]
            if isinstance(route, dict) and 'claimed' in route:
                print(f"  {city1} - {city2}: claimed by {route['claimed']}")
                claimed_found = True
    
    if not claimed_found:
        print("  No routes have been claimed yet.")

def test_interactive_gameplay():
    """Test a game with human players interactively"""
    clear_screen()
    print("=== Ticket To Ride Interactive Gameplay Test ===")
    print("This will start a test game with 2-5 human players.")
    
    # Setup
    board = Board.create_standard_board()
    deck = Deck()
    
    # Shuffle decks
    deck.shuffle_train_cards()
    deck.shuffle_ticket_cards()
    
    # Create players
    num_players = 0
    while num_players < 2 or num_players > 5:
        try:
            num_players = int(input("\nEnter number of players (2-5): "))
            if num_players < 2 or num_players > 5:
                print("Please enter a number between 2 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        players.append(HumanPlayer(name))
    
    # Deal initial cards
    for player in players:
        clear_screen()
        print(f"\n{player.name}'s initial setup")
        print("Other players look away from the screen!")
        input("Press Enter when ready...")
        
        # Deal initial train cards
        player.hand = [deck.draw_train_card() for _ in range(4)]
        
        # Draw initial tickets
        tickets = [deck.draw_ticket_card() for _ in range(3)]
        print(f"\n{player.name}, you received these tickets:")
        for i, ticket in enumerate(tickets):
            city1, city2, points = ticket
            print(f"{i}: {city1} to {city2} ({points} points)")
        
        keep_indices = input("\nEnter indices to keep (e.g., 0 1 2): ").split()
        keep_indices = [int(idx) for idx in keep_indices if idx.isdigit() and 0 <= int(idx) < len(tickets)]
        
        if not keep_indices:  # Must keep at least 1
            keep_indices = [0]
            print("You must keep at least one ticket. Keeping the first one.")
            
        player.tickets.extend([tickets[i] for i in keep_indices])
        
        # Return unwanted tickets to deck
        unwanted_tickets = [tickets[i] for i in range(len(tickets)) if i not in keep_indices]
        deck.ticket_cards.extend(unwanted_tickets)
        deck.shuffle_ticket_cards()
        
        input("\nPress Enter when you're done viewing your cards...")
    
    # Set up face-up cards
    deck.setup_face_up_cards()
    
    # Create game state
    game_state = GameState(board, players, 0, deck)
    
    # Main game loop
    turn_number = 1
    current_player_idx = 0
    game_over = False
    final_round = False
    final_round_trigger_player = None
    
    while not game_over:
        clear_screen()
        current_player = players[current_player_idx]
        
        print(f"\n=== Turn {turn_number}: {current_player.name}'s turn ===")
        print("\nGame status:")
        for p in players:
            print(f"  {p.name}: {p.score} points, {p.trains} trains left")
        
        display_board_status(board)
        input(f"\n{current_player.name}, press Enter to start your turn...")
        
        clear_screen()
        print(f"\n{current_player.name}'s turn:")
        
        # Display player's current state
        display_player_info(current_player, deck)
        
        # Let player choose an action
        print("\nChoose your action:")
        print("1. Draw train cards")
        print("2. Claim a route")
        print("3. Draw ticket cards")
        
        valid_choice = False
        while not valid_choice:
            try:
                choice = int(input("\nEnter choice (1-3): "))
                if 1 <= choice <= 3:
                    valid_choice = True
                else:
                    print("Please enter a number between 1 and 3.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Process the action
        if choice == 1:  # Draw train cards
            # Draw 2 cards total
            for draw in range(2):
                if draw > 0:
                    display_player_info(current_player, deck)
                
                print(f"\nDraw {draw+1}/2:")
                print("Choose a card to draw:")
                print("0-4: Take a face-up card")
                print("D: Draw from the deck")
                
                card_choice = input("Your choice: ").strip().upper()
                
                if card_choice == 'D':
                    # Draw from deck
                    card = deck.draw_train_card()
                    if card:
                        current_player.hand.append(card)
                        print(f"You drew: {card}")
                    else:
                        print("The train deck is empty!")
                        break
                elif card_choice.isdigit() and 0 <= int(card_choice) < len(deck.face_up_cards):
                    # Take face-up card
                    index = int(card_choice)
                    card = deck.face_up_cards[index]
                    
                    # Check if it's a wild card for the first draw
                    if card == 'wild' and draw == 0:
                        current_player.hand.append(card)
                        deck.replace_face_up_card(index)
                        print(f"You took a wild card! You can't draw a second card this turn.")
                        break
                    else:
                        current_player.hand.append(card)
                        deck.replace_face_up_card(index)
                        print(f"You took: {card}")
                else:
                    print("Invalid choice, try again.")
                    draw -= 1  # Retry this draw
        
        elif choice == 2:  # Claim a route
            print("\nClaim a route:")
            print("Enter the two cities and the color to use (or 'back' to go back)")
            print("Format: CityA, CityB, Color")
            print("Example: New York, Boston, red")
            
            trying_to_claim = True
            while trying_to_claim:
                claim_input = input("Your claim: ").strip()
                if claim_input.lower() == 'back':
                    # Go back to action selection
                    valid_choice = False
                    trying_to_claim = False
                    continue
                
                try:
                    parts = [p.strip() for p in claim_input.split(',')]
                    if len(parts) != 3:
                        print("Please enter two cities and a color, separated by commas.")
                        continue
                    
                    city1, city2, color = parts
                    
                    # Create the action
                    action = {
                        'action_type': 'claim_route',
                        'city1': city1,
                        'city2': city2,
                        'color': color.lower()
                    }
                    
                    # Try to execute it
                    result = execute_action(current_player, action, game_state)
                    
                    if result:
                        print(f"Successfully claimed route from {city1} to {city2}!")
                        # Check for final round trigger
                        if current_player.trains <= 2:
                            print(f"{current_player.name} has {current_player.trains} trains left! Final round begins!")
                            final_round = True
                            final_round_trigger_player = current_player_idx
                        trying_to_claim = False  # Exit the claiming loop
                    else:
                        print("Could not claim that route. Try again or enter 'back'.")
                except Exception as e:
                    print(f"Error: {e}")
                    print("Try again or enter 'back'.")
        
        elif choice == 3:  # Draw ticket cards
            if len(deck.ticket_cards) >= 3:
                tickets = [deck.draw_ticket_card() for _ in range(3)]
                print(f"\n{current_player.name}, you received these tickets:")
                for i, ticket in enumerate(tickets):
                    city1, city2, points = ticket
                    print(f"{i}: {city1} to {city2} ({points} points)")
                
                keep_indices = input("\nEnter indices to keep (e.g., 0 1 2): ").split()
                keep_indices = [int(idx) for idx in keep_indices if idx.isdigit() and 0 <= int(idx) < len(tickets)]
                
                if not keep_indices:  # Must keep at least 1
                    keep_indices = [0]
                    print("You must keep at least one ticket. Keeping the first one.")
                    
                current_player.tickets.extend([tickets[i] for i in keep_indices])
                
                # Return unwanted tickets to deck
                unwanted_tickets = [tickets[i] for i in range(len(tickets)) if i not in keep_indices]
                deck.ticket_cards.extend(unwanted_tickets)
                deck.shuffle_ticket_cards()
            else:
                print("Not enough ticket cards remaining!")
        
        # Move to next player
        current_player_idx = (current_player_idx + 1) % len(players)
        
        # Check for game end
        if final_round and current_player_idx == final_round_trigger_player:
            game_over = True
        
        if current_player_idx == 0:
            turn_number += 1
        
        input("\nPress Enter to continue to next player's turn...")
    
    # Game is over, calculate final scores
    clear_screen()
    print("\n=== Game Over! Final Scoring ===")
    
    for player in players:
        print(f"\nScoring for {player.name}:")
        print(f"Points from routes: {player.score}")
        
        # Score tickets
        ticket_score = check_tickets(player, board)
        print(f"Points from tickets: {'+' if ticket_score >= 0 else ''}{ticket_score}")
        
        # Longest path bonus
        longest_path_score = longest_continuous_path(player, board)
        print(f"Longest continuous path bonus: +{longest_path_score}")
        
        # Update final score
        final_score = player.score + ticket_score + longest_path_score
        print(f"Final score: {final_score}")
        player.score = final_score
    
    # Determine winner
    winner = max(players, key=lambda p: p.score)
    print(f"\nThe winner is {winner.name} with {winner.score} points!")
    
    print("\nTest gameplay complete.")
    return game_state

if __name__ == "__main__":
    test_interactive_gameplay()