import os
import sys
import unittest
import pygame

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the AssetManager
from engine.asset_manager import AssetManager

class TestAssetManager(unittest.TestCase):
    """Test the AssetManager class"""
    
    def setUp(self):
        """Set up for the tests"""
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Get the base path
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        # Create the AssetManager
        self.asset_manager = AssetManager(self.base_path)
    
    def tearDown(self):
        """Clean up after the tests"""
        pygame.quit()
    
    def test_asset_manager_initialization(self):
        """Test that the AssetManager initializes properly"""
        # Check that the assets were loaded
        self.assertIsInstance(self.asset_manager.assets, dict)
        self.assertIn('units', self.asset_manager.assets)
        self.assertIn('environment', self.asset_manager.assets)
        self.assertIn('ui', self.asset_manager.assets)
    
    def test_get_asset(self):
        """Test getting assets"""
        # Try to get a unit asset (we know scifiUnit_01 exists)
        unit_asset = self.asset_manager.get_asset('units', 'scifiUnit_01')
        if len(self.asset_manager.assets['units']) > 0:
            self.assertIsNotNone(unit_asset, "Failed to get unit asset")
        
        # Try to get a ui asset (we know metalPanel_blue exists)
        ui_asset = self.asset_manager.get_asset('ui', 'metalPanel_blue')
        if len(self.asset_manager.assets['ui']) > 0:
            self.assertIsNotNone(ui_asset, "Failed to get UI asset")
    
    def test_get_random_unit_asset(self):
        """Test getting a random unit asset"""
        if len(self.asset_manager.assets['units']) > 0:
            # Get a random asset for a portal archer
            portal_archer_asset = self.asset_manager.get_random_unit_asset('portal_archer')
            self.assertIsNotNone(portal_archer_asset, "Failed to get Portal Archer asset")
            
            # Get a random asset for a dimensioneer
            dimensioneer_asset = self.asset_manager.get_random_unit_asset('dimensioneer')
            self.assertIsNotNone(dimensioneer_asset, "Failed to get Dimensioneer asset")
            
            # Get a random asset for a generic unit
            generic_asset = self.asset_manager.get_random_unit_asset('generic')
            self.assertIsNotNone(generic_asset, "Failed to get generic unit asset")
    
    def test_get_ui_element(self):
        """Test getting UI elements"""
        if len(self.asset_manager.assets['ui']) > 0:
            # Get button UI element
            button = self.asset_manager.get_ui_element('button')
            self.assertIsNotNone(button, "Failed to get button UI element")
            
            # Get panel UI element
            panel = self.asset_manager.get_ui_element('panel')
            self.assertIsNotNone(panel, "Failed to get panel UI element")
    
    def test_get_environment_asset(self):
        """Test getting environment assets"""
        if len(self.asset_manager.assets['environment']) > 0:
            # Get obstacle environment asset
            obstacle = self.asset_manager.get_environment_asset('obstacle')
            self.assertIsNotNone(obstacle, "Failed to get obstacle environment asset")
            
            # Get decoration environment asset
            decoration = self.asset_manager.get_environment_asset('decoration')
            self.assertIsNotNone(decoration, "Failed to get decoration environment asset")


if __name__ == '__main__':
    unittest.main()
