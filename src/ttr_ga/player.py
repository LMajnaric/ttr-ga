import random
from ttr_ga.utils.state import GameState

class Deck:
    def __init__(self):
        self.train_cards = ["red", "blue", "green", "yellow", "black", "pink", "orange", "white"] * 12 + ["wild"] * 14
        random.shuffle(self.train_cards)
        self.ticket_cards = [("Seattle", "New York", 22), ("Los Angeles", "New York", 21), ("Los Angeles", "Miami", 20), ("Vancouver", "Montreal", 20), ("Portland", "Nashville", 17), ("San Francisco", "Atlanta", 17), ("Los Angeles", "Chicago", 16),
                             ("Calgary", "Phoenix", 13), ("Montreal", "New Orleans", 13), ("Vancouver", "Santa Fe", 13), ("Boston", "Miami", 12), ("Winnipeg", "Houston", 12), ("Dallas", "New York", 11), ("Dnever", "Pittsburgh", 11),
                             ("Portland", "Phoenix", 11), ("Winnipeg", "Little Rock", 11), ("Duluth", "El Paso", 10), ("Toronto", "Miami", 10), ("Chicago", "Santa Fe", 9), ("Montreal", "Atlanta", 9), ("Sault St Marie", "Oklahoma City", 9),
                             ("Seattle", "Los Angeles", 9), ("Duluth", "Houston", 8), ("Helena", "Los Angeles", 8), ("Sault St Marie", "Nashville", 8), ("Calgary", "Salt Lake City", 7), ("Chicago", "New Orleans", 7), ("New York", "Atlanta", 6),
                             ("Kansas City", "Houston", 5), ("Denver", "El Paso", 4)]
        random.shuffle(self.ticket_cards)
        self.face_up_cards = [self.train_cards.pop() for _ in range(5)]

    def draw_train_card(self):
        return self.train_cards.pop()

    def draw_ticket_card(self):
        return self.ticket_cards.pop()
    
    def shuffle_train_cards(self):
        """Shuffle the train card deck"""
        import random
        random.shuffle(self.train_cards)

    def shuffle_ticket_cards(self):
        """Shuffle the ticket card deck"""
        import random
        random.shuffle(self.ticket_cards)
        
    def setup_face_up_cards(self):
        """Set up the initial face-up cards, ensuring no more than 2 wilds"""
        self.face_up_cards = []
        for _ in range(5):
            self.add_face_up_card()
        
        # Check for 3+ wilds
        self.check_and_replace_wilds()
    
    def add_face_up_card(self):
        """Add a new card to the face-up cards"""
        if self.train_cards:
            self.face_up_cards.append(self.draw_train_card())
    
    def replace_face_up_card(self, index):
        """Replace a face-up card and check for too many wilds"""
        if 0 <= index < len(self.face_up_cards):
            if self.train_cards:
                self.face_up_cards[index] = self.draw_train_card()
                self.check_and_replace_wilds()
    
    def check_and_replace_wilds(self):
        """Check for 3+ wilds in face-up cards and replace all if found"""
        wild_count = self.face_up_cards.count('wild')
        if wild_count >= 3:
            print("Three or more wild cards present. Replacing all face-up cards.")
            # Put the current face-up cards back in the deck
            self.train_cards.extend(self.face_up_cards)
            random.shuffle(self.train_cards)
            
            # Draw new face-up cards
            self.face_up_cards = []
            for _ in range(5):
                if self.train_cards:
                    self.face_up_cards.append(self.draw_train_card())
            
            # Check again (recursive call)
            self.check_and_replace_wilds()

class Player:
    """Base class for all players (human and AI)"""
    def __init__(self, name):
        self.name = name
        self.trains = 45
        self.hand = []
        self.tickets = []
        self.score = 0

    def choose_action(self, game_state):
        """Must be implemented by subclasses"""
        raise NotImplementedError

    def draw_initial_cards(self, deck):
        for _ in range(4):
            self.hand.append(deck.draw_train_card())

    def calculate_route_score(self, length):
        if length == 1:
            return 1
        elif length == 2:
            return 2
        elif length == 3:
            return 4
        elif length == 4:
            return 7
        elif length == 5:
            return 10
        elif length == 6:
            return 15
        
    def add_tickets(self, tickets):
        """Add specified tickets to the player's hand"""
        self.tickets.extend(tickets)
    
    def draw_ticket_cards(self, deck, count=3, min_keep=1):
        """
        Draw ticket cards from the deck
        Returns the tickets drawn but not kept
        
        This base implementation keeps all tickets (for AI use)
        """
        if len(deck.ticket_cards) < count:
            count = len(deck.ticket_cards)  # Draw as many as available
            
        if count == 0:
            return []
            
        # Draw tickets
        tickets = [deck.draw_ticket_card() for _ in range(count)]
        
        # Base implementation keeps all tickets
        self.tickets.extend(tickets)
        
        return []  # No tickets returned to deck


class HumanPlayer(Player):
    """Human player implementation with input"""
    
    def choose_action(self, game_state):
        print(f"{self.name}'s turn. Choose an action:")
        print("1: Draw train cards")
        print("2: Claim a route")
        print("3: Draw destination ticket cards")
        
        action = input("Enter your choice (1/2/3): ")
        
        if action == '1':
            return self._choose_draw_train_cards()
        elif action == '2':
            return self._choose_claim_route(game_state.board)
        elif action == '3':
            return {"action_type": "draw_tickets"}
        else:
            print("Invalid choice. Try again.")
            return self.choose_action(game_state)
        
    def _choose_draw_train_cards(self):
        print("Choose how to draw train cards:")
        print("1: Draw two blind cards")
        print("2: Draw one blind card and one face-up card")
        print("3: Draw two face-up cards (Wild card can only be taken as a single card)")
        
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == '1':
            return {"action_type": "draw_train_cards", "method": "blind", "count": 2}
        elif choice == '2':
            return {"action_type": "draw_train_cards", "method": "mixed", "blind_count": 1}
        elif choice == '3':
            return {"action_type": "draw_train_cards", "method": "face_up", "count": 2}
        else:
            print("Invalid choice. Try again.")
            return self._choose_draw_train_cards()
    
    def _choose_claim_route(self, board):
        print("Choose a route to claim:")
        for i, (city1, city2, data) in enumerate(board.graph.edges(data=True)):
            if 'claimed' not in data:  # Only show unclaimed routes
                print(f"{i}: {city1} to {city2} ({data['color']}, {data['length']})")
        
        try:
            route_choice = int(input("Enter the route number: "))
            route = list(board.graph.edges(data=True))[route_choice]
            
            if 'claimed' in route[2]:
                print("This route is already claimed. Choose another.")
                return self._choose_claim_route(board)
            
            color = input("Enter the color of the cards you are using to claim the route: ")
            
            return {
                "action_type": "claim_route",
                "city1": route[0],
                "city2": route[1],
                "color": color
            }
        except (ValueError, IndexError):
            print("Invalid choice. Try again.")
            return self._choose_claim_route(board)
    
    def draw_ticket_cards(self, deck, count=3, min_keep=1):
        """
        Interactive version of ticket drawing that prompts the user
        Returns the tickets drawn but not kept
        """
        if len(deck.ticket_cards) < count:
            count = len(deck.ticket_cards)
            
        if count == 0:
            print("No ticket cards left in the deck.")
            return []
            
        # Draw tickets
        tickets = [deck.draw_ticket_card() for _ in range(count)]
        
        print(f"{self.name} received tickets:")
        for i, ticket in enumerate(tickets):
            city1, city2, points = ticket
            print(f"{i}: {city1} to {city2} ({points} points)")
        
        # Get user selection
        keep_tickets = input(f"Enter the indices of the tickets you want to keep (minimum {min_keep}): ").split()
        keep_indices = []
        
        for idx in keep_tickets:
            try:
                idx = int(idx)
                if 0 <= idx < len(tickets):
                    keep_indices.append(idx)
            except ValueError:
                pass
        
        # Ensure minimum number of tickets kept
        if len(keep_indices) < min_keep:
            print(f"You must keep at least {min_keep} ticket(s). Keeping the first {min_keep}.")
            keep_indices = list(range(min(min_keep, count)))
        
        # Add kept tickets to player's hand
        kept_tickets = [tickets[i] for i in keep_indices]
        self.tickets.extend(kept_tickets)
        
        # Return unwanted tickets
        return_tickets = [tickets[i] for i in range(len(tickets)) if i not in keep_indices]
        
        print(f"Kept tickets: {', '.join([f'{t[0]} to {t[1]}' for t in kept_tickets])}")
        return return_tickets
    
    # Implement this interface method instead of the old take_turn
    def take_turn(self, deck, board):
        game_state = GameState(board, [self], 0, deck)  # Temporary game state
        action = self.choose_action(game_state)
        return action
        # execute_action(self, action, game_state)