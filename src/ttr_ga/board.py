import networkx as nx
from ttr_ga.common import CITIES, ROUTES

class Board:
    def __init__(self):
        self.graph = nx.MultiGraph()  # Use MultiGraph to handle double routes
        self.double_routes = []

    def add_city(self, city):
        self.graph.add_node(city)

    def add_route(self, city1, city2, length, color, is_double=False):
        if is_double:
            self.graph.add_edge(city1, city2, length=length, color=color)
            self.double_routes.append((city1, city2))
        else:
            self.graph.add_edge(city1, city2, length=length, color=color)
    
    @classmethod
    def create_standard_board(cls):
        """Create a standard Ticket to Ride USA board"""
        board = cls()
        
        for city in CITIES:
            board.add_city(city)
        
        for route in ROUTES:
            board.add_route(*route)
        
        return board
    
    def is_double_route(self, city1, city2):
        return (city1, city2) in self.double_routes or (city2, city1) in self.double_routes

    def claim_route(self, player, city1, city2, color=None, player_count=None):
        """
        Attempt to claim a route between two cities
        Returns True if successful, False otherwise
        
        For 2-3 player games, only one of the double routes can be claimed.
        For 4+ player games, a single player cannot claim both routes of a double route.
        """
        # Find the edge between the cities
        edge_data = self.graph.get_edge_data(city1, city2)
        if not edge_data:
            print(f"No route exists between {city1} and {city2}")
            return False
            
        # Check if any route is already claimed by this player
        player_already_claimed = any('claimed' in route and route['claimed'] == player.name 
                                    for key, route in edge_data.items())
        
        if player_already_claimed:
            print(f"{player.name} has already claimed a route between {city1} and {city2}")
            return False
        
        # For 2-3 player games, check if any route is claimed by any player
        double_route_blocked = False
        if player_count and player_count < 4:
            double_route_blocked = any('claimed' in route for key, route in edge_data.items())
            
        # Find an unclaimed route
        for key, route in edge_data.items():
            if 'claimed' not in route and not double_route_blocked:
                route_color = route['color']
                route_length = route['length']

                # Determine which color cards the player will use
                card_color = color or route_color

                # Check if player has required cards for this route
                can_claim, cards_to_use = self._player_can_claim_route(player, route_color, route_length, card_color)
                
                if can_claim:
                    # Remove cards from player's hand
                    for card in cards_to_use:
                        player.hand.remove(card)
                    
                    # Update player stats
                    player.trains -= route_length
                    player.score += player.calculate_route_score(route_length)
                    
                    # Mark route as claimed
                    route['claimed'] = player.name
                    print(f"{player.name} claimed route from {city1} to {city2}")
                    
                    # Check for final round trigger
                    if player.trains <= 2:
                        print(f"{player.name} has {player.trains} trains left! Final round begins!")
                        return True, "final_round"
                    
                    return True
                else:
                    print(f"Not enough cards to claim this route")
                    return False
        
        print(f"All routes between {city1} and {city2} are already claimed")
        return False

    def _player_can_claim_route(self, player, route_color, route_length, card_color):
        """
        Check if the player has the required cards to claim a route
        Returns (can_claim, cards_to_use)
        """
        cards_to_use = []
        
        # Gray routes can be claimed with any single color
        if route_color == 'gray':
            # Count cards by color
            color_counts = {}
            for card in player.hand:
                if card != 'wild':
                    color_counts[card] = color_counts.get(card, 0) + 1
            
            # Find the color with most cards (at least route_length)
            best_color = None
            best_count = 0
            
            for c, count in color_counts.items():
                if count >= route_length and count > best_count:
                    best_color = c
                    best_count = count
            
            if best_color:
                cards_to_use = [best_color] * route_length
                return True, cards_to_use
            
            # If no color has enough cards, check with wilds
            wild_count = player.hand.count('wild')
            
            for c, count in color_counts.items():
                if count + wild_count >= route_length:
                    # Use as many regular cards as possible, then fill with wilds
                    cards_to_use = [c] * min(count, route_length)
                    wilds_needed = route_length - len(cards_to_use)
                    cards_to_use.extend(['wild'] * wilds_needed)
                    return True, cards_to_use
            
            return False, []
        
        # Colored routes
        else:
            # Using specified color
            if card_color == route_color or route_color == 'gray':
                color_count = player.hand.count(card_color)
                wild_count = player.hand.count('wild')
                
                if color_count + wild_count >= route_length:
                    # Use as many regular cards as possible, then fill with wilds
                    cards_to_use = [card_color] * min(color_count, route_length)
                    wilds_needed = route_length - len(cards_to_use)
                    cards_to_use.extend(['wild'] * wilds_needed)
                    return True, cards_to_use
            
            return False, []

    def display(self):
        print("Cities:", self.graph.nodes)
        print("Routes:")
        for u, v, data in self.graph.edges(data=True):
            print(f"{u} - {v}: {data}")


