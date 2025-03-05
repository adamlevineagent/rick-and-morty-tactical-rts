from typing import Tuple, Optional
import math
import numpy as np

from .unit import Unit

class Dimensioneer(Unit):
    """
    Dimensioneer unit - Rick and Morty universe's equivalent of a melee warrior.
    Equipped with a portal-enhanced melee weapon that can cut through dimensions.
    """
    
    def __init__(self, position: Tuple[float, float, float], faction: str = "player"):
        """
        Initialize a Dimensioneer unit
        
        Args:
            position: (x, y, z) initial position
            faction: The faction this unit belongs to (player, enemy)
        """
        super().__init__("dimensioneer", position, faction)
        
        # Override base stats with Dimensioneer-specific values
        self.max_health = 150
        self.health = self.max_health
        self.speed = 4.5
        self.damage = 25
        self.attack_range = 2.0
        self.attack_speed = 1.2  # attacks per second
        
        # Special abilities
        self.can_dimension_slash = True
        self.dimension_slash_cooldown = 15.0  # seconds
        self.dimension_slash_timer = 0.0
        self.dimension_slash_damage = 50
        self.dimension_slash_range = 5.0
        
    def update(self, dt: float, game_state) -> None:
        """
        Update the Dimensioneer unit
        
        Args:
            dt: Time elapsed since last frame in seconds
            game_state: Current game state
        """
        # Update cooldowns
        if self.dimension_slash_timer > 0:
            self.dimension_slash_timer -= dt
            if self.dimension_slash_timer <= 0:
                self.can_dimension_slash = True
                
        # Call the base update method
        super().update(dt, game_state)
        
    def dimension_slash(self, target_position: Tuple[float, float, float]) -> bool:
        """
        Perform a dimension slash special attack
        
        Args:
            target_position: Position to target with the slash
            
        Returns:
            True if the ability was used, False if on cooldown
        """
        if not self.can_dimension_slash:
            return False
            
        # Calculate direction vector
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Set cooldown
        self.can_dimension_slash = False
        self.dimension_slash_timer = self.dimension_slash_cooldown
        
        # The actual effect would be implemented in the game state
        # For now, we just return success
        return True
        
    def take_damage(self, damage: float) -> None:
        """
        Apply damage to the Dimensioneer, with chance to dodge
        
        Args:
            damage: Amount of damage to apply
        """
        # Dimensioneers have a small chance to dodge attacks
        if np.random.random() < 0.1:  # 10% dodge chance
            # Dodge successful
            return
            
        # Apply damage normally if dodge fails
        super().take_damage(damage)
