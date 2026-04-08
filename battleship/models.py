"""Domain models for the Battleship game."""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional


class Direction(Enum):
    """Ship direction on the board."""
    HORIZONTAL = "H"
    VERTICAL = "V"


class ShotResult(Enum):
    """Result of a shot."""
    WATER = "WATER"
    HIT = "HIT"
    SINK = "SINK"


@dataclass
class Ship:
    """Represents a ship on the battleship board."""
    x: int
    y: int
    size: int
    direction: Direction
    hits: Set[Tuple[int, int]] = field(default_factory=set)
    
    def __post_init__(self):
        if isinstance(self.direction, str):
            self.direction = Direction(self.direction)
    
    def get_coordinates(self) -> List[Tuple[int, int]]:
        """Get all coordinates occupied by this ship."""
        coords = []
        for i in range(self.size):
            if self.direction == Direction.HORIZONTAL:
                coords.append((self.x + i, self.y))
            else:  # VERTICAL
                coords.append((self.x, self.y + i))
        return coords
    
    def is_within_bounds(self, board_size: int = 10) -> bool:
        """Check if the ship is within the board boundaries."""
        for x, y in self.get_coordinates():
            if x < 0 or x >= board_size or y < 0 or y >= board_size:
                return False
        return True
    
    def overlaps_with(self, other: 'Ship') -> bool:
        """Check if this ship overlaps with another ship."""
        my_coords = set(self.get_coordinates())
        other_coords = set(other.get_coordinates())
        return bool(my_coords & other_coords)
    
    def register_hit(self, x: int, y: int) -> bool:
        """Register a hit at the given coordinates. Returns True if this ship was hit."""
        coord = (x, y)
        if coord in self.get_coordinates():
            self.hits.add(coord)
            return True
        return False
    
    def is_sunk(self) -> bool:
        """Check if the ship is completely sunk."""
        return len(self.hits) >= self.size
    
    def is_hit_at(self, x: int, y: int) -> bool:
        """Check if the ship has been hit at the given coordinates."""
        return (x, y) in self.hits
    
    def occupies(self, x: int, y: int) -> bool:
        """Check if this ship occupies the given coordinate."""
        return (x, y) in self.get_coordinates()


class Board:
    """Represents the battleship game board."""
    
    def __init__(self, size: int = 10):
        self.size = size
        self.ships: List[Ship] = []
    
    def add_ship(self, ship: Ship) -> None:
        """Add a ship to the board."""
        self.ships.append(ship)
    
    def validate_ships(self) -> Tuple[bool, Optional[str]]:
        """
        Validate all ships on the board.
        Returns (is_valid, error_message).
        """
        # Check if all ships are within bounds
        for ship in self.ships:
            if not ship.is_within_bounds(self.size):
                return False, "Ship falls outside of board boundaries"
        
        # Check for overlapping ships
        for i, ship1 in enumerate(self.ships):
            for ship2 in self.ships[i + 1:]:
                if ship1.overlaps_with(ship2):
                    return False, "Ships overlap"
        
        return True, None
    
    def get_ship_at(self, x: int, y: int) -> Optional[Ship]:
        """Get the ship at the given coordinates, if any."""
        for ship in self.ships:
            if ship.occupies(x, y):
                return ship
        return None
    
    def is_within_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within the board."""
        return 0 <= x < self.size and 0 <= y < self.size


class Game:
    """Manages the battleship game state."""
    
    def __init__(self):
        self.board: Optional[Board] = None
    
    def create_game(self, ships_data: List[dict]) -> Tuple[bool, Optional[str]]:
        """
        Create a new game with the given ships.
        Returns (success, error_message).
        """
        board = Board()
        
        for ship_data in ships_data:
            ship = Ship(
                x=ship_data['x'],
                y=ship_data['y'],
                size=ship_data['size'],
                direction=ship_data['direction']
            )
            board.add_ship(ship)
        
        is_valid, error = board.validate_ships()
        if not is_valid:
            return False, error
        
        self.board = board
        return True, None
    
    def process_shot(self, x: int, y: int) -> Tuple[Optional[ShotResult], Optional[str]]:
        """
        Process a shot at the given coordinates.
        Returns (result, error_message).
        """
        if self.board is None:
            return None, "No game in progress"
        
        if not self.board.is_within_bounds(x, y):
            return None, "Shot is out of bounds"
        
        ship = self.board.get_ship_at(x, y)
        
        if ship is None:
            return ShotResult.WATER, None
        
        # Check if ship was already sunk before this hit
        was_already_sunk = ship.is_sunk()
        
        # Register the hit
        ship.register_hit(x, y)
        
        if was_already_sunk:
            # Hitting an already sunk ship returns HIT
            return ShotResult.HIT, None
        
        if ship.is_sunk():
            return ShotResult.SINK, None
        
        return ShotResult.HIT, None
    
    def delete_game(self) -> None:
        """Delete the current game."""
        self.board = None
