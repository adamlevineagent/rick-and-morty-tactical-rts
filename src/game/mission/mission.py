import json
import os
from typing import Dict, List, Tuple, Any, Optional
from game.units.unit_factory import UnitFactory

class Mission:
    """
    Represents a playable mission in the game with objectives, 
    unit placements, and win/loss conditions.
    """
    
    def __init__(self, mission_id: str, name: str, description: str):
        """
        Initialize a new mission
        
        Args:
            mission_id: Unique identifier for the mission
            name: Display name of the mission
            description: Mission description/briefing
        """
        self.mission_id = mission_id
        self.name = name
        self.description = description
        
        # Mission properties
        self.map_name = "default_map"
        self.difficulty = "normal"
        self.time_limit = 0  # 0 means no time limit
        
        # Mission state
        self.objectives = []
        self.completed_objectives = []
        self.player_squads_config = []
        self.enemy_waves = []
        self.current_wave = 0
        self.next_wave_time = 0
        
    def load_from_file(self, filepath: str) -> bool:
        """
        Load mission data from a JSON file
        
        Args:
            filepath: Path to the mission JSON file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Load basic mission info
            self.mission_id = data.get('mission_id', self.mission_id)
            self.name = data.get('name', self.name)
            self.description = data.get('description', self.description)
            self.map_name = data.get('map_name', self.map_name)
            self.difficulty = data.get('difficulty', self.difficulty)
            self.time_limit = data.get('time_limit', self.time_limit)
            
            # Load objectives
            self.objectives = data.get('objectives', [])
            
            # Load player squad configurations
            self.player_squads_config = data.get('player_squads', [])
            
            # Load enemy waves
            self.enemy_waves = data.get('enemy_waves', [])
            
            return True
        except Exception as e:
            print(f"Error loading mission file: {e}")
            return False
    
    def setup_game_state(self, game_state) -> None:
        """
        Set up the game state for this mission
        
        Args:
            game_state: GameState object to configure
        """
        # Set mission-specific game state properties
        game_state.mission_name = self.name
        game_state.game_time = 0
        game_state.time_limit = self.time_limit
        game_state.mission_objectives = self.objectives
        
        # Clear existing squads
        game_state.player_squads = []
        game_state.enemy_squads = []
        
        # Create unit factory
        unit_factory = UnitFactory()
        
        # Create player squads based on configuration
        for squad_config in self.player_squads_config:
            squad_type = squad_config.get('type', 'balanced')
            position = tuple(squad_config.get('position', (0, 0, 0)))
            size = squad_config.get('size', 5)
            name = squad_config.get('name', 'Player Squad')
            
            # Create the appropriate squad type
            if squad_type == 'balanced':
                # Create a mixed squad for balanced type
                squad = UnitFactory.create_mixed_squad(
                    position,
                    {
                        "dimensioneer": max(1, size // 3),
                        "portal_archer": max(1, size // 3),
                        "tech_grenadier": max(1, size // 3),
                    },
                    "player",
                    name
                )
            elif squad_type == 'archer':
                squad = UnitFactory.create_squad("portal_archer", position, size, "player", name)
            elif squad_type == 'grenadier':
                squad = UnitFactory.create_squad("tech_grenadier", position, size, "player", name)
            else:
                # Default to player starter squad
                squad = UnitFactory.create_player_starter_squad(position)
                squad.name = name
            
            # Add to game state
            game_state.player_squads.append(squad)
        
        # Spawn first wave of enemies if there are any
        if self.enemy_waves:
            self._spawn_enemy_wave(0, game_state, unit_factory)
            
        # Reset mission state
        self.current_wave = 0
        self.completed_objectives = []
        
    def update(self, game_state, dt: float) -> None:
        """
        Update mission state
        
        Args:
            game_state: Current game state
            dt: Time elapsed since last frame
        """
        # Check for next enemy wave
        if self.current_wave < len(self.enemy_waves) - 1:
            wave = self.enemy_waves[self.current_wave]
            trigger_type = wave.get('trigger', 'time')
            
            if trigger_type == 'time':
                # Time-based wave
                trigger_time = wave.get('trigger_time', 0)
                if game_state.game_time >= trigger_time:
                    self.current_wave += 1
                    self._spawn_enemy_wave(self.current_wave, game_state, UnitFactory())
            
            elif trigger_type == 'objective':
                # Objective-based wave
                trigger_objective = wave.get('trigger_objective', '')
                if trigger_objective in self.completed_objectives:
                    self.current_wave += 1
                    self._spawn_enemy_wave(self.current_wave, game_state, UnitFactory())
                    
            elif trigger_type == 'enemies_defeated':
                # Wave triggered when all enemies are defeated
                if len(game_state.enemy_squads) == 0:
                    self.current_wave += 1
                    self._spawn_enemy_wave(self.current_wave, game_state, UnitFactory())
        
        # Check objectives
        self._update_objectives(game_state)
        
    def _spawn_enemy_wave(self, wave_index: int, game_state, unit_factory) -> None:
        """
        Spawn an enemy wave
        
        Args:
            wave_index: Index of the wave to spawn
            game_state: Current game state
            unit_factory: UnitFactory instance
        """
        if wave_index >= len(self.enemy_waves):
            return
            
        wave = self.enemy_waves[wave_index]
        squads = wave.get('squads', [])
        
        for squad_config in squads:
            squad_type = squad_config.get('type', 'gromflomite')
            position = tuple(squad_config.get('position', (0, 0, 0)))
            size = squad_config.get('size', 5)
            name = squad_config.get('name', f'Enemy {wave_index + 1}')
            
            # Create the appropriate squad type using the static method
            squad = UnitFactory.create_squad("gromflomite", position, size, "enemy", name)
            
            # Add to game state
            game_state.enemy_squads.append(squad)
    
    def _update_objectives(self, game_state) -> None:
        """
        Update mission objectives
        
        Args:
            game_state: Current game state
        """
        for objective in self.objectives:
            if objective['id'] in self.completed_objectives:
                continue
                
            objective_type = objective.get('type')
            
            if objective_type == 'defeat_all':
                # Check if all enemies are defeated
                if len(game_state.enemy_squads) == 0:
                    self.completed_objectives.append(objective['id'])
                    
            elif objective_type == 'survive_time':
                # Check if player survived for the required time
                required_time = objective.get('time', 0)
                if game_state.game_time >= required_time:
                    self.completed_objectives.append(objective['id'])
                    
            elif objective_type == 'reach_position':
                # Check if any player unit reached the target position
                target_pos = tuple(objective.get('position', (0, 0, 0)))
                radius = objective.get('radius', 10)
                
                # Check if any player unit is within range of the target
                for squad in game_state.player_squads:
                    for unit in squad.units:
                        dx = unit.position[0] - target_pos[0]
                        dy = unit.position[1] - target_pos[1]
                        distance = (dx*dx + dy*dy) ** 0.5
                        
                        if distance <= radius:
                            self.completed_objectives.append(objective['id'])
                            break
    
    def check_win_condition(self, game_state) -> bool:
        """
        Check if the mission win condition is met
        
        Args:
            game_state: Current game state
            
        Returns:
            True if mission is won, False otherwise
        """
        # Check if all mandatory objectives are completed
        for objective in self.objectives:
            if objective.get('mandatory', True) and objective['id'] not in self.completed_objectives:
                return False
        
        return True
    
    def check_loss_condition(self, game_state) -> bool:
        """
        Check if the mission loss condition is met
        
        Args:
            game_state: Current game state
            
        Returns:
            True if mission is lost, False otherwise
        """
        # Check if all player units are defeated
        if len(game_state.player_squads) == 0:
            return True
            
        # Check if time limit is exceeded (if there is one)
        if self.time_limit > 0 and game_state.game_time >= self.time_limit:
            return True
            
        return False
