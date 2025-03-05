import numpy as np
from typing import List, Tuple, Dict, Any

from game.objects import Projectile, Explosion

class PhysicsEngine:
    """
    Handles all physics simulations for the game, including:
    - Projectile trajectories
    - Collisions
    - Explosions and knockback
    - Ragdoll physics for unit corpses
    """
    
    def __init__(self, renderer=None):
        """
        Initialize the physics engine
        
        Args:
            renderer: The game renderer for rendering physics objects
        """
        self.gravity = 9.8  # m/s^2, downward
        self.projectiles = []  # List of active projectiles
        self.explosions = []  # List of active explosions
        self.debris = []  # List of debris pieces and corpses
        self.renderer = renderer  # Store the renderer
        
        # Physics settings
        self.physics_step = 1/60  # Fixed physics timestep
        self.accumulated_time = 0
        
    def update(self, dt, game_state):
        """
        Update all physics objects
        
        Args:
            dt: Time elapsed since last frame in seconds
            game_state: The current game state
        """
        # Accumulate time for fixed timestep updates
        self.accumulated_time += dt
        
        # Run physics with a fixed timestep for stability
        while self.accumulated_time >= self.physics_step:
            self._update_projectiles(game_state, self.physics_step)
            self._update_explosions(game_state, self.physics_step)
            self._update_debris(self.physics_step)
            
            self.accumulated_time -= self.physics_step
    
    def _update_projectiles(self, game_state, dt):
        """
        Update all projectiles
        
        Args:
            game_state: The current game state
            dt: Physics timestep in seconds
        """
        # Iterate through all active projectiles
        for proj in self.projectiles[:]:
            if not proj.active:
                self.projectiles.remove(proj)
                continue
                
            # Update projectile and collect any effects that result
            effects = proj.update(dt, game_state)
            
            # Process effects (explosions, hits, etc.)
            for effect in effects:
                if effect['type'] == 'explosion':
                    # Create a new explosion
                    explosion = Explosion(
                        position=effect['position'],
                        radius=effect['radius'],
                        damage=effect['damage'],
                        owner=effect['owner'],
                        lifetime=0.5,
                        damage_falloff=True
                    )
                    self.explosions.append(explosion)
                    
                    # Create debris from the explosion
                    self._create_debris(effect['position'], effect['radius'])
    
    def _update_explosions(self, game_state, dt):
        """
        Update all active explosions
        
        Args:
            game_state: The current game state
            dt: Physics timestep in seconds
        """
        # Iterate through all active explosions
        for explosion in self.explosions[:]:
            if not explosion.active:
                self.explosions.remove(explosion)
                continue
                
            # Update explosion
            explosion.update(dt, game_state)
    
    def _update_debris(self, dt):
        """
        Update all debris pieces
        
        Args:
            dt: Physics timestep in seconds
        """
        # Iterate through all debris pieces
        for debris in self.debris[:]:
            # Update position based on velocity
            debris['position'] = (
                debris['position'][0] + debris['velocity'][0] * dt,
                debris['position'][1] + debris['velocity'][1] * dt,
                debris['position'][2] + debris['velocity'][2] * dt
            )
            
            # Apply gravity to velocity
            debris['velocity'] = (
                debris['velocity'][0] * 0.99,  # Apply drag
                debris['velocity'][1] * 0.99,
                debris['velocity'][2] - self.gravity * dt
            )
            
            # Check for ground collision
            if debris['position'][2] <= 0:
                if debris['bounces'] > 0:
                    # Bounce with energy loss
                    debris['velocity'] = (
                        debris['velocity'][0] * 0.8,
                        debris['velocity'][1] * 0.8,
                        -debris['velocity'][2] * 0.5  # Half the energy on bounce
                    )
                    debris['bounces'] -= 1
                    debris['position'] = (
                        debris['position'][0],
                        debris['position'][1],
                        0.1  # Slightly above ground to prevent stuck
                    )
                else:
                    # Stop motion if out of bounces
                    debris['velocity'] = (0, 0, 0)
                    debris['position'] = (
                        debris['position'][0],
                        debris['position'][1],
                        0
                    )
            
            # Update debris lifetime
            debris['lifetime'] -= dt
            if debris['lifetime'] <= 0:
                self.debris.remove(debris)
    
    def _create_debris(self, position, radius):
        """
        Create debris pieces at the specified position
        
        Args:
            position: (x, y, z) position where debris originates
            radius: Radius of the area to spawn debris
        """
        # Number of debris pieces scales with explosion radius
        num_debris = int(radius * 5)
        
        for _ in range(num_debris):
            # Random velocity in a sphere
            angle = np.random.uniform(0, 2 * np.pi)
            elevation = np.random.uniform(-np.pi / 2, np.pi / 2)
            speed = np.random.uniform(1, 5) * radius
            
            vx = speed * np.cos(elevation) * np.cos(angle)
            vy = speed * np.cos(elevation) * np.sin(angle)
            vz = speed * np.sin(elevation)
            
            debris = {
                'position': position,
                'velocity': (vx, vy, vz),
                'rotation': (np.random.uniform(0, 360), np.random.uniform(0, 360), np.random.uniform(0, 360)),
                'angular_velocity': (np.random.uniform(-180, 180), np.random.uniform(-180, 180), np.random.uniform(-180, 180)),
                'size': np.random.uniform(0.1, 0.3),
                'bounces': np.random.randint(1, 4),
                'lifetime': np.random.uniform(5, 15)  # Seconds before disappearing
            }
            
            self.debris.append(debris)
    
    def create_projectile(self, start_position, direction, faction, damage, projectile_type):
        """
        Create a projectile from start_position moving in the given direction
        
        Args:
            start_position: (x, y, z) starting position
            direction: (dx, dy, dz) direction vector
            faction: The faction that fired this projectile
            damage: Base damage for the projectile
            projectile_type: Type of projectile (energy, portal, grenade)
            
        Returns:
            The created projectile object
        """
        # Calculate a target position based on the direction vector
        # We'll just use a point far away in the direction
        distance = 1000  # Some large distance
        target_position = (
            start_position[0] + direction[0] * distance,
            start_position[1] + direction[1] * distance,
            start_position[2] + direction[2] * distance
        )
        
        # Map project types
        if projectile_type == 'energy':
            actual_type = 'energy_bolt'
        elif projectile_type == 'portal':
            actual_type = 'portal_arrow'
        elif projectile_type == 'grenade':
            actual_type = 'grenade'
        else:
            actual_type = 'arrow'
            
        # Call the existing fire_projectile method
        return self.fire_projectile(
            start_position=start_position,
            target_position=target_position,
            owner=faction,  # Using faction as owner
            damage=damage,
            projectile_type=actual_type
        )
        
    def fire_projectile(self, start_position, target_position=None, target_unit=None, 
                      projectile_type="arrow", owner=None, damage=10.0):
        """
        Fire a projectile from start_position toward a target
        
        Args:
            start_position: (x, y, z) starting position
            target_position: (x, y, z) target position (if not targeting a unit)
            target_unit: Unit to target (if not targeting a position)
            projectile_type: Type of projectile (arrow, grenade, portal_arrow, energy_bolt)
            owner: The unit that fired this projectile
            damage: Base damage for the projectile
            
        Returns:
            The created projectile object
        """
        # Set up parameters based on projectile type
        if projectile_type == "arrow":
            speed = 100.0
            lifetime = 5.0
        elif projectile_type == "grenade":
            speed = 60.0
            lifetime = 10.0
        elif projectile_type == "portal_arrow":
            speed = 120.0
            lifetime = 5.0
        elif projectile_type == "energy_bolt":
            speed = 150.0
            lifetime = 3.0
        else:  # Default
            speed = 100.0
            lifetime = 5.0
            
        # Create the projectile using our Projectile class
        projectile = Projectile(
            position=start_position,
            target_position=target_position,
            target_unit=target_unit,
            speed=speed,
            damage=damage,
            owner=owner,
            lifetime=lifetime,
            projectile_type=projectile_type
        )
        
        # Add to active projectiles
        self.projectiles.append(projectile)
        
        return projectile
        
    def create_explosion(self, position, radius=3.0, damage=30.0, owner=None):
        """
        Create an explosion at the specified position
        
        Args:
            position: (x, y, z) position of the explosion
            radius: Radius of the explosion
            damage: Base damage of the explosion
            owner: The unit that caused this explosion
            
        Returns:
            The created explosion object
        """
        explosion = Explosion(
            position=position,
            radius=radius,
            damage=damage,
            owner=owner,
            lifetime=0.5,
            damage_falloff=True
        )
        
        self.explosions.append(explosion)
        
        # Create debris from the explosion
        self._create_debris(position, radius)
        
        return explosion
    
    def render(self, dt):
        """
        Render all physics objects
        
        Args:
            dt: Time elapsed since last frame
        """
        if not self.renderer:
            return  # Can't render without a renderer
            
        screen = self.renderer.screen
        
        # Render projectiles
        for projectile in self.projectiles:
            projectile.render(screen, self.renderer)
            
        # Render explosions
        for explosion in self.explosions:
            explosion.render(screen, self.renderer)
            
        # Render debris (simplified for now)
        for debris in self.debris:
            # Convert world position to screen position
            screen_pos = self.renderer.world_to_screen(debris['position'])
            
            # Draw a simple circle for debris
            import pygame
            pygame.draw.circle(screen, (100, 100, 100), screen_pos, int(debris['size'] * self.renderer.camera_zoom))
