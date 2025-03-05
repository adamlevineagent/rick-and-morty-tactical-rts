import os
import pygame
import random

class AssetManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.assets = {
            'units': {},
            'environment': {},
            'ui': {}
        }
        self.load_assets()
        
    def load_assets(self):
        """Load all assets from the assets directory"""
        # Load unit assets
        unit_path = os.path.join(self.base_path, 'assets', 'images', 'units')
        self.load_assets_from_directory(unit_path, 'units')
        
        # Load environment assets
        env_path = os.path.join(self.base_path, 'assets', 'images', 'environment')
        self.load_assets_from_directory(env_path, 'environment')
        
        # Load UI assets
        ui_path = os.path.join(self.base_path, 'assets', 'images', 'ui')
        self.load_assets_from_directory(ui_path, 'ui')
        
        print(f"Loaded {len(self.assets['units'])} unit assets")
        print(f"Loaded {len(self.assets['environment'])} environment assets")
        print(f"Loaded {len(self.assets['ui'])} UI assets")
    
    def load_assets_from_directory(self, directory, asset_type):
        """Load all image assets from a directory"""
        if not os.path.exists(directory):
            print(f"Warning: Asset directory {directory} does not exist")
            return
            
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                try:
                    asset_path = os.path.join(directory, filename)
                    asset_name = os.path.splitext(filename)[0]
                    self.assets[asset_type][asset_name] = pygame.image.load(asset_path).convert_alpha()
                except pygame.error as e:
                    print(f"Could not load asset {filename}: {e}")
    
    def get_asset(self, asset_type, asset_name):
        """Get an asset by type and name"""
        if asset_type not in self.assets:
            print(f"Warning: Asset type {asset_type} does not exist")
            return None
            
        if asset_name not in self.assets[asset_type]:
            print(f"Warning: Asset {asset_name} does not exist in {asset_type}")
            return None
            
        return self.assets[asset_type][asset_name]
    
    def get_random_unit_asset(self, unit_type):
        """Get a random unit asset for a specific unit type"""
        matching_assets = []
        
        # Define mapping between unit types and asset patterns
        unit_patterns = {
            'portal_archer': ['scifiUnit_0', 'scifiUnit_1'],
            'dimensioneer': ['scifiUnit_2', 'scifiUnit_3'],
            'generic': ['scifiUnit']
        }
        
        pattern = unit_patterns.get(unit_type, unit_patterns['generic'])
        
        for asset_name in self.assets['units']:
            if any(asset_name.startswith(p) for p in pattern):
                matching_assets.append(asset_name)
        
        if not matching_assets:
            # If no matching assets, return a random unit asset
            matching_assets = list(self.assets['units'].keys())
        
        if matching_assets:
            return self.get_asset('units', random.choice(matching_assets))
        
        return None
    
    def get_ui_element(self, element_type):
        """Get a UI element by type (button, panel, bar, etc.)"""
        element_types = {
            'button': 'button_square_header_small_square',
            'button_large': 'button_square_header_large_square',
            'panel': 'metalPanel',
            'panel_blue': 'metalPanel_blue',
            'panel_corner': 'metalPanel_blueCorner',
            'bar_h': 'barHorizontal_blue_mid',
            'bar_h_left': 'barHorizontal_blue_left',
            'bar_h_right': 'barHorizontal_blue_right',
            'bar_v': 'barVertical_blue_mid',
            'bar_v_top': 'barVertical_blue_top',
            'bar_v_bottom': 'barVertical_blue_bottom',
        }
        
        asset_name = element_types.get(element_type)
        if asset_name:
            return self.get_asset('ui', asset_name)
        
        return None
    
    def get_environment_asset(self, env_type):
        """Get an environment asset by type"""
        env_patterns = {
            'obstacle': ['scifiEnvironment_0'],
            'decoration': ['scifiEnvironment_1'],
            'generic': ['scifiEnvironment']
        }
        
        pattern = env_patterns.get(env_type, env_patterns['generic'])
        matching_assets = []
        
        for asset_name in self.assets['environment']:
            if any(asset_name.startswith(p) for p in pattern):
                matching_assets.append(asset_name)
        
        if matching_assets:
            return self.get_asset('environment', random.choice(matching_assets))
        
        return None
