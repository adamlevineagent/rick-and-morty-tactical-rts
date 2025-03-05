import pygame
import numpy as np
from enum import Enum
from typing import List, Tuple, Optional
import math

# Import Unit class (assuming it exists in the same directory)
from .unit import Unit

class FormationType(Enum):
    """Enumeration of available formation types for squads."""
    LINE = 1
    WEDGE = 2
    COLUMN = 3
    SCATTERED = 4
    CIRCLE = 5

class Squad:
    """
    Represents a group of units that move and act together.
    Manages unit formations and issues commands to individual units.
    """
    
    def __init__(self, name: str, faction: str, position: Tuple[float, float]):
        """
        Initialize a new squad.
        
        Args:
            name: The name of the squad
            faction: The faction this squad belongs to (e.g., 'player', 'enemy')
            position: The (x, y) position of the squad's center
        """
        self.name = name
        self.faction = faction
        self.position = list(position)
        self.units: List[Unit] = []
        self.selected = False
        self.formation = FormationType.LINE
        self.formation_spacing = 30  # Spacing between units in formation
        self.formation_width = 5     # Maximum units in a row for line formation
        self.target_position = None
        self.waypoints = []
        self.auto_attack = True      # Whether units auto-attack nearby enemies
        self.alert_status = "normal" # normal, defensive, aggressive
        
    def add_unit(self, unit: Unit) -> None:
        """Add a unit to the squad."""
        self.units.append(unit)
        unit.squad = self
        self._update_formation()
        
    def remove_unit(self, unit: Unit) -> None:
        """Remove a unit from the squad."""
        if unit in self.units:
            self.units.remove(unit)
            unit.squad = None
            self._update_formation()
    
    def move_to(self, target_position: Tuple[float, float]) -> None:
        """
        Command the squad to move to a target position.
        
        Args:
            target_position: The (x, y) coordinates to move to
        """
        self.target_position = list(target_position)
        self.waypoints = [self.target_position]  # Simple direct path for now
        self._update_formation()
        
        # Issue movement commands to individual units
        for i, unit in enumerate(self.units):
            if hasattr(unit, 'formation_position') and unit.formation_position:
                unit.move_to(unit.formation_position)
    
    def set_formation(self, formation_type: FormationType) -> None:
        """Change the squad's formation."""
        self.formation = formation_type
        self._update_formation()
        
        # If the squad has a target position, reissue movement commands
        if self.target_position:
            self.move_to(self.target_position)
    
    def attack_target(self, target_position: Tuple[float, float]) -> None:
        """
        Command the squad to attack at a specified position.
        
        Args:
            target_position: The (x, y) coordinates to attack
        """
        # First move to a position from which units can attack
        self.move_to(target_position)
        
        # Then set each unit to attack mode
        for unit in self.units:
            unit.set_attack_mode(True)
    
    def attack_unit(self, target_unit: Unit) -> None:
        """
        Command the squad to attack a specific unit.
        
        Args:
            target_unit: The Unit object to attack
        """
        # Each unit in the squad will target the specified unit
        for unit in self.units:
            unit.set_target(target_unit)
            unit.set_attack_mode(True)
    
    def select(self) -> None:
        """Select this squad."""
        self.selected = True
        for unit in self.units:
            unit.selected = True
    
    def deselect(self) -> None:
        """Deselect this squad."""
        self.selected = False
        for unit in self.units:
            unit.selected = False
    
    def is_empty(self) -> bool:
        """Check if the squad has no units."""
        return len(self.units) == 0
    
    def update(self, delta_time: float, game_state) -> None:
        """
        Update the squad and all its units.
        
        Args:
            delta_time: Time elapsed since last update in seconds
            game_state: Current game state object containing global state
        """
        # Remove dead units
        self.units = [unit for unit in self.units if unit.is_alive()]
        
        # Update squad position to be the average of unit positions
        if self.units:
            avg_pos_x = sum(unit.position[0] for unit in self.units) / len(self.units)
            avg_pos_y = sum(unit.position[1] for unit in self.units) / len(self.units)
            self.position = [avg_pos_x, avg_pos_y]
        
        # Update each unit
        for unit in self.units:
            unit.update(delta_time, game_state)
        
        # Check if squad reached waypoint
        if self.waypoints and self.units:
            waypoint = self.waypoints[0]
            
            # Calculate distance to current waypoint
            distance = math.sqrt(
                (self.position[0] - waypoint[0])**2 + 
                (self.position[1] - waypoint[1])**2
            )
            
            # If close enough to waypoint, move to next waypoint
            if distance < 50:  # Threshold distance
                self.waypoints.pop(0)
                if self.waypoints:
                    self.move_to(self.waypoints[0])
                else:
                    # Final destination reached, maintain formation
                    self._update_formation()
    
    def render(self, renderer, camera) -> None:
        """
        Render the squad and its units.
        
        Args:
            renderer: The renderer object
            camera: The camera object for view transformations
        """
        # Render each unit
        for unit in self.units:
            unit.render(renderer, camera)
        
        # If selected, render squad selection indicator
        if self.selected:
            # Calculate a rectangle that encompasses all units
            min_x = min(unit.position[0] for unit in self.units) if self.units else self.position[0]
            min_y = min(unit.position[1] for unit in self.units) if self.units else self.position[1]
            max_x = max(unit.position[0] for unit in self.units) if self.units else self.position[0]
            max_y = max(unit.position[1] for unit in self.units) if self.units else self.position[1]
            
            # Add padding
            padding = 10
            min_x -= padding
            min_y -= padding
            max_x += padding
            max_y += padding
            
            # Draw selection rectangle
            screen_min = camera.world_to_screen((min_x, min_y))
            screen_max = camera.world_to_screen((max_x, max_y))
            rect = pygame.Rect(
                screen_min[0], 
                screen_min[1], 
                screen_max[0] - screen_min[0], 
                screen_max[1] - screen_min[1]
            )
            pygame.draw.rect(renderer.screen, (0, 255, 0), rect, 2)
    
    def _update_formation(self) -> None:
        """Update unit positions to maintain formation."""
        if not self.units:
            return
            
        # Get target position (use current position if no target)
        target = self.target_position if self.target_position else self.position
            
        if self.formation == FormationType.LINE:
            self._form_line(target)
        elif self.formation == FormationType.WEDGE:
            self._form_wedge(target)
        elif self.formation == FormationType.COLUMN:
            self._form_column(target)
        elif self.formation == FormationType.SCATTERED:
            self._form_scattered(target)
        elif self.formation == FormationType.CIRCLE:
            self._form_circle(target)
    
    def _form_line(self, target: List[float]) -> None:
        """Arrange units in a line formation."""
        num_units = len(self.units)
        if num_units == 0:
            return
            
        # Determine number of rows and units per row
        if num_units <= self.formation_width:
            units_per_row = num_units
            rows = 1
        else:
            units_per_row = self.formation_width
            rows = (num_units + units_per_row - 1) // units_per_row
        
        # Calculate total width and height
        total_width = (units_per_row - 1) * self.formation_spacing
        total_height = (rows - 1) * self.formation_spacing
        
        # Calculate direction vector (from squad to target)
        direction = [
            target[0] - self.position[0],
            target[1] - self.position[1]
        ]
        
        # Normalize direction
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        if length > 0:
            direction[0] /= length
            direction[1] /= length
        else:
            direction = [0, 1]  # Default direction if squad is at target
        
        # Calculate perpendicular vector for line width
        perp = [-direction[1], direction[0]]
        
        for i, unit in enumerate(self.units):
            row = i // units_per_row
            col = i % units_per_row
            
            # Center the units in each row
            units_in_this_row = min(units_per_row, num_units - row * units_per_row)
            row_width = (units_in_this_row - 1) * self.formation_spacing
            offset = (total_width - row_width) / 2 if units_per_row > units_in_this_row else 0
            
            # Calculate position relative to formation center
            rel_x = (col * self.formation_spacing - row_width / 2) + offset
            rel_y = row * self.formation_spacing - total_height / 2
            
            # Calculate position in world space
            unit.formation_position = [
                target[0] + rel_x * perp[0] + rel_y * direction[0],
                target[1] + rel_x * perp[1] + rel_y * direction[1]
            ]
    
    def _form_wedge(self, target: List[float]) -> None:
        """Arrange units in a wedge formation."""
        num_units = len(self.units)
        if num_units == 0:
            return
            
        # Calculate direction vector
        direction = [
            target[0] - self.position[0],
            target[1] - self.position[1]
        ]
        
        # Normalize direction
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        if length > 0:
            direction[0] /= length
            direction[1] /= length
        else:
            direction = [0, 1]  # Default direction
        
        # Calculate perpendicular vector for wedge width
        perp = [-direction[1], direction[0]]
        
        # Leader is at the front
        leader_idx = 0
        
        for i, unit in enumerate(self.units):
            if i == leader_idx:
                # Leader position
                rel_x = 0
                rel_y = 0
            else:
                # Calculate which side of the wedge this unit belongs to
                side = 1 if (i % 2 == 1) else -1
                
                # Calculate position in the wedge
                row = (i - 1) // 2 + 1
                rel_x = side * row * self.formation_spacing * 0.8
                rel_y = row * self.formation_spacing * 0.8
            
            # Calculate position in world space
            unit.formation_position = [
                target[0] + rel_x * perp[0] + rel_y * direction[0],
                target[1] + rel_x * perp[1] + rel_y * direction[1]
            ]
    
    def _form_column(self, target: List[float]) -> None:
        """Arrange units in a column formation."""
        num_units = len(self.units)
        if num_units == 0:
            return
            
        # Calculate direction vector
        direction = [
            target[0] - self.position[0],
            target[1] - self.position[1]
        ]
        
        # Normalize direction
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        if length > 0:
            direction[0] /= length
            direction[1] /= length
        else:
            direction = [0, 1]  # Default direction
        
        # Units per column (typically 1 for a single-file column)
        units_per_col = 2
        
        # Calculate total column length
        total_length = (num_units // units_per_col) * self.formation_spacing
        if num_units % units_per_col > 0:
            total_length += self.formation_spacing
        
        # Calculate perpendicular vector for column width
        perp = [-direction[1], direction[0]]
        
        for i, unit in enumerate(self.units):
            col = i // units_per_col
            row = i % units_per_col
            
            # Calculate position relative to formation center
            rel_x = (row - 0.5) * self.formation_spacing if units_per_col > 1 else 0
            rel_y = col * self.formation_spacing - total_length / 2
            
            # Calculate position in world space
            unit.formation_position = [
                target[0] + rel_x * perp[0] + rel_y * direction[0],
                target[1] + rel_x * perp[1] + rel_y * direction[1]
            ]
    
    def _form_scattered(self, target: List[float]) -> None:
        """Arrange units in a scattered formation."""
        num_units = len(self.units)
        if num_units == 0:
            return
            
        # Radius of scattered formation
        radius = self.formation_spacing * math.sqrt(num_units) * 0.5
        
        for i, unit in enumerate(self.units):
            # Calculate random offset within a circle
            angle = 2 * math.pi * (i / num_units)
            distance = radius * math.sqrt(np.random.random())
            
            rel_x = distance * math.cos(angle)
            rel_y = distance * math.sin(angle)
            
            # Calculate position in world space
            unit.formation_position = [
                target[0] + rel_x,
                target[1] + rel_y
            ]
    
    def _form_circle(self, target: List[float]) -> None:
        """Arrange units in a circle formation."""
        num_units = len(self.units)
        if num_units == 0:
            return
            
        # Radius of circle formation
        radius = self.formation_spacing * 2
        
        for i, unit in enumerate(self.units):
            # Calculate position on circle
            angle = 2 * math.pi * (i / num_units)
            
            rel_x = radius * math.cos(angle)
            rel_y = radius * math.sin(angle)
            
            # Calculate position in world space
            unit.formation_position = [
                target[0] + rel_x,
                target[1] + rel_y
            ]
