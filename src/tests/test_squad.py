import os
import sys
import unittest
import pygame
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import squad and unit classes
from game.units.squad import Squad, FormationType
from game.units.unit import Unit
from game.units.portal_archer import PortalArcher
from game.units.dimensioneer import Dimensioneer
from game.game_state import GameState

class TestSquad(unittest.TestCase):
    """Test the Squad class"""
    
    def setUp(self):
        """Set up for the tests"""
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Create a game state
        self.game_state = GameState()
        
        # Create a player squad - using 3D coordinates
        self.player_squad = Squad("Player Squad", "player", (100, 100, 0))
        
        # Add units to the squad - using 3D coordinates
        self.unit1 = Unit("test_unit1", (100, 100, 0), "player")
        self.unit2 = Unit("test_unit2", (120, 100, 0), "player")
        self.unit3 = PortalArcher((140, 100, 0), "player")
        self.unit4 = Dimensioneer((160, 100, 0), "player")
        
        self.player_squad.add_unit(self.unit1)
        self.player_squad.add_unit(self.unit2)
        self.player_squad.add_unit(self.unit3)
        self.player_squad.add_unit(self.unit4)
        
        # Create an enemy squad - using 3D coordinates
        self.enemy_squad = Squad("Enemy Squad", "enemy", (300, 300, 0))
        self.enemy_unit = Unit("enemy_unit", (300, 300, 0), "enemy")
        self.enemy_squad.add_unit(self.enemy_unit)
    
    def tearDown(self):
        """Clean up after the tests"""
        pygame.quit()
    
    def test_squad_initialization(self):
        """Test that squads initialize correctly"""
        # Check basic squad attributes
        self.assertEqual(self.player_squad.name, "Player Squad")
        self.assertEqual(self.player_squad.faction, "player")
        self.assertEqual(self.player_squad.position, [100, 100, 0])  # Updated for 3D position
        self.assertEqual(len(self.player_squad.units), 4)
    
    def test_unit_addition_removal(self):
        """Test adding and removing units from a squad"""
        # Test initial count
        initial_count = len(self.player_squad.units)
        
        # Add a new unit
        new_unit = Unit("new_unit", (180, 100), "player")
        self.player_squad.add_unit(new_unit)
        self.assertEqual(len(self.player_squad.units), initial_count + 1)
        self.assertIn(new_unit, self.player_squad.units)
        self.assertEqual(new_unit.squad, self.player_squad)
        
        # Remove the unit
        self.player_squad.remove_unit(new_unit)
        self.assertEqual(len(self.player_squad.units), initial_count)
        self.assertNotIn(new_unit, self.player_squad.units)
        
        # Test removing multiple units by removing them individually
        self.player_squad.remove_unit(self.unit1)
        self.player_squad.remove_unit(self.unit2)
        self.assertEqual(len(self.player_squad.units), initial_count - 2)
        self.assertNotIn(self.unit1, self.player_squad.units)
        self.assertNotIn(self.unit2, self.player_squad.units)
    
    def test_squad_movement(self):
        """Test squad movement commands"""
        # Set a destination for the squad - using 3D coordinates
        target_pos = (200, 200, 0)
        self.player_squad.move_to(target_pos)
        
        # Check that all units have formation positions
        for unit in self.player_squad.units:
            self.assertIsNotNone(unit.formation_position)
    
    def test_squad_formation(self):
        """Test squad formation positions"""
        # Update formation positions
        self.player_squad._update_formation()
        
        # Check that each unit has a formation position
        for unit in self.player_squad.units:
            self.assertIsNotNone(unit.formation_position)
        
        # Check that formation positions are different for each unit
        formation_positions = [tuple(unit.formation_position) for unit in self.player_squad.units]
        unique_positions = set(formation_positions)
        self.assertEqual(len(unique_positions), len(self.player_squad.units))
    
    def test_squad_combat(self):
        """Test squad combat commands"""
        # Order squad to attack enemy unit
        self.player_squad.attack_unit(self.enemy_unit)
        
        # Check that all units are targeting the enemy
        for unit in self.player_squad.units:
            self.assertEqual(unit.target, self.enemy_unit)
            # Check if the unit is in attack mode by verifying it has a target
            self.assertIsNotNone(unit.target)
    
    def test_squad_selection(self):
        """Test squad selection"""
        # Initially not selected
        self.assertFalse(self.player_squad.selected)
        
        # Select the squad
        self.player_squad.select()
        self.assertTrue(self.player_squad.selected)
        
        # Check that all units are selected
        for unit in self.player_squad.units:
            self.assertTrue(unit.selected)
        
        # Deselect the squad
        self.player_squad.deselect()
        self.assertFalse(self.player_squad.selected)
        
        # Check that all units are deselected
        for unit in self.player_squad.units:
            self.assertFalse(unit.selected)
    
    def test_unit_removal_on_death(self):
        """Test that dead units are removed from the squad"""
        initial_count = len(self.player_squad.units)
        
        # Kill a unit
        self.unit1.take_damage(self.unit1.health)
        self.assertEqual(self.unit1.state, "dead")
        
        # Update the squad to process the dead unit
        self.player_squad.update(0.1, self.game_state)
        
        # Check that the dead unit was removed
        self.assertEqual(len(self.player_squad.units), initial_count - 1)
        self.assertNotIn(self.unit1, self.player_squad.units)


if __name__ == '__main__':
    unittest.main()
