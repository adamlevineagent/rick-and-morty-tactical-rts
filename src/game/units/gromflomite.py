from typing import Tuple, Optional
import math
import numpy as np

from .unit import Unit

class Gromflomite(Unit):
    """
    Gromflomite unit - Standard insectoid soldiers of the Galactic Federation.
    Armed with energy rifles and light armor.
    """
    
    def __init__(self, position: Tuple[float, float, float], faction: str = "enemy"):
        """
        Initialize a Gromflomite soldier
        
        Args:
            position: (x, y, z) initial position
            faction: The faction this unit belongs to (typically 'enemy')
        """
        super().__init__("gromflomite", position, faction)
        
        # Override base stats with Gromflomite-specific values
        self.max_health = 100
        self.health = self.max_health
        self.speed = 4.0
        self.damage = 12
        self.attack_range = 15.0  # Ranged unit
        self.attack_speed = 1.0  # attacks per second
        
        # Special abilities
        self.can_call_reinforcements = True
        self.reinforcements_cooldown = 45.0  # seconds
        self.reinforcements_timer = 0.0
        
        # Projectile tracking
        self.projectiles = []
        
    def update(self, dt: float, game_state) -> None:
        """
        Update the Gromflomite soldier
        
        Args:
            dt: Time elapsed since last frame in seconds
            game_state: Current game state
        """
        # Update cooldowns
        if self.reinforcements_timer > 0:
            self.reinforcements_timer -= dt
            if self.reinforcements_timer <= 0:
                self.can_call_reinforcements = True
                
        # Update projectiles
        for proj in self.projectiles[:]:
            proj['lifetime'] -= dt
            if proj['lifetime'] <= 0:
                self.projectiles.remove(proj)
                continue
                
            # Move projectile
            proj['position'] = (
                proj['position'][0] + proj['velocity'][0] * dt,
                proj['position'][1] + proj['velocity'][1] * dt,
                proj['position'][2]  # Maintain height
            )
            
            # Check for collisions
            for unit in game_state.get_units():
                if unit.faction != self.faction and unit.is_alive():
                    # Simple distance check
                    dx = unit.position[0] - proj['position'][0]
                    dy = unit.position[1] - proj['position'][1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < 1.0:  # Hit radius
                        unit.take_damage(self.damage)
                        self.projectiles.remove(proj)
                        break
                
        # Call the base update method
        super().update(dt, game_state)
        
    def _update_attack(self, dt: float, game_state) -> None:
        """Override attack to implement ranged attacks"""
        # Find target
        target_unit = None
        
        # If target is a string (ID), find the unit
        if isinstance(self.target, str):
            # Search in all units
            for unit in game_state.get_units():
                if unit.id == self.target:
                    target_unit = unit
                    break
        elif hasattr(self.target, 'id'):
            # Target is already a unit
            target_unit = self.target
        
        # Target not found or is dead
        if target_unit is None or not self.is_valid_target(target_unit):
            self.state = "idle"
            self.target = None
            return
        
        # Calculate distance to target
        dx = target_unit.position[0] - self.position[0]
        dy = target_unit.position[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Update rotation to face target
        target_rotation = (math.atan2(dy, dx) * 180 / math.pi) % 360
        self.rotation = target_rotation
        self.sprite_index = int(((self.rotation + 22.5) % 360) // 45)
        
        # Check if target is in range
        if distance > self.attack_range:
            # Move toward target
            self.state = "moving"
            self.path = [target_unit.position]
            return
        
        # Attack timer
        self.attack_timer += dt
        if self.attack_timer >= 1.0 / self.attack_speed:
            self.attack_timer = 0
            
            # Fire an energy beam
            self._fire_beam(target_unit.position)
            
            # Trigger attack animation
            self.animation_frame = 0
            self.animation_timer = 0
    
    def _fire_beam(self, target_position: Tuple[float, float, float]) -> None:
        """
        Fire an energy beam at the target position
        
        Args:
            target_position: Position to fire at
        """
        # Calculate direction
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Beam speed
        speed = 30.0
        
        # Add some randomness to aim (Gromflomites aren't perfect shots)
        spread = 0.05  # Spread factor
        dx += (np.random.random() - 0.5) * spread
        dy += (np.random.random() - 0.5) * spread
        
        # Normalize direction after adding spread
        direction_length = math.sqrt(dx*dx + dy*dy)
        dx /= direction_length
        dy /= direction_length
        
        # Create projectile
        beam = {
            'position': self.position,
            'velocity': (dx * speed, dy * speed),
            'lifetime': 1.0,  # seconds
            'damage': self.damage
        }
        
        self.projectiles.append(beam)
        
    def call_reinforcements(self, game_state) -> bool:
        """
        Call for reinforcements, spawning additional Gromflomites
        
        Args:
            game_state: Current game state
            
        Returns:
            True if reinforcements were called, False if on cooldown
        """
        if not self.can_call_reinforcements:
            return False
            
        # Set cooldown
        self.can_call_reinforcements = False
        self.reinforcements_timer = self.reinforcements_cooldown
        
        # In a real implementation, this would trigger the game state to spawn
        # new Gromflomites near the caller's position
        
        # For now, just return success
        return True
    
    def render(self, renderer, camera) -> None:
        """
        Render the Gromflomite and its projectiles
        
        Args:
            renderer: Renderer object
            camera: Camera object
        """
        # Render the unit
        super().render(renderer, camera)
        
        # Render projectiles
        for proj in self.projectiles:
            # Convert projectile position to screen coordinates
            screen_pos = camera.world_to_screen(proj['position'])
            
            # Get projectile sprite
            sprite = renderer.get_projectile_sprite('energy_beam')
            
            if sprite:
                # Calculate rotation angle for the sprite
                angle = math.atan2(proj['velocity'][1], proj['velocity'][0]) * 180 / math.pi
                
                # Rotate the sprite
                rotated_sprite = pygame.transform.rotate(sprite, -angle)
                
                # Center the sprite at the projectile position
                sprite_rect = rotated_sprite.get_rect(center=screen_pos)
                
                # Draw the sprite
                renderer.screen.blit(rotated_sprite, sprite_rect)
