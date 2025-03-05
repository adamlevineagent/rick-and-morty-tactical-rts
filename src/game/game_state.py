import pygame
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import random

from .units import UnitFactory, Squad, FormationType

class GameState:
    """
    The GameState class manages the current state of the game, including:
    - Units (player and enemy)
    - Terrain
    - Mission objectives
    - Game time and progression
    """
    
    def __init__(self, mission_mode=False):
        """
        Initialize a new game state
        
        Args:
            mission_mode: If True, don't create test units (mission will populate)
        """
        # Game state variables
        self.game_time = 0  # Total game time in seconds
        self.mission_name = "Test Mission"
        self.mission_objectives = []
        self.time_limit = 0  # 0 means no time limit
        self.mission_complete = False
        self.mission_failed = False
        
        # Terrain data
        self.terrain_size = 2000  # Size of the terrain in world units
        self.terrain_heightmap = self._generate_test_heightmap()
        
        # Squad lists
        self.player_squads = []
        self.enemy_squads = []
        
        # Selected squads and units
        self.selected_squads = []
        self.selected_units = []
        
        # Game object lists
        self.projectiles = []
        self.explosions = []
        self.debris = []
        
        # Create test units and squads if not in mission mode
        if not mission_mode:
            self._create_test_units()
    
    def _generate_test_heightmap(self):
        """Generate a simple heightmap for testing"""
        size = 100  # Size of heightmap grid
        heightmap = np.zeros((size, size))
        
        # Create some random terrain features
        for _ in range(5):
            # Random hill
            x = np.random.randint(10, size - 10)
            y = np.random.randint(10, size - 10)
            radius = np.random.randint(5, 15)
            height = np.random.uniform(3.0, 10.0)
            
            # Create a hill using a radial function
            for i in range(max(0, x - radius), min(size, x + radius)):
                for j in range(max(0, y - radius), min(size, y + radius)):
                    distance = np.sqrt((i - x) ** 2 + (j - y) ** 2)
                    if distance < radius:
                        # Smooth falloff
                        factor = (1 - distance / radius) ** 2
                        heightmap[i, j] += height * factor
        
        return heightmap
    
    def _create_test_units(self):
        """Create test squads and units using the UnitFactory"""
        # Create player squads
        dimensioneer_squad = UnitFactory.create_squad(
            "dimensioneer", 
            (-50, -20),
            6, 
            "player", 
            "Dimensioneer Squad Alpha"
        )
        self.player_squads.append(dimensioneer_squad)
        
        archer_squad = UnitFactory.create_squad(
            "portal_archer", 
            (-20, -60),
            2, 
            "player", 
            "Portal Archer Squad Beta"
        )
        self.player_squads.append(archer_squad)
        
        grenadier_squad = UnitFactory.create_squad(
            "tech_grenadier", 
            (0, -30),
            1, 
            "player", 
            "Tech Grenadier Squad Gamma"
        )
        self.player_squads.append(grenadier_squad)
        
        # Create a mixed player squad
        mixed_squad = UnitFactory.create_mixed_squad(
            (30, -40),
            {
                "dimensioneer": 2,
                "portal_archer": 2,
                "tech_grenadier": 1
            },
            "player",
            "Rick's Elite Team"
        )
        self.player_squads.append(mixed_squad)
        
        # Create enemy squads
        for i in range(2):
            enemy_squad = UnitFactory.create_squad(
                "gromflomite",
                (100 + i * 50, 100 + i * 30),
                4,
                "enemy",
                f"Federation Patrol {i+1}"
            )
            self.enemy_squads.append(enemy_squad)
    
    def get_terrain_height(self, x, y):
        """
        Get the height of the terrain at the specified world coordinates
        
        Args:
            x, y: World coordinates
            
        Returns:
            Height in world units
        """
        # Convert world coordinates to heightmap indices
        size = self.terrain_heightmap.shape[0]
        terrain_scale = self.terrain_size / size
        
        # Map coordinates to heightmap indices
        i = int((x + self.terrain_size / 2) / terrain_scale)
        j = int((y + self.terrain_size / 2) / terrain_scale)
        
        # Clamp to valid range
        i = max(0, min(size - 1, i))
        j = max(0, min(size - 1, j))
        
        return self.terrain_heightmap[i, j]
    
    def get_all_player_units(self):
        """Get a flat list of all player units from all squads"""
        all_units = []
        for squad in self.player_squads:
            all_units.extend(squad.units)
        return all_units
    
    def get_all_enemy_units(self):
        """Get a flat list of all enemy units from all squads"""
        all_units = []
        for squad in self.enemy_squads:
            all_units.extend(squad.units)
        return all_units
    
    def handle_selection(self, start_pos, end_pos, screen_to_world_func):
        """
        Handle unit selection based on screen coordinates
        
        Args:
            start_pos: Screen coordinates of selection start
            end_pos: Screen coordinates of selection end
            screen_to_world_func: Function to convert screen to world coordinates
        """
        # Clear current selection
        self.selected_squads = []
        self.selected_units = []
        
        # Convert screen coordinates to world coordinates
        start_world = screen_to_world_func(start_pos[0], start_pos[1])
        end_world = screen_to_world_func(end_pos[0], end_pos[1])
        
        # Create selection rectangle
        min_x = min(start_world[0], end_world[0])
        max_x = max(start_world[0], end_world[0])
        min_y = min(start_world[1], end_world[1])
        max_y = max(start_world[1], end_world[1])
        
        # Check each player unit
        selected_by_squad = {}
        
        for squad in self.player_squads:
            selected_in_squad = []
            
            for unit in squad.units:
                pos = unit.position
                if min_x <= pos[0] <= max_x and min_y <= pos[1] <= max_y:
                    self.selected_units.append(unit)
                    selected_in_squad.append(unit)
            
            # If all units in squad are selected, add the squad to selected_squads
            if len(selected_in_squad) == len(squad.units) and len(squad.units) > 0:
                self.selected_squads.append(squad)
            elif selected_in_squad:
                selected_by_squad[squad] = selected_in_squad
                
        print(f"Selected {len(self.selected_units)} units in {len(self.selected_squads)} squads")
        
        # Return the selection information for UI feedback
        return {
            'units': self.selected_units,
            'squads': self.selected_squads,
            'partial_squads': selected_by_squad
        }
    
    def handle_unit_command(self, target_pos, command_type, screen_to_world_func):
        """
        Issue a command to the selected units or squads
        
        Args:
            target_pos: Screen coordinates of the target
            command_type: Type of command (move, attack, etc.)
            screen_to_world_func: Function to convert screen to world coordinates
        """
        # Convert target position to world coordinates
        target_world = screen_to_world_func(target_pos[0], target_pos[1])
        target_position = (target_world[0], target_world[1])
        
        # If we have selected squads, command them
        if self.selected_squads:
            for squad in self.selected_squads:
                if command_type == "move":
                    squad.move_to(target_position)
                elif command_type == "attack":
                    # Find the closest enemy unit to the target position
                    closest_enemy = None
                    min_distance = float('inf')
                    
                    for enemy_squad in self.enemy_squads:
                        for enemy in enemy_squad.units:
                            dx = enemy.position[0] - target_position[0]
                            dy = enemy.position[1] - target_position[1]
                            distance = np.sqrt(dx*dx + dy*dy)
                            
                            if distance < min_distance:
                                min_distance = distance
                                closest_enemy = enemy
                    
                    if closest_enemy:
                        squad.attack_target(closest_enemy)
                elif command_type == "formation":
                    # Cycle through formations
                    formations = list(FormationType)
                    current_index = formations.index(squad.formation_type)
                    next_index = (current_index + 1) % len(formations)
                    squad.set_formation(formations[next_index])
        
        # For individually selected units (not in a selected squad)
        else:
            # Group selected units by their squad
            units_by_squad = {}
            for unit in self.selected_units:
                # Find which squad this unit belongs to
                for squad in self.player_squads:
                    if unit in squad.units:
                        if squad not in units_by_squad:
                            units_by_squad[squad] = []
                        units_by_squad[squad].append(unit)
                        break
            
            # Command each unit individually
            for unit in self.selected_units:
                if command_type == "move":
                    unit.move_to(target_position)
                elif command_type == "attack":
                    # Find closest enemy
                    closest_enemy = None
                    min_distance = float('inf')
                    
                    for enemy_squad in self.enemy_squads:
                        for enemy in enemy_squad.units:
                            dx = enemy.position[0] - target_position[0]
                            dy = enemy.position[1] - target_position[1]
                            distance = np.sqrt(dx*dx + dy*dy)
                            
                            if distance < min_distance:
                                min_distance = distance
                                closest_enemy = enemy
                    
                    if closest_enemy:
                        unit.attack_target(closest_enemy)
    
    def update(self, dt):
        """
        Update the game state
        
        Args:
            dt: Time delta in seconds
        """
        # Update game time
        self.game_time += dt
        
        # Check time limit
        if self.time_limit > 0 and self.game_time >= self.time_limit:
            self.mission_failed = True
        
        # Update all player squads
        for squad in self.player_squads:
            squad.update(dt, self)
        
        # Update all enemy squads
        for squad in self.enemy_squads:
            # Simple AI for enemy squads
            if random.random() < 0.01:  # 1% chance per frame to issue new order
                # Random movement in their area
                new_x = squad.position[0] + random.uniform(-40, 40)
                new_y = squad.position[1] + random.uniform(-40, 40)
                squad.move_to((new_x, new_y))
                
                # 10% chance to attack a random player unit if nearby
                if random.random() < 0.1:
                    all_player_units = self.get_all_player_units()
                    if all_player_units:
                        # Pick a random player unit to target
                        target_unit = random.choice(all_player_units)
                        dx = target_unit.position[0] - squad.position[0]
                        dy = target_unit.position[1] - squad.position[1]
                        distance = np.sqrt(dx*dx + dy*dy)
                        
                        # Only attack if within reasonable distance
                        if distance < 200:
                            squad.attack_target(target_unit)
            
            # Update squad
            squad.update(dt, self)
        
        # Check if all player squads are defeated
        if len(self.player_squads) == 0:
            self.mission_failed = True
        
        # Check if all enemy squads are defeated
        if len(self.enemy_squads) == 0 and self.mission_objectives:
            # This is a simple win condition - more complex ones would be handled by the mission system
            self.mission_complete = True
    
    def _update_squads_and_units(self, dt):
        """
        Update all squads and units
        
        Args:
            dt: Time elapsed since last frame in seconds
        """
        # Update player squads
        for squad in self.player_squads:
            squad.update(dt)
        
        # Update enemy squads
        for squad in self.enemy_squads:
            # Simple AI for enemy squads
            if random.random() < 0.01:  # 1% chance per frame to issue new order
                # Random movement in their area
                new_x = squad.position[0] + random.uniform(-40, 40)
                new_y = squad.position[1] + random.uniform(-40, 40)
                squad.move_to((new_x, new_y))
                
                # 10% chance to attack a random player unit if nearby
                if random.random() < 0.1:
                    all_player_units = self.get_all_player_units()
                    if all_player_units:
                        # Pick a random player unit to target
                        target_unit = random.choice(all_player_units)
                        dx = target_unit.position[0] - squad.position[0]
                        dy = target_unit.position[1] - squad.position[1]
                        distance = np.sqrt(dx*dx + dy*dy)
                        
                        # Only attack if within reasonable distance
                        if distance < 200:
                            squad.attack_target(target_unit)
            
            # Update squad
            squad.update(dt)
    
    def _update_game_objects(self, dt):
        """
        Update projectiles, explosions and other game objects
        
        Args:
            dt: Time elapsed since last frame in seconds
        """
        # Note: Will be implemented later when we add projectile and effect classes
        pass
