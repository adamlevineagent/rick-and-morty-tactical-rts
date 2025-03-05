import pygame
import numpy as np
import uuid
from typing import Tuple, List, Optional, Any

class Unit:
    """Base class for all units in the game"""
    
    def __init__(self, type_name: str, position: Tuple[float, float, float], faction: str = "neutral", unit_type: Optional[str] = None):
        """
        Initialize a new unit
        
        Args:
            type_name: String identifier of the unit type
            position: (x, y, z) initial position
            faction: The faction this unit belongs to (player, enemy, neutral)
            unit_type: Optional override for asset selection (defaults to type_name)
        """
        self.id = str(uuid.uuid4())
        self.type = type_name
        self.unit_type = unit_type if unit_type else type_name  # Used for asset selection
        self.position = position
        self.rotation = 0  # degrees, 0 is east, going counter-clockwise
        self.faction = faction
        self.squad = None  # Reference to the Squad this unit belongs to
        self.formation_position = None  # Target position in formation
        
        # State
        self.health = 100
        self.max_health = 100
        self.state = "idle"  # idle, moving, attacking, dead
        self.target = None
        self.path = []
        self.selected = False
        
        # Animation state
        self.sprite_index = 0
        self.animation_frame = 0
        self.animation_speed = 0.1  # seconds per frame
        self.animation_timer = 0
        
        # Common attributes (will be overridden by subclasses)
        self.speed = 5.0
        self.attack_range = 1.0
        self.attack_speed = 1.0  # attacks per second
        self.damage = 10
        self.is_ranged = False
        
        # Knockback parameters
        self.knockback_power = 0.0  # How far this unit pushes enemies on hit
        self.knockback_resistance = 0.0  # How resistant this unit is to being knocked back
        self.knockback_recovery = 2.0  # How quickly unit recovers from knockback (seconds)
        self.knockback_timer = 0  # Current knockback recovery timer
        self.knockback_velocity = np.array([0.0, 0.0, 0.0])  # Current knockback movement
        
        # Track who damaged this unit (useful for scoring or vengeance AI)
        self.last_attacker = None
        
    def update(self, dt: float, game_state) -> None:
        """
        Update the unit state
        
        Args:
            dt: Time elapsed since last frame in seconds
            game_state: Current game state
        """
        # Process knockback if active
        if self.knockback_timer > 0:
            # Move unit based on knockback velocity
            self.position = (
                self.position[0] + self.knockback_velocity[0] * dt,
                self.position[1] + self.knockback_velocity[1] * dt,
                self.position[2]
            )
            
            # Reduce knockback timer
            self.knockback_timer -= dt
            if self.knockback_timer <= 0:
                # Reset knockback
                self.knockback_velocity = np.array([0.0, 0.0, 0.0])
                self.knockback_timer = 0
                
                # If the unit was in an active state before knockback, resume it
                if self.state == "idle" and self.target is not None:
                    self.state = "attacking"
            
            # Skip other updates while affected by knockback
            return
        
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # Assuming 4 frames per animation
        
        # Update based on current state
        if self.state == "moving" and self.path:
            self._update_movement(dt, game_state)
        elif self.state == "attacking":
            self._update_attack(dt, game_state)
            
    def _update_movement(self, dt: float, game_state) -> None:
        """Update unit movement"""
        if not self.path:
            self.state = "idle"
            return
        
        # Get next waypoint
        target = self.path[0]
        
        # Calculate direction and distance
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = np.sqrt(dx*dx + dy*dy)
        
        # Check if we've reached the waypoint
        if distance < 0.5:  # Close enough
            self.path.pop(0)
            if not self.path:
                self.state = "idle"
                return
            
            # Get the next waypoint
            target = self.path[0]
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
        
        # Update rotation
        target_rotation = (np.arctan2(dy, dx) * 180 / np.pi) % 360
        
        # Smooth rotation (simple version)
        rotation_diff = (target_rotation - self.rotation) % 360
        if rotation_diff > 180:
            rotation_diff -= 360
            
        rotation_speed = 180 * dt  # 180 degrees per second
        if abs(rotation_diff) < rotation_speed:
            self.rotation = target_rotation
        else:
            self.rotation = (self.rotation + np.sign(rotation_diff) * rotation_speed) % 360
        
        # Convert rotation to sprite index (assuming 8 directional sprites)
        self.sprite_index = int(((self.rotation + 22.5) % 360) // 45)
        
        # Move toward target
        move_distance = min(self.speed * dt, distance)
        
        self.position = (
            self.position[0] + dx / distance * move_distance,
            self.position[1] + dy / distance * move_distance,
            self.position[2]  # Keep same height for now
        )
        
    def _update_attack(self, dt: float, game_state) -> None:
        """Update unit attack"""
        # Find target
        target_unit = None
        
        # If target is a string (ID), find the unit
        if isinstance(self.target, str):
            # Search in player units
            for unit in game_state.player_units:
                if unit.id == self.target:
                    target_unit = unit
                    break
                    
            # If not found, search in enemy units
            if target_unit is None:
                for unit in game_state.enemy_units:
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
        distance = np.sqrt(dx*dx + dy*dy)
        
        # Update rotation to face target
        target_rotation = (np.arctan2(dy, dx) * 180 / np.pi) % 360
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
            
            # Perform attack
            target_unit.take_damage(self.damage, self)
            
            # Trigger attack animation
            self.animation_frame = 0
            self.animation_timer = 0
    
    def is_valid_target(self, target_unit) -> bool:
        """Check if a unit is a valid target (alive and enemy)"""
        return target_unit is not None and \
               target_unit.state != "dead" and \
               target_unit.faction != self.faction
    
    def is_alive(self) -> bool:
        """Check if the unit is alive"""
        return self.state != "dead"
            
    def is_melee_unit(self) -> bool:
        """Determine if this unit is considered a melee unit"""
        return not self.is_ranged and self.attack_range <= 2.0

    def take_damage(self, amount: float, attacker=None) -> None:
        """
        Deal damage to the unit
        
        Args:
            amount: Amount of damage to deal
            attacker: Unit that caused the damage (optional)
        """
        # Apply damage
        self.health -= amount
        
        # Apply knockback if the attacker is a melee unit
        if attacker is not None and attacker.is_melee_unit():
            # Calculate knockback direction (away from attacker)
            dx = self.position[0] - attacker.position[0]
            dy = self.position[1] - attacker.position[1]
            if dx == 0 and dy == 0:  # Prevent division by zero
                # Random direction if units are stacked
                angle = np.random.random() * 2 * np.pi
                dx, dy = np.cos(angle), np.sin(angle)
            else:
                # Normalize direction vector
                mag = np.sqrt(dx*dx + dy*dy)
                dx, dy = dx/mag, dy/mag
            
            # Calculate knockback amount based on attacker's power and unit's resistance
            knockback_strength = max(0, attacker.knockback_power - self.knockback_resistance)
            
            # Apply knockback (distance slightly longer than attacker's range)
            knockback_distance = attacker.attack_range * 1.2 * knockback_strength
            
            # Set knockback velocity (this will be used during unit update)
            self.knockback_velocity = np.array([dx * knockback_distance, dy * knockback_distance, 0])
            
            # Set knockback recovery timer
            self.knockback_timer = self.knockback_recovery
            
            # Briefly interrupt current action
            if self.state != "dead":
                self.path = []  # Clear path to prevent automatic movement
                
        # Optional: Track who damaged this unit (useful for scoring or vengeance AI)
        self.last_attacker = attacker
        
        if self.health <= 0:
            self.health = 0
            self.state = "dead"
            
    def heal(self, amount: float) -> None:
        """
        Heal the unit
        
        Args:
            amount: Amount of health to restore
        """
        self.health = min(self.health + amount, self.max_health)
    
    def set_destination(self, destination: tuple) -> None:
        """
        Set a destination for the unit to move to
        
        Args:
            destination: Target position (x, y, z)
        """
        # Store destination
        self.destination = destination
        
        # Create a path (for now just a direct line)
        self.path = [destination]
        
        # Set state to moving
        self.state = "moving"
    
    def move_to(self, target_position: List[float]) -> None:
        """
        Command the unit to move to a position
        
        Args:
            target_position: The [x, y] or [x, y, z] position to move to
        """
        self.state = "moving"
        self.target = None
        
        # Ensure target position is 3D
        if len(target_position) == 2:
            target_position = [target_position[0], target_position[1], self.position[2]]
            
        self.path = [target_position]
    
    def set_target(self, target) -> None:
        """
        Set the unit's attack target
        
        Args:
            target: Target unit to attack
        """
        self.target = target
    
    def set_attack_mode(self, attacking: bool = True) -> None:
        """
        Toggle attack mode
        
        Args:
            attacking: True to enter attack mode, False to exit
        """
        if attacking and self.target:
            self.state = "attacking"
        elif not attacking:
            self.state = "idle"
            
    def issue_move_command(self, target_position):
        """
        Legacy method - Issue a move command to this unit
        
        Args:
            target_position: (x, y, z) position to move to
        """
        self.move_to(target_position)
        
    def issue_attack_command(self, target):
        """
        Legacy method - Issue an attack command to this unit
        
        Args:
            target: Target unit or position
        """
        if hasattr(target, 'id'):
            self.set_target(target)
            self.set_attack_mode(True)
            
            # If target is out of range, move toward it
            dx = target.position[0] - self.position[0]
            dy = target.position[1] - self.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance > self.attack_range:
                self.state = "moving"
                self.path = [target.position]
        else:
            # If target is a position, move there
            self.move_to(target)
    
    def render(self, renderer, camera) -> None:
        """
        Render the unit
        
        Args:
            renderer: Renderer object
            camera: Camera object for view transformations
        """
        # Skip rendering dead units
        if self.state == "dead":
            return
            
        # Convert world position to screen position
        screen_pos = camera.world_to_screen(self.position)
        
        # Get sprite based on type, direction and animation frame
        sprite = renderer.get_unit_sprite(
            self.unit_type, 
            self.sprite_index, 
            self.animation_frame, 
            self.state
        )
        
        if sprite:
            # Center the sprite
            sprite_rect = sprite.get_rect(center=screen_pos)
            renderer.screen.blit(sprite, sprite_rect)
            
            # Render health bar if damaged
            if self.health < self.max_health:
                health_pct = self.health / self.max_health
                health_width = 32  # Fixed width for health bar
                health_height = 4
                
                # Background (red)
                health_bg_rect = pygame.Rect(
                    screen_pos[0] - health_width/2,
                    screen_pos[1] - 30,  # Position above unit
                    health_width,
                    health_height
                )
                pygame.draw.rect(renderer.screen, (255, 0, 0), health_bg_rect)
                
                # Foreground (green)
                health_fg_rect = pygame.Rect(
                    screen_pos[0] - health_width/2,
                    screen_pos[1] - 30,
                    health_width * health_pct,
                    health_height
                )
                pygame.draw.rect(renderer.screen, (0, 255, 0), health_fg_rect)
            
        # If selected, draw selection circle
        if self.selected:
            radius = 15  # Selection circle radius
            pygame.draw.circle(
                renderer.screen,
                (0, 255, 0),  # Green color
                screen_pos,
                radius,
                2  # Line width
            )
