from typing import Tuple, List, Optional
import math
import numpy as np

from .unit import Unit

class TechGrenadier(Unit):
    """
    Tech Grenadier unit - Rick and Morty universe's equivalent of explosive specialists.
    Uses advanced technology grenades that deal area damage and can create temporary hazards.
    """
    
    def __init__(self, position: Tuple[float, float, float], faction: str = "player"):
        """
        Initialize a Tech Grenadier unit
        
        Args:
            position: (x, y, z) initial position
            faction: The faction this unit belongs to (player, enemy)
        """
        super().__init__("tech_grenadier", position, faction)
        
        # Override base stats with Tech Grenadier specific values
        self.max_health = 120
        self.health = self.max_health
        self.speed = 3.8  # Slower than other units
        self.damage = 8  # Low direct damage
        self.attack_range = 12.0  # Medium range
        self.attack_speed = 0.5  # attacks per second (slower)
        
        # Special abilities
        self.can_mega_bomb = True
        self.mega_bomb_cooldown = 30.0  # seconds
        self.mega_bomb_timer = 0.0
        self.mega_bomb_radius = 8.0
        self.mega_bomb_damage = 75
        
        # Grenade tracking
        self.grenades: List = []  # Will store active grenades
        
    def update(self, dt: float, game_state) -> None:
        """
        Update the Tech Grenadier unit
        
        Args:
            dt: Time elapsed since last frame in seconds
            game_state: Current game state
        """
        # Update cooldowns
        if self.mega_bomb_timer > 0:
            self.mega_bomb_timer -= dt
            if self.mega_bomb_timer <= 0:
                self.can_mega_bomb = True
                
        # Update grenades
        for grenade in self.grenades[:]:
            grenade['lifetime'] -= dt
            
            # Check if grenade should explode
            if grenade['lifetime'] <= 0:
                # Create explosion
                self._create_explosion(grenade['position'], grenade['radius'], grenade['damage'], game_state)
                self.grenades.remove(grenade)
                continue
                
            # Move grenade (with arc trajectory)
            grenade['time_in_air'] += dt
            
            # Calculate new position based on projectile motion
            # x = x0 + vx * t
            # y = y0 + vy * t - 0.5 * g * t^2
            t = grenade['time_in_air']
            
            grenade['position'] = (
                grenade['start_position'][0] + grenade['velocity'][0] * t,
                grenade['start_position'][1] + grenade['velocity'][1] * t,
                grenade['start_position'][2] + grenade['z_velocity'] * t - 0.5 * 9.8 * t * t
            )
                
        # Call the base update method
        super().update(dt, game_state)
        
    def _update_attack(self, dt: float, game_state) -> None:
        """Override attack to implement grenade throwing"""
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
            
            # Throw a grenade
            self._throw_grenade(target_unit.position)
            
            # Trigger attack animation
            self.animation_frame = 0
            self.animation_timer = 0
    
    def _throw_grenade(self, target_position: Tuple[float, float, float]) -> None:
        """
        Throw a grenade at the target position
        
        Args:
            target_position: Position to throw at
        """
        # Calculate direction
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        dz = target_position[2] - self.position[2]
        distance_2d = math.sqrt(dx*dx + dy*dy)
        
        # Normalize horizontal direction
        if distance_2d > 0:
            dx /= distance_2d
            dy /= distance_2d
        
        # Grenade speed
        speed = 15.0
        
        # Calculate initial velocity for arc trajectory
        # For simplicity, we'll use a fixed time-to-target approach
        time_to_target = distance_2d / speed
        
        # Initial z velocity to reach the target height
        # Using the formula: z = z0 + vz*t - 0.5*g*t^2
        # Solving for vz: vz = (z - z0 + 0.5*g*t^2) / t
        gravity = 9.8
        z_velocity = (dz + 0.5 * gravity * time_to_target * time_to_target) / time_to_target
        
        # Create grenade
        grenade = {
            'start_position': self.position,
            'position': self.position,
            'velocity': (dx * speed, dy * speed),
            'z_velocity': z_velocity,
            'time_in_air': 0.0,
            'lifetime': time_to_target,  # Explode when reaching target
            'damage': self.damage,
            'radius': 3.0  # Explosion radius
        }
        
        self.grenades.append(grenade)
        
    def _create_explosion(self, position: Tuple[float, float, float], radius: float, damage: float, game_state) -> None:
        """
        Create an explosion at the specified position
        
        Args:
            position: Center of the explosion
            radius: Radius of the explosion
            damage: Base damage of the explosion
            game_state: Current game state
        """
        # Find all units in explosion radius
        for unit in game_state.get_units():
            if unit.is_alive():
                # Calculate distance to explosion
                dx = unit.position[0] - position[0]
                dy = unit.position[1] - position[1]
                dz = unit.position[2] - position[2]
                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if distance <= radius:
                    # Calculate damage based on distance (more damage closer to center)
                    distance_factor = 1.0 - (distance / radius)
                    explosion_damage = damage * distance_factor
                    
                    # Apply damage to unit
                    unit.take_damage(explosion_damage)
                    
                    # Apply knockback
                    # In a full implementation, this would affect the unit's position
                    # For now, we just calculate the direction
                    if distance > 0:
                        knockback_direction = (dx/distance, dy/distance)
        
        # In a real implementation, we would add visual and sound effects here
        
    def mega_bomb(self, target_position: Tuple[float, float, float]) -> bool:
        """
        Throw a mega bomb with a large explosion radius
        
        Args:
            target_position: Position to target
            
        Returns:
            True if the ability was used, False if on cooldown
        """
        if not self.can_mega_bomb:
            return False
            
        # Calculate direction
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        dz = target_position[2] - self.position[2]
        distance_2d = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction
        if distance_2d > 0:
            dx /= distance_2d
            dy /= distance_2d
        
        # Set cooldown
        self.can_mega_bomb = False
        self.mega_bomb_timer = self.mega_bomb_cooldown
        
        # Grenade speed
        speed = 12.0  # Slower than regular grenades
        
        # Calculate initial velocity for arc trajectory
        time_to_target = distance_2d / speed
        
        # Initial z velocity to reach the target height
        gravity = 9.8
        z_velocity = (dz + 0.5 * gravity * time_to_target * time_to_target) / time_to_target
        
        # Create mega bomb
        mega_bomb = {
            'start_position': self.position,
            'position': self.position,
            'velocity': (dx * speed, dy * speed),
            'z_velocity': z_velocity,
            'time_in_air': 0.0,
            'lifetime': time_to_target,
            'damage': self.mega_bomb_damage,
            'radius': self.mega_bomb_radius,
            'is_mega': True
        }
        
        self.grenades.append(mega_bomb)
        return True
    
    def render(self, renderer, camera) -> None:
        """
        Render the grenadier and its grenades
        
        Args:
            renderer: Renderer object
            camera: Camera object
        """
        # Render the unit
        super().render(renderer, camera)
        
        # Render grenades
        for grenade in self.grenades:
            # Convert grenade position to screen coordinates
            screen_pos = camera.world_to_screen(grenade['position'])
            
            # Get grenade sprite
            sprite = renderer.get_projectile_sprite(
                'mega_bomb' if grenade.get('is_mega', False) else 'grenade'
            )
            
            if sprite:
                # Center the sprite at the grenade position
                sprite_rect = sprite.get_rect(center=screen_pos)
                
                # Draw the sprite
                renderer.screen.blit(sprite, sprite_rect)
