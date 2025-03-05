import os
import sys
import unittest
import pygame

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import game state and related classes
from game.game_state import GameState
from game.units.squad import Squad
from game.units.unit import Unit
from game.mission.mission import Mission
from game.mission.mission_manager import MissionManager

class TestGameState(unittest.TestCase):
    """Test the GameState class"""
    
    def setUp(self):
        """Set up for the tests"""
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Create a game state with mission_mode=True to avoid auto-creating test units
        self.game_state = GameState(mission_mode=True)
        
        # Create some squads and units for testing
        self.player_squad1 = Squad("Player Squad 1", "player", (100, 100))
        self.player_squad2 = Squad("Player Squad 2", "player", (150, 150))
        self.enemy_squad = Squad("Enemy Squad", "enemy", (300, 300))
        
        self.unit1 = Unit("test_unit1", (100, 100), "player")
        self.unit2 = Unit("test_unit2", (150, 150), "player")
        self.enemy_unit = Unit("enemy_unit", (300, 300), "enemy")
        
        self.player_squad1.add_unit(self.unit1)
        self.player_squad2.add_unit(self.unit2)
        self.enemy_squad.add_unit(self.enemy_unit)
        
        # Add squads to game state
        self.game_state.player_squads.append(self.player_squad1)
        self.game_state.player_squads.append(self.player_squad2)
        self.game_state.enemy_squads.append(self.enemy_squad)
    
    def tearDown(self):
        """Clean up after the tests"""
        pygame.quit()
    
    def test_game_state_initialization(self):
        """Test that the game state initializes correctly"""
        # Check basic game state attributes
        self.assertIsInstance(self.game_state.player_squads, list)
        self.assertIsInstance(self.game_state.enemy_squads, list)
        self.assertIsInstance(self.game_state.selected_squads, list)
        self.assertEqual(len(self.game_state.player_squads), 2)
        self.assertEqual(len(self.game_state.enemy_squads), 1)
        self.assertEqual(len(self.game_state.selected_squads), 0)
    
    def test_squad_selection(self):
        """Test squad selection in the game state"""
        # Mock the screen_to_world_func function
        def screen_to_world_func(x, y):
            return (x, y)
        
        # Initially no squads selected
        self.assertEqual(len(self.game_state.selected_squads), 0)
        
        # Define a selection rectangle that encompasses player_squad1
        start_pos = (90, 90)
        end_pos = (110, 110)
        
        # Process selection
        selection = self.game_state.handle_selection(start_pos, end_pos, screen_to_world_func)
        
        # Check that the selection was processed
        self.assertEqual(len(self.game_state.selected_units), 1)
        self.assertIn(self.unit1, self.game_state.selected_units)
        
        # Deselect by selecting empty space
        empty_start = (0, 0)
        empty_end = (10, 10)
        self.game_state.handle_selection(empty_start, empty_end, screen_to_world_func)
        self.assertEqual(len(self.game_state.selected_units), 0)
        self.assertEqual(len(self.game_state.selected_squads), 0)
    
    def test_get_all_player_units(self):
        """Test getting all player units from the game state"""
        # Call get_all_player_units method
        player_units = self.game_state.get_all_player_units()
        
        # Should contain all units from player squads
        self.assertIn(self.unit1, player_units)
        self.assertIn(self.unit2, player_units)
        self.assertNotIn(self.enemy_unit, player_units)
        self.assertEqual(len(player_units), 2)
    
    def test_get_all_enemy_units(self):
        """Test getting all enemy units"""
        # Call get_all_enemy_units method
        enemy_units = self.game_state.get_all_enemy_units()
        
        # Should contain only enemy units
        self.assertNotIn(self.unit1, enemy_units)
        self.assertNotIn(self.unit2, enemy_units)
        self.assertIn(self.enemy_unit, enemy_units)
        self.assertEqual(len(enemy_units), 1)
    
    def test_game_mode(self):
        """Test game attributes"""
        # Test default mission state
        self.assertEqual(self.game_state.mission_name, "Test Mission")
        self.assertFalse(self.game_state.mission_complete)
        self.assertFalse(self.game_state.mission_failed)
        
        # Update game state
        self.game_state.update(0.1)
        self.assertEqual(round(self.game_state.game_time * 10), 1)  # 0.1 seconds added
    
    def test_mission_state(self):
        """Test the mission state in the game state"""
        # Create a simple test mission
        mission = Mission("test_mission", "Test Mission", "Test mission description")
        
        # Check that the mission manager can be created
        mission_manager = MissionManager()
        self.assertIsInstance(mission_manager, MissionManager)
        
        # Mission would typically be loaded by the mission manager
        # but for the test we'll just set some properties directly
        self.game_state.mission_name = mission.name
        self.game_state.mission_objectives = ["Eliminate all enemies"]
        
        # Test mission state
        self.assertEqual(self.game_state.mission_name, mission.name)
        self.assertEqual(len(self.game_state.mission_objectives), 1)


if __name__ == '__main__':
    unittest.main()
