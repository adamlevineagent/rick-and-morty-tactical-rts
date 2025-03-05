from typing import Tuple, List, Optional
import math
import numpy as np

from .unit import Unit

class PortalArcher(Unit):
    """
    Portal Archer unit - Rick and Morty universe's equivalent of ranged archers.
    Shoots arrows through mini-portals that can bypass obstacles and hit targets from unexpected angles.
    """
    
    def __init__(self, position: Tuple[float, float, float], faction: str = "player"):
        """
        Initialize a Portal Archer unit
        
        Args:
            position: (x, y, z) initial position
            faction: The faction this unit belongs to (player, enemy)
        """
        super().__init__("portal_archer", position, faction)
        
        # Override base stats with Portal Archer specific values
        self.max_health = 90
        self.health = self.max_health
        self.speed = 5.0
        self.damage = 15
        self.attack_range = 18.0  # Long range
        self.attack_speed = 0.8  # attacks per second (slower than melee)
        self.is_ranged = True  # This is a ranged unit
        
        # Knockback settings
        self.knockback_power = 0.0  # No knockback on ranged attacks
        self.knockback_resistance = 0.1  # Low resistance to being knocked back
        self.knockback_recovery = 1.5  # Slow recovery from knockback
        
        # Special abilities
        self.can_portal_volley = True
        self.portal_volley_cooldown = 20.0  # seconds
        self.portal_volley_timer = 0.0
        self.portal_volley_arrows = 5
        self.portal_volley_spread = 30  # degrees
        
        # Projectile tracking
        self.projectiles: List = []  # Will store active projectiles
        
    def update(self, dt: float, game_state) -> None:
        """
        Update the Portal Archer unit
        
        Args:
            dt: Time elapsed since last frame in seconds
            game_state: Current game state
        """
        # Update cooldowns
        if self.portal_volley_timer > 0:
            self.portal_volley_timer -= dt
            if self.portal_volley_timer <= 0:
                self.can_portal_volley = True
                
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
            
            # Check for collisions (in a real implementation, this would be handled by the physics engine)
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
            
            # Fire an arrow
            self._fire_arrow(target_unit.position)
            
            # Trigger attack animation
            self.animation_frame = 0
            self.animation_timer = 0
    
    def _fire_arrow(self, target_position: Tuple[float, float, float]) -> None:
        """
        Fire an arrow at the target position
        
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
        
        # Arrow speed
        speed = 20.0
        
        # Create projectile
        arrow = {
            'position': self.position,
            'velocity': (dx * speed, dy * speed),
            'lifetime': 5.0,  # seconds
            'damage': self.damage
        }
        
        self.projectiles.append(arrow)
        
    def portal_volley(self, target_position: Tuple[float, float, float]) -> bool:
        """
        Fire multiple arrows in a spread pattern through portals
        
        Args:
            target_position: Central position to target
            
        Returns:
            True if the ability was used, False if on cooldown
        """
        if not self.can_portal_volley:
            return False
            
        # Calculate base direction
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        base_angle = math.atan2(dy, dx)
        
        # Set cooldown
        self.can_portal_volley = False
        self.portal_volley_timer = self.portal_volley_cooldown
        
        # Fire multiple arrows in a spread
        for i in range(self.portal_volley_arrows):
            # Calculate spread angle
            angle_offset = (i / (self.portal_volley_arrows - 1) - 0.5) * math.radians(self.portal_volley_spread)
            angle = base_angle + angle_offset
            
            # Calculate direction
            arrow_dx = math.cos(angle)
            arrow_dy = math.sin(angle)
            
            # Arrow speed
            speed = 20.0
            
            # Create projectile with portal effect (higher damage)
            arrow = {
                'position': self.position,
                'velocity': (arrow_dx * speed, arrow_dy * speed),
                'lifetime': 5.0,  # seconds
                'damage': self.damage * 1.5,  # More damage for special ability
                'is_portal': True
            }
            
            self.projectiles.append(arrow)
        
        return True
    
    def render(self, renderer, camera) -> None:
        """
        Render the archer and its projectiles
        
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
            
            # Get projectile sprite based on whether it's a portal arrow
            sprite = renderer.get_projectile_sprite(
                'portal_arrow' if proj.get('is_portal', False) else 'arrow'
            )
            
            if sprite:
                # Calculate rotation angle for the sprite
                angle = math.atan2(proj['velocity'][1], proj['velocity'][0]) * 180 / math.pi
                
                # Rotate the sprite
                rotated_sprite = pygame.transform.rotate(sprite, -angle)
                
                # Center the sprite at the projectile position
                sprite_rect = rotated_sprite.get_rect(center=screen_pos)
                
                # Draw the sprite
                renderer.screen.blit(rotated_sprite, sprite_rect)
