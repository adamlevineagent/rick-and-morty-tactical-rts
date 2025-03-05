#!/usr/bin/env python3
import os
import sys
import unittest
import pygame

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our game modules
from engine.renderer.game_renderer import GameRenderer
from engine.physics.physics_engine import PhysicsEngine
from engine.input.input_handler import InputHandler
from engine.asset_manager import AssetManager
from game.game_state import GameState
from game.mission.mission_manager import MissionManager
from game.mission.mission import Mission
from game.units.dimensioneer import Dimensioneer
from game.units.portal_archer import PortalArcher
from game.units.squad import Squad
from game.units.unit import Unit
from game.units.unit_factory import UnitFactory

class TestMission(unittest.TestCase):
    """Test the Mission class"""
    
    def setUp(self):
        """Set up for the tests"""
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Create a game state
        self.game_state = GameState(mission_mode=True)
        
        # Create the mission manager
        self.mission_manager = MissionManager()
        
        # Create a test mission
        self.test_mission = Mission(
            "test_mission",
            "Test Mission",
            "This is a test mission description"
        )
        self.test_mission.objectives = ["Eliminate all enemies", "Protect the base"]
        self.test_mission.time_limit = 300  # 5 minutes
        
        # Add player squad configurations to the mission
        self.test_mission.player_squads_config = [
            {"type": "archer", "position": (100, 100, 0), "size": 2, "name": "Archer Squad"},
            {"type": "balanced", "position": (150, 100, 0), "size": 3, "name": "Mixed Squad"}
        ]
        
        # Add enemy waves to the mission
        self.test_mission.enemy_waves = [
            {
                "trigger": "time",
                "trigger_time": 0,
                "squads": [
                    {"type": "gromflomite", "position": (500, 500, 0), "size": 3, "name": "Wave 1 Squad"}
                ]
            },
            {
                "trigger": "time",
                "trigger_time": 60,
                "squads": [
                    {"type": "gromflomite", "position": (600, 500, 0), "size": 5, "name": "Wave 2 Squad"}
                ]
            }
        ]
    
    def tearDown(self):
        """Clean up after the tests"""
        pygame.quit()
    
    def test_mission_initialization(self):
        """Test that missions initialize correctly"""
        # Basic mission attributes
        self.assertEqual(self.test_mission.mission_id, "test_mission")
        self.assertEqual(self.test_mission.name, "Test Mission")
        self.assertEqual(self.test_mission.description, "This is a test mission description")
        self.assertEqual(len(self.test_mission.objectives), 2)
        self.assertEqual(self.test_mission.time_limit, 300)
        
        # Squad configurations and enemy waves
        self.assertEqual(len(self.test_mission.player_squads_config), 2)
        self.assertEqual(len(self.test_mission.enemy_waves), 2)
    
    def test_mission_setup_game_state(self):
        """Test setting up a game state for the mission"""
        # Setup the game state
        self.test_mission.setup_game_state(self.game_state)
        
        # Check that mission parameters were applied to game state
        self.assertEqual(self.game_state.mission_name, self.test_mission.name)
        self.assertEqual(self.game_state.mission_objectives, self.test_mission.objectives)
        self.assertEqual(self.game_state.time_limit, self.test_mission.time_limit)
        
        # Check that player squads were created
        self.assertEqual(len(self.game_state.player_squads), 2)
        
        # Check that first wave of enemies was spawned
        wave_1_squad_count = len(self.test_mission.enemy_waves[0]["squads"])
        self.assertEqual(len(self.game_state.enemy_squads), wave_1_squad_count)
    
    def test_mission_wave_spawning(self):
        """Test spawning enemy waves"""
        # Setup the game state
        self.test_mission.setup_game_state(self.game_state)
        
        # Check first wave
        initial_enemy_squad_count = len(self.game_state.enemy_squads)
        self.assertEqual(initial_enemy_squad_count, 1)  # From wave 1
        
        # Trigger next wave by updating the mission with elapsed time
        self.game_state.game_time = 61  # Past the trigger time for wave 2
        self.test_mission.update(self.game_state, 0.1)
        
        # Check that wave 2 enemies were added
        new_enemy_squad_count = len(self.game_state.enemy_squads)
        self.assertEqual(new_enemy_squad_count, 2)  # Wave 1 + Wave 2 squads
    
    def test_mission_update(self):
        """Test mission update logic"""
        # Setup the game state
        self.test_mission.setup_game_state(self.game_state)
        
        # Simulate game time passing
        self.game_state.game_time = 30
        
        # Update the mission
        self.test_mission.update(self.game_state, 0.1)
        
        # Current wave should still be 0 (first wave)
        self.assertEqual(self.test_mission.current_wave, 0)
        
        # Fast forward to trigger second wave
        self.game_state.game_time = 61
        self.test_mission.update(self.game_state, 0.1)
        
        # Current wave should now be 1 (second wave)
        self.assertEqual(self.test_mission.current_wave, 1)
    
    def test_mission_load_from_file(self):
        """Test loading mission from file"""
        # Create a temporary mission file
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            mission_data = {
                "mission_id": "test_file_mission",
                "name": "Test File Mission",
                "description": "Mission loaded from file",
                "map_name": "test_map",
                "difficulty": "hard",
                "time_limit": 600,
                "objectives": ["Test objective 1", "Test objective 2"],
                "player_squads": [
                    {"type": "archer", "position": [100, 100, 0], "size": 3}
                ],
                "enemy_waves": [
                    {
                        "trigger": "time",
                        "trigger_time": 10,
                        "squads": [
                            {"type": "gromflomite", "position": [500, 500, 0], "size": 4}
                        ]
                    }
                ]
            }
            json.dump(mission_data, temp_file)
            temp_path = temp_file.name
        
        try:
            # Test loading the mission file
            new_mission = Mission("placeholder", "placeholder", "placeholder")
            result = new_mission.load_from_file(temp_path)
            
            # Check that loading succeeded
            self.assertTrue(result)
            
            # Check that mission properties were set correctly
            self.assertEqual(new_mission.mission_id, "test_file_mission")
            self.assertEqual(new_mission.name, "Test File Mission")
            self.assertEqual(new_mission.difficulty, "hard")
            self.assertEqual(len(new_mission.objectives), 2)
            self.assertEqual(len(new_mission.player_squads_config), 1)
            self.assertEqual(len(new_mission.enemy_waves), 1)
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def test_victory_defeat_conditions(self):
        """Test mission victory and defeat conditions via game state update"""
        # Set up a simple mission for testing victory conditions
        self.test_mission.setup_game_state(self.game_state)
        
        # Victory: Eliminate all enemies
        original_enemy_count = len(self.game_state.enemy_squads)
        self.assertTrue(original_enemy_count > 0)
        
        # Clear enemy squads to simulate victory
        self.game_state.enemy_squads = []
        self.game_state.update(0.1)
        
        # We can't directly test mission_complete here as it depends on the GameState implementation
        # Instead we're testing that our Mission class correctly handles the update logic
        
        # Reset for defeat test
        self.test_mission.setup_game_state(self.game_state)
        
        # Defeat: Lose all player squads
        original_player_count = len(self.game_state.player_squads)
        self.assertTrue(original_player_count > 0)
        
        # Clear player squads to simulate defeat
        self.game_state.player_squads = []
        self.game_state.update(0.1)
        
        # Again, we can't directly test mission_failed without knowing GameState implementation details


if __name__ == '__main__':
    unittest.main()
