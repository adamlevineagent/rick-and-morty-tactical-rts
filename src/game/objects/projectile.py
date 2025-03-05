import pygame
import numpy as np
from typing import Tuple, List, Optional, Any

class Projectile:
    """
    Base class for projectiles in the game
    
    Projectiles are created by units when they attack and travel through
    the game world, potentially causing damage when they hit targets.
    """
    
    def __init__(self, 
                position: Tuple[float, float, float],
                target_position: Tuple[float, float, float] = None,
                target_unit = None,
                speed: float = 100.0,
                damage: float = 10.0,
                owner = None,
                lifetime: float = 5.0,
                projectile_type: str = "arrow"):
        """
        Initialize a new projectile
        
        Args:
            position: Starting position
            target_position: Position to travel toward (if not tracking a unit)
            target_unit: Unit to track and hit (if not traveling to a position)
            speed: Movement speed in world units per second
            damage: Damage to deal on hit
            owner: The unit that fired this projectile
            lifetime: Maximum lifetime in seconds before auto-destruction
            projectile_type: Type of projectile (affects visuals and behavior)
        """
        self.position = position
        self.target_position = target_position
        self.target_unit = target_unit
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.max_lifetime = lifetime
        self.lifetime = 0
        self.projectile_type = projectile_type
        self.active = True
        
        # Calculate initial direction
        if target_position:
            dx = target_position[0] - position[0]
            dy = target_position[1] - position[1]
            dz = target_position[2] - position[2]
            distance = np.sqrt(dx*dx + dy*dy + dz*dz)
            if distance > 0:
                self.direction = (dx/distance, dy/distance, dz/distance)
            else:
                self.direction = (0, 0, 0)
        elif target_unit:
            # Will be updated each frame to track the target
            dx = target_unit.position[0] - position[0]
            dy = target_unit.position[1] - position[1]
            dz = 0  # Assume same height for now
            distance = np.sqrt(dx*dx + dy*dy + dz*dz)
            if distance > 0:
                self.direction = (dx/distance, dy/distance, dz/distance)
            else:
                self.direction = (0, 0, 0)
        else:
            self.direction = (0, 0, 0)
            
        # Calculate rotation (for rendering)
        self.rotation = np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        
        # Special properties for different projectile types
        if projectile_type == "grenade":
            self.has_gravity = True
            self.bounce_factor = 0.3
            self.z_velocity = 20.0  # Initial upward velocity
            self.explodes = True
            self.explosion_radius = 15.0
        elif projectile_type == "energy_bolt":
            self.has_trail = True
            self.trail_color = (30, 200, 255)
        elif projectile_type == "portal_arrow":
            self.portal_travels = True
            self.trail_color = (120, 20, 200)
        else:  # Default arrow
            self.has_gravity = False
            self.has_trail = False
            self.explodes = False
    
    def update(self, dt, game_state):
        """
        Update the projectile state
        
        Args:
            dt: Time elapsed since last frame
            game_state: Current game state for collision detection
        
        Returns:
            List of effects created this frame (e.g., explosions)
        """
        # Update lifetime and check if expired
        self.lifetime += dt
        if self.lifetime >= self.max_lifetime:
            self.active = False
            return []
        
        # If tracking a unit, update direction
        if self.target_unit and self.target_unit.is_alive():
            dx = self.target_unit.position[0] - self.position[0]
            dy = self.target_unit.position[1] - self.position[1]
            dz = 0  # Assume same height for now
            distance = np.sqrt(dx*dx + dy*dy + dz*dz)
            if distance > 0:
                # Only partially adjust direction each frame for homing effect
                self.direction = (
                    0.8 * self.direction[0] + 0.2 * dx/distance,
                    0.8 * self.direction[1] + 0.2 * dy/distance,
                    0.8 * self.direction[2] + 0.2 * dz/distance
                )
                
                # Normalize direction
                dir_length = np.sqrt(self.direction[0]**2 + self.direction[1]**2 + self.direction[2]**2)
                if dir_length > 0:
                    self.direction = (
                        self.direction[0] / dir_length,
                        self.direction[1] / dir_length,
                        self.direction[2] / dir_length
                    )
        
        # Apply gravity if needed
        if hasattr(self, 'has_gravity') and self.has_gravity:
            self.z_velocity -= 9.8 * dt  # Apply gravity
            new_z = self.position[2] + self.z_velocity * dt
            
            # Check for ground collision
            if new_z <= 0:
                if hasattr(self, 'explodes') and self.explodes:
                    # Create explosion at impact
                    self.active = False
                    return [{
                        'type': 'explosion',
                        'position': (self.position[0], self.position[1], 0),
                        'radius': self.explosion_radius,
                        'damage': self.damage,
                        'owner': self.owner
                    }]
                elif hasattr(self, 'bounce_factor'):
                    # Bounce off ground
                    self.z_velocity = -self.z_velocity * self.bounce_factor
                    new_z = 0
            
            self.position = (self.position[0], self.position[1], new_z)
        
        # Move projectile based on direction and speed
        self.position = (
            self.position[0] + self.direction[0] * self.speed * dt,
            self.position[1] + self.direction[1] * self.speed * dt,
            self.position[2] + self.direction[2] * self.speed * dt
        )
        
        # Update rotation for rendering
        self.rotation = np.degrees(np.arctan2(self.direction[1], self.direction[0]))
        
        # Check for collision with units
        effects = self._check_collisions(game_state)
        
        return effects
    
    def _check_collisions(self, game_state):
        """
        Check for collisions with units and terrain
        
        Args:
            game_state: The current game state
            
        Returns:
            A list of effect dictionaries (damage, explosions, etc.)
        """
        effects = []
        
        # Default to friendly fire OFF
        allow_friendly_fire = False
        
        # Determine faction (either from a unit owner or from a string faction identifier)
        owner_faction = "neutral"
        if self.owner:
            if isinstance(self.owner, str):
                # Owner is already a faction string
                owner_faction = self.owner
            else:
                # Owner is a unit object
                owner_faction = self.owner.faction
        
        # Check collision with appropriate units based on faction
        units_to_check = []
        if owner_faction == "player":
            # Player projectiles hit enemy units
            units_to_check = game_state.get_all_enemy_units()
        elif owner_faction == "enemy":
            # Enemy projectiles hit player units
            units_to_check = game_state.get_all_player_units()
        
        # Check each unit for collision
        for unit in units_to_check:
            if not unit.is_alive():
                continue
                
            # Simple circle collision check
            dx = unit.position[0] - self.position[0]
            dy = unit.position[1] - self.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            # Get collision radius (default to 1.0 if not defined)
            collision_radius = getattr(unit, 'collision_radius', 1.0)
            
            # Check if within collision radius
            if distance < collision_radius:
                # Hit detected!
                unit.take_damage(self.damage, self.owner)
                
                # Create hit effect
                effects.append({
                    'type': 'hit',
                    'position': (self.position[0], self.position[1], self.position[2]),
                    'unit': unit
                })
                
                # Deactivate projectile unless it's a penetrating type
                if not hasattr(self, 'penetrates') or not self.penetrates:
                    self.active = False
                
                # If projectile explodes on impact, create explosion
                if hasattr(self, 'explodes') and self.explodes:
                    effects.append({
                        'type': 'explosion',
                        'position': (self.position[0], self.position[1], self.position[2]),
                        'radius': self.explosion_radius,
                        'damage': self.damage,
                        'owner': self.owner
                    })
                    self.active = False
                
                # Return after first hit unless penetrating
                if not hasattr(self, 'penetrates') or not self.penetrates:
                    break
        
        return effects
    
    def render(self, screen, renderer):
        """
        Render the projectile
        
        Args:
            screen: Pygame screen to render on
            renderer: GameRenderer for world-to-screen conversion
        """
        if not self.active:
            return
            
        # Convert world position to screen position
        screen_pos = renderer.world_to_screen(self.position)
        
        # Choose color based on type
        if self.projectile_type == "arrow":
            color = (150, 75, 0)  # Brown
            size = 2
        elif self.projectile_type == "grenade":
            color = (50, 50, 50)  # Dark gray
            size = 4
        elif self.projectile_type == "energy_bolt":
            color = (30, 200, 255)  # Cyan
            size = 3
        elif self.projectile_type == "portal_arrow":
            color = (120, 20, 200)  # Purple
            size = 3
        else:
            color = (255, 255, 255)  # White (default)
            size = 2
            
        # Draw projectile
        pygame.draw.circle(screen, color, screen_pos, size)
        
        # Draw trail if it has one
        if hasattr(self, 'has_trail') and self.has_trail:
            # Calculate trail points based on direction (backwards)
            trail_length = 15
            trail_end = (
                self.position[0] - self.direction[0] * trail_length,
                self.position[1] - self.direction[1] * trail_length,
                self.position[2] - self.direction[2] * trail_length
            )
            trail_end_screen = renderer.world_to_screen(trail_end)
            
            # Draw trail line
            trail_color = getattr(self, 'trail_color', color)
            pygame.draw.line(screen, trail_color, screen_pos, trail_end_screen, 2)


class Explosion:
    """
    Represents an explosion effect that can damage multiple units
    """
    
    def __init__(self, 
                position: Tuple[float, float, float],
                radius: float = 15.0,
                damage: float = 30.0,
                owner = None,
                lifetime: float = 0.5,
                damage_falloff: bool = True):
        """
        Initialize a new explosion
        
        Args:
            position: Center position of the explosion
            radius: Radius of the explosion in world units
            damage: Maximum damage at center
            owner: The unit that caused this explosion
            lifetime: How long the explosion lasts in seconds
            damage_falloff: Whether damage decreases with distance from center
        """
        self.position = position
        self.radius = radius
        self.damage = damage
        self.owner = owner
        self.max_lifetime = lifetime
        self.lifetime = 0
        self.damage_falloff = damage_falloff
        self.active = True
        
        # Animation properties
        self.current_radius = 0
        self.max_radius_time = lifetime * 0.3  # Time to reach full radius
        
        # Track units already damaged to prevent multiple hits
        self.damaged_units = set()
    
    def update(self, dt, game_state):
        """
        Update the explosion animation and apply damage
        
        Args:
            dt: Time elapsed since last frame
            game_state: Current game state for affecting units
            
        Returns:
            List of additional effects (usually empty for explosions)
        """
        # Update lifetime and check if expired
        self.lifetime += dt
        if self.lifetime >= self.max_lifetime:
            self.active = False
            return []
        
        # Update current radius based on lifetime
        if self.lifetime < self.max_radius_time:
            # Expanding phase
            progress = self.lifetime / self.max_radius_time
            self.current_radius = self.radius * progress
        else:
            # Full size phase
            self.current_radius = self.radius
        
        # Apply damage to units in range (if this is the first frame)
        if self.lifetime < dt:
            self._apply_damage(game_state)
        
        return []
    
    def _apply_damage(self, game_state):
        """
        Apply damage to units within the explosion radius
        
        Args:
            game_state: Current game state for accessing units
        """
        # Get owner faction
        owner_faction = "neutral"
        if self.owner:
            owner_faction = self.owner.faction
        
        # Apply damage to appropriate units based on faction
        if owner_faction == "player":
            # Player explosions damage enemy units
            units_to_check = game_state.get_all_enemy_units()
        elif owner_faction == "enemy":
            # Enemy explosions damage player units
            units_to_check = game_state.get_all_player_units()
        else:
            # Neutral explosions damage both
            units_to_check = game_state.get_all_player_units() + game_state.get_all_enemy_units()
        
        # Check each unit for being in blast radius
        for unit in units_to_check:
            if not unit.is_alive() or unit in self.damaged_units:
                continue
                
            # Calculate distance to explosion center
            dx = unit.position[0] - self.position[0]
            dy = unit.position[1] - self.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            # Check if within explosion radius
            if distance <= self.radius:
                # Calculate damage based on distance
                if self.damage_falloff:
                    # Linear falloff from center
                    damage_multiplier = 1.0 - (distance / self.radius)
                    actual_damage = self.damage * damage_multiplier
                else:
                    # Full damage throughout
                    actual_damage = self.damage
                
                # Apply damage to unit
                unit.take_damage(actual_damage, self.owner)
                
                # Mark unit as damaged by this explosion
                self.damaged_units.add(unit)
    
    def render(self, screen, renderer):
        """
        Render the explosion effect
        
        Args:
            screen: Pygame screen to render on
            renderer: GameRenderer for world-to-screen conversion
        """
        if not self.active:
            return
            
        # Convert world position to screen position
        screen_pos = renderer.world_to_screen(self.position)
        
        # Calculate radius in screen coordinates
        screen_radius = int(self.current_radius * renderer.camera_zoom)
        
        # Calculate color based on lifetime (orange fading to transparent)
        alpha = int(255 * (1 - self.lifetime / self.max_lifetime))
        
        # Create a surface for the explosion with transparency
        explosion_surface = pygame.Surface((screen_radius * 2, screen_radius * 2), pygame.SRCALPHA)
        
        # Draw concentric circles with gradient
        for i in range(screen_radius, 0, -3):
            color_val = min(255, 100 + int(155 * i / screen_radius))
            color = (color_val, int(color_val * 0.6), 0, alpha * i // screen_radius)
            pygame.draw.circle(explosion_surface, color, (screen_radius, screen_radius), i)
        
        # Draw the explosion to the screen
        screen.blit(explosion_surface, (screen_pos[0] - screen_radius, screen_pos[1] - screen_radius))
