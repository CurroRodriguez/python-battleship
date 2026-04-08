import unittest

from battleship.models import Ship, Board, Game, Direction, ShotResult


class TestShip(unittest.TestCase):
    """Unit tests for the Ship class."""

    def test_horizontal_ship_coordinates(self):
        """A horizontal ship should occupy consecutive x coordinates."""
        ship = Ship(x=2, y=1, size=4, direction=Direction.HORIZONTAL)
        coords = ship.get_coordinates()
        self.assertEqual(coords, [(2, 1), (3, 1), (4, 1), (5, 1)])

    def test_vertical_ship_coordinates(self):
        """A vertical ship should occupy consecutive y coordinates."""
        ship = Ship(x=7, y=4, size=3, direction=Direction.VERTICAL)
        coords = ship.get_coordinates()
        self.assertEqual(coords, [(7, 4), (7, 5), (7, 6)])

    def test_ship_direction_from_string(self):
        """Ship should accept direction as string."""
        ship = Ship(x=0, y=0, size=2, direction="H")
        self.assertEqual(ship.direction, Direction.HORIZONTAL)
        
        ship_v = Ship(x=0, y=0, size=2, direction="V")
        self.assertEqual(ship_v.direction, Direction.VERTICAL)

    def test_ship_within_bounds(self):
        """Ship should correctly detect if it's within board bounds."""
        ship = Ship(x=0, y=0, size=3, direction=Direction.HORIZONTAL)
        self.assertTrue(ship.is_within_bounds(10))
        
    def test_ship_outside_bounds_horizontal(self):
        """Horizontal ship extending past board edge should be out of bounds."""
        ship = Ship(x=8, y=1, size=4, direction=Direction.HORIZONTAL)
        self.assertFalse(ship.is_within_bounds(10))

    def test_ship_outside_bounds_vertical(self):
        """Vertical ship extending past board edge should be out of bounds."""
        ship = Ship(x=5, y=8, size=4, direction=Direction.VERTICAL)
        self.assertFalse(ship.is_within_bounds(10))

    def test_ships_overlap(self):
        """Two ships that share a coordinate should be detected as overlapping."""
        ship1 = Ship(x=5, y=5, size=4, direction=Direction.HORIZONTAL)
        ship2 = Ship(x=7, y=4, size=3, direction=Direction.VERTICAL)
        self.assertTrue(ship1.overlaps_with(ship2))

    def test_ships_no_overlap(self):
        """Two ships that don't share coordinates should not overlap."""
        ship1 = Ship(x=0, y=0, size=3, direction=Direction.HORIZONTAL)
        ship2 = Ship(x=0, y=1, size=3, direction=Direction.HORIZONTAL)
        self.assertFalse(ship1.overlaps_with(ship2))

    def test_register_hit(self):
        """Ship should register a hit at valid coordinates."""
        ship = Ship(x=2, y=1, size=4, direction=Direction.HORIZONTAL)
        self.assertTrue(ship.register_hit(3, 1))
        self.assertIn((3, 1), ship.hits)

    def test_register_hit_miss(self):
        """Ship should not register a hit at coordinates it doesn't occupy."""
        ship = Ship(x=2, y=1, size=4, direction=Direction.HORIZONTAL)
        self.assertFalse(ship.register_hit(0, 0))

    def test_ship_sunk(self):
        """Ship should be sunk after all coordinates are hit."""
        ship = Ship(x=0, y=0, size=2, direction=Direction.HORIZONTAL)
        ship.register_hit(0, 0)
        ship.register_hit(1, 0)
        self.assertTrue(ship.is_sunk())

    def test_ship_not_sunk(self):
        """Ship should not be sunk if not all coordinates are hit."""
        ship = Ship(x=0, y=0, size=2, direction=Direction.HORIZONTAL)
        ship.register_hit(0, 0)
        self.assertFalse(ship.is_sunk())


class TestBoard(unittest.TestCase):
    """Unit tests for the Board class."""

    def test_board_creation(self):
        """Board should be created with correct size."""
        board = Board(size=10)
        self.assertEqual(board.size, 10)
        self.assertEqual(len(board.ships), 0)

    def test_add_ship(self):
        """Ships should be added to the board."""
        board = Board()
        ship = Ship(x=0, y=0, size=3, direction=Direction.HORIZONTAL)
        board.add_ship(ship)
        self.assertEqual(len(board.ships), 1)

    def test_validate_ships_within_bounds(self):
        """Valid ships should pass validation."""
        board = Board()
        board.add_ship(Ship(x=0, y=0, size=3, direction=Direction.HORIZONTAL))
        is_valid, error = board.validate_ships()
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_ships_out_of_bounds(self):
        """Ships out of bounds should fail validation."""
        board = Board()
        board.add_ship(Ship(x=8, y=0, size=4, direction=Direction.HORIZONTAL))
        is_valid, error = board.validate_ships()
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_ships_overlap(self):
        """Overlapping ships should fail validation."""
        board = Board()
        board.add_ship(Ship(x=5, y=5, size=4, direction=Direction.HORIZONTAL))
        board.add_ship(Ship(x=7, y=4, size=3, direction=Direction.VERTICAL))
        is_valid, error = board.validate_ships()
        self.assertFalse(is_valid)

    def test_get_ship_at(self):
        """Should return the ship at given coordinates."""
        board = Board()
        ship = Ship(x=0, y=0, size=3, direction=Direction.HORIZONTAL)
        board.add_ship(ship)
        result = board.get_ship_at(1, 0)
        self.assertEqual(result, ship)

    def test_get_ship_at_empty(self):
        """Should return None when no ship at coordinates."""
        board = Board()
        board.add_ship(Ship(x=0, y=0, size=3, direction=Direction.HORIZONTAL))
        result = board.get_ship_at(5, 5)
        self.assertIsNone(result)

    def test_is_within_bounds(self):
        """Should correctly check if coordinates are within bounds."""
        board = Board()
        self.assertTrue(board.is_within_bounds(0, 0))
        self.assertTrue(board.is_within_bounds(9, 9))
        self.assertFalse(board.is_within_bounds(10, 0))
        self.assertFalse(board.is_within_bounds(0, 10))
        self.assertFalse(board.is_within_bounds(-1, 0))


class TestGame(unittest.TestCase):
    """Unit tests for the Game class."""

    def test_create_game(self):
        """Game should be created with valid ships."""
        game = Game()
        ships = [
            {"x": 0, "y": 0, "size": 3, "direction": "H"},
            {"x": 0, "y": 1, "size": 2, "direction": "H"},
        ]
        success, error = game.create_game(ships)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertIsNotNone(game.board)

    def test_create_game_invalid_ships(self):
        """Game creation should fail with invalid ships."""
        game = Game()
        ships = [{"x": 8, "y": 0, "size": 4, "direction": "H"}]
        success, error = game.create_game(ships)
        self.assertFalse(success)
        self.assertIsNotNone(error)

    def test_shot_water(self):
        """Shot at empty coordinates should return WATER."""
        game = Game()
        game.create_game([{"x": 0, "y": 0, "size": 2, "direction": "H"}])
        result, error = game.process_shot(5, 5)
        self.assertEqual(result, ShotResult.WATER)
        self.assertIsNone(error)

    def test_shot_hit(self):
        """Shot at ship coordinates should return HIT."""
        game = Game()
        game.create_game([{"x": 0, "y": 0, "size": 3, "direction": "H"}])
        result, error = game.process_shot(1, 0)
        self.assertEqual(result, ShotResult.HIT)
        self.assertIsNone(error)

    def test_shot_sink(self):
        """Last shot to sink a ship should return SINK."""
        game = Game()
        game.create_game([{"x": 0, "y": 0, "size": 2, "direction": "H"}])
        game.process_shot(0, 0)
        result, error = game.process_shot(1, 0)
        self.assertEqual(result, ShotResult.SINK)
        self.assertIsNone(error)

    def test_shot_hit_sunk_ship(self):
        """Hitting an already sunk ship should return HIT."""
        game = Game()
        game.create_game([{"x": 0, "y": 0, "size": 1, "direction": "H"}])
        game.process_shot(0, 0)  # Sinks the ship
        result, error = game.process_shot(0, 0)  # Hit the sunk ship again
        self.assertEqual(result, ShotResult.HIT)

    def test_shot_out_of_bounds(self):
        """Shot outside board should return error."""
        game = Game()
        game.create_game([{"x": 0, "y": 0, "size": 2, "direction": "H"}])
        result, error = game.process_shot(10, 7)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_delete_game(self):
        """Deleting game should clear the board."""
        game = Game()
        game.create_game([{"x": 0, "y": 0, "size": 2, "direction": "H"}])
        game.delete_game()
        self.assertIsNone(game.board)


if __name__ == "__main__":
    unittest.main()
