import os
import sys
import unittest
import pygame
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Unit class and related classes
from game.units.unit import Unit
from game.units.portal_archer import PortalArcher
from game.units.dimensioneer import Dimensioneer
from game.game_state import GameState

class TestUnit(unittest.TestCase):
    """Test the Unit class"""
    
    def setUp(self):
        """Set up for the tests"""
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Create a game state
        self.game_state = GameState()
        
        # Create test units
        self.player_unit = Unit("test_unit", (100, 100, 0), "player")
        self.enemy_unit = Unit("enemy_unit", (200, 200, 0), "enemy")
        
        # Create specialized units
        self.portal_archer = PortalArcher((150, 150, 0), "player")
        self.dimensioneer = Dimensioneer((250, 250, 0), "player")
    
    def tearDown(self):
        """Clean up after the tests"""
        pygame.quit()
    
    def test_unit_initialization(self):
        """Test that units initialize correctly"""
        # Check basic unit attributes
        self.assertEqual(self.player_unit.type, "test_unit")
        self.assertEqual(self.player_unit.faction, "player")
        self.assertEqual(self.player_unit.position, (100, 100, 0))
        self.assertEqual(self.player_unit.state, "idle")
        self.assertTrue(self.player_unit.is_alive())
        
        # Check specialized unit attributes
        self.assertEqual(self.portal_archer.type, "portal_archer")
        self.assertEqual(self.dimensioneer.type, "dimensioneer")
    
    def test_take_damage(self):
        """Test unit damage calculations"""
        # Test normal damage
        initial_health = self.player_unit.health
        self.player_unit.take_damage(20)
        self.assertEqual(self.player_unit.health, initial_health - 20)
        
        # Test damage with attacker
        self.player_unit.take_damage(10, self.enemy_unit)
        self.assertEqual(self.player_unit.health, initial_health - 30)
        self.assertEqual(self.player_unit.last_attacker, self.enemy_unit)
        
        # Test damage with string attacker (should not crash)
        self.player_unit.take_damage(10, "some_string_attacker")
        self.assertEqual(self.player_unit.health, initial_health - 40)
        self.assertEqual(self.player_unit.last_attacker, "some_string_attacker")
        
        # Test fatal damage
        self.player_unit.take_damage(self.player_unit.health)
        self.assertEqual(self.player_unit.health, 0)
        self.assertEqual(self.player_unit.state, "dead")
        self.assertFalse(self.player_unit.is_alive())
    
    def test_healing(self):
        """Test unit healing"""
        # Damage the unit
        self.player_unit.take_damage(50)
        initial_health = self.player_unit.health
        
        # Heal the unit
        self.player_unit.heal(20)
        self.assertEqual(self.player_unit.health, initial_health + 20)
        
        # Test overhealing (should cap at max_health)
        self.player_unit.heal(1000)
        self.assertEqual(self.player_unit.health, self.player_unit.max_health)
    
    def test_movement(self):
        """Test unit movement"""
        # Set a destination
        self.player_unit.set_destination((150, 150, 0))
        self.assertEqual(self.player_unit.state, "moving")
        
        # Update the unit to simulate movement
        dt = 0.1  # 100ms
        initial_position = np.array(self.player_unit.position)
        self.player_unit.update(dt, self.game_state)
        
        # Check that the unit moved in the right direction
        current_position = np.array(self.player_unit.position)
        direction = current_position - initial_position
        target_direction = np.array([150, 150, 0]) - initial_position
        
        # Normalize both vectors
        direction_norm = np.linalg.norm(direction)
        if direction_norm > 0:
            direction = direction / direction_norm
        
        target_direction_norm = np.linalg.norm(target_direction)
        if target_direction_norm > 0:
            target_direction = target_direction / target_direction_norm
        
        # Check if the directions match (with some tolerance)
        dot_product = np.dot(direction, target_direction)
        self.assertGreater(dot_product, 0.9, "Unit did not move in the right direction")
    
    def test_attack_commands(self):
        """Test unit attack commands"""
        # Set an attack target
        self.player_unit.set_target(self.enemy_unit)
        self.assertEqual(self.player_unit.target, self.enemy_unit)
        
        # Test attack mode
        self.player_unit.set_attack_mode(True)
        self.assertEqual(self.player_unit.state, "attacking")
        
        # Reset attack mode
        self.player_unit.set_attack_mode(False)
        self.assertEqual(self.player_unit.state, "idle")
    
    def test_specialized_units(self):
        """Test specialized unit attributes"""
        # Portal Archer
        self.assertEqual(self.portal_archer.type, "portal_archer")
        self.assertEqual(self.portal_archer.unit_type, "portal_archer")
        self.assertTrue(hasattr(self.portal_archer, 'max_health'))
        
        # Dimensioneer
        self.assertEqual(self.dimensioneer.type, "dimensioneer")
        self.assertEqual(self.dimensioneer.unit_type, "dimensioneer")
        self.assertTrue(hasattr(self.dimensioneer, 'max_health'))


if __name__ == '__main__':
    unittest.main()
