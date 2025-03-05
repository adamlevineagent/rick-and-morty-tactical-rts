import pygame
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

class GameRenderer:
    """
    Handles rendering of all game elements including terrain, units, projectiles and effects.
    Serves as the intermediary between the game state and the display.
    """
    
    def __init__(self, screen_width_or_screen=1280, screen_height=720):
        """
        Initialize the game renderer
        
        Args:
            screen_width_or_screen: Either the width of the game window or a pygame Surface
            screen_height: Height of the game window (only used if screen_width_or_screen is an integer)
        """
        # Check if we're given a pygame Surface or dimensions
        if isinstance(screen_width_or_screen, pygame.Surface):
            self.screen = screen_width_or_screen
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            self.screen_width = screen_width_or_screen
            self.screen_height = screen_height
            self.screen = None
        
        # Camera settings
        self.camera_position = (0, 0, 500)  # (x, y, z) - z is height
        self.camera_rotation = 0  # Degrees, 0 = East, 90 = North
        self.camera_zoom = 1.0
        self.camera_pitch = 45  # Degrees down from horizontal
        
        # UI Elements
        self.ui_elements = []
        
        # Initialize fonts
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 10),
            'medium': pygame.font.SysFont('Arial', 14),
            'large': pygame.font.SysFont('Arial', 18),
            'title': pygame.font.SysFont('Arial', 24, bold=True)
        }
        
        # Initialize Pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
    
    def initialize(self):
        """Initialize the renderer and create the game window"""
        if not self.screen:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.DOUBLEBUF | pygame.HWSURFACE
            )
        pygame.display.set_caption("Rick and Morty Tactical RTS")
        
        # Load common resources
        # self.fonts = {
        #     'small': pygame.font.SysFont('Arial', 10),
        #     'medium': pygame.font.SysFont('Arial', 14),
        #     'large': pygame.font.SysFont('Arial', 18),
        #     'title': pygame.font.SysFont('Arial', 24, bold=True)
        # }
    
    def world_to_screen(self, world_pos):
        """
        Convert a 3D world position to 2D screen coordinates
        
        Args:
            world_pos: (x, y, z) position in world space
            
        Returns:
            (x, y) position in screen space
        """
        # Extract world position components
        world_x, world_y, world_z = world_pos
        
        # Apply camera transform (simplified for now)
        # Center of screen is camera position
        rel_x = world_x - self.camera_position[0]
        rel_y = world_y - self.camera_position[1]
        
        # Apply rotation
        angle_rad = np.radians(self.camera_rotation)
        rot_x = rel_x * np.cos(angle_rad) + rel_y * np.sin(angle_rad)
        rot_y = -rel_x * np.sin(angle_rad) + rel_y * np.cos(angle_rad)
        
        # Apply perspective (simplified)
        # For isometric-style projection
        pitch_rad = np.radians(self.camera_pitch)
        screen_x = rot_x * self.camera_zoom
        screen_y = (rot_y * np.sin(pitch_rad) - world_z * np.cos(pitch_rad)) * self.camera_zoom
        
        # Translate to screen center
        screen_x += self.screen_width / 2
        screen_y += self.screen_height / 2
        
        return (int(screen_x), int(screen_y))
    
    def render_game(self, game_state, physics_engine):
        """
        Render the complete game scene
        
        Args:
            game_state: Current game state
            physics_engine: Physics engine instance
        """
        if not self.screen:
            self.initialize()
        
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Render terrain
        self._render_terrain(game_state)
        
        # Render units
        self._render_units(game_state)
        
        # Render physics objects (projectiles, explosions, debris)
        physics_engine.render(self.screen, self)
        
        # Render UI elements
        self._render_ui(game_state)
        
        # Update the display
        pygame.display.flip()
    
    def render_game_state(self, game_state):
        """
        Render the game state without using physics_engine (which should be rendered separately)
        
        Args:
            game_state: Current game state
        """
        if not self.screen:
            self.initialize()
        
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Render terrain
        self._render_terrain(game_state)
        
        # Render units
        self._render_units(game_state)
        
        # Render UI elements
        self._render_ui(game_state)
        
        # Update the display
        pygame.display.flip()
        
    def _render_terrain(self, game_state):
        """
        Render the terrain
        
        Args:
            game_state: Current game state
        """
        # Simplified terrain rendering for now
        # Draw a green grid to represent the ground
        grid_size = 50  # Size of grid cells in world units
        ground_color = (30, 100, 30)  # Dark green
        grid_color = (50, 120, 50)  # Lighter green
        
        # Calculate visible grid area
        view_range = 500 / self.camera_zoom  # How far we can see
        min_x = int((self.camera_position[0] - view_range) // grid_size) * grid_size
        max_x = int((self.camera_position[0] + view_range) // grid_size + 1) * grid_size
        min_y = int((self.camera_position[1] - view_range) // grid_size) * grid_size
        max_y = int((self.camera_position[1] + view_range) // grid_size + 1) * grid_size
        
        # Draw ground plane
        ground_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        pygame.draw.rect(self.screen, ground_color, ground_rect)
        
        # Draw grid lines
        for x in range(min_x, max_x, grid_size):
            start_pos = self.world_to_screen((x, min_y, 0))
            end_pos = self.world_to_screen((x, max_y, 0))
            pygame.draw.line(self.screen, grid_color, start_pos, end_pos, 1)
        
        for y in range(min_y, max_y, grid_size):
            start_pos = self.world_to_screen((min_x, y, 0))
            end_pos = self.world_to_screen((max_x, y, 0))
            pygame.draw.line(self.screen, grid_color, start_pos, end_pos, 1)
    
    def _render_units(self, game_state):
        """
        Render all units
        
        Args:
            game_state: Current game state
        """
        # Render player squads
        for squad in game_state.player_squads:
            # Render squad formation outline if selected
            if squad in game_state.selected_squads:
                self._render_squad_formation(squad, (0, 255, 0, 128))  # Green for player
            
            # Render each unit in the squad
            for unit in squad.units:
                self._render_unit(unit, selected=(unit in game_state.selected_units))
        
        # Render enemy squads
        for squad in game_state.enemy_squads:
            # No formation outline for enemies
            
            # Render each unit in the squad
            for unit in squad.units:
                self._render_unit(unit)
    
    def _render_squad_formation(self, squad, color):
        """
        Render the formation outline for a squad
        
        Args:
            squad: The squad to render formation for
            color: Color to use for the formation outline
        """
        # Get formation points
        formation_points = squad.get_formation_points()
        
        # Convert to screen coordinates
        screen_points = [self.world_to_screen((p[0], p[1], 0)) for p in formation_points]
        
        # Draw lines connecting the points
        if len(screen_points) > 1:
            pygame.draw.lines(self.screen, color, True, screen_points, 1)
    
    def _render_unit(self, unit, selected=False):
        """
        Render a single unit
        
        Args:
            unit: The unit to render
            selected: Whether the unit is selected
        """
        # Convert unit position to screen coordinates
        screen_pos = self.world_to_screen(unit.position)
        
        # Determine color based on faction and type
        if unit.faction == "player":
            if unit.__class__.__name__ == "Dimensioneer":
                color = (0, 0, 200)  # Blue
            elif unit.__class__.__name__ == "PortalArcher":
                color = (0, 200, 0)  # Green
            elif unit.__class__.__name__ == "TechGrenadier":
                color = (200, 100, 0)  # Orange
            else:
                color = (0, 0, 200)  # Default blue
        else:
            # Enemy units
            if unit.__class__.__name__ == "Gromflomite":
                color = (200, 0, 0)  # Red
            else:
                color = (150, 0, 0)  # Dark red
        
        # Draw the unit
        unit_radius = 8
        pygame.draw.circle(self.screen, color, screen_pos, unit_radius)
        
        # Draw selection indicator if selected
        if selected:
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, unit_radius + 3, 2)
        
        # Draw health bar
        health_pct = unit.health / unit.max_health
        bar_width = 20
        bar_height = 4
        bar_pos = (screen_pos[0] - bar_width // 2, screen_pos[1] - unit_radius - 8)
        
        # Background (black)
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (bar_pos[0], bar_pos[1], bar_width, bar_height))
        
        # Health fill (green to red based on health)
        health_color = (int(255 * (1 - health_pct)), int(255 * health_pct), 0)
        health_width = int(bar_width * health_pct)
        pygame.draw.rect(self.screen, health_color, 
                         (bar_pos[0], bar_pos[1], health_width, bar_height))
        
        # Draw unit state indicator
        if unit.state == "attacking":
            # Red attack indicator
            pygame.draw.circle(self.screen, (255, 0, 0), 
                               (screen_pos[0] + unit_radius + 3, screen_pos[1] - unit_radius - 3), 3)
        elif unit.state == "moving":
            # Green movement indicator
            pygame.draw.circle(self.screen, (0, 255, 0), 
                               (screen_pos[0] + unit_radius + 3, screen_pos[1] - unit_radius - 3), 3)
    
    def _render_ui(self, game_state):
        """
        Render UI elements
        
        Args:
            game_state: Current game state
        """
        # Draw selection info at bottom left
        if game_state.selected_squads or game_state.selected_units:
            self._render_selection_info(game_state)
        
        # Draw game time at top right
        time_text = f"Mission Time: {int(game_state.game_time // 60):02d}:{int(game_state.game_time % 60):02d}"
        time_surface = self.fonts['medium'].render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (self.screen_width - 150, 10))
        
        # Draw mission name at top
        title_surface = self.fonts['title'].render(game_state.mission_name, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 20))
        self.screen.blit(title_surface, title_rect)
    
    def _render_selection_info(self, game_state):
        """
        Render information about the current selection
        
        Args:
            game_state: Current game state
        """
        # Panel background
        panel_rect = pygame.Rect(10, self.screen_height - 100, 300, 90)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), panel_rect, 1)
        
        # If squads are selected
        if game_state.selected_squads:
            # Display squad info
            squad = game_state.selected_squads[0]  # Just show first squad for now
            
            # Squad name
            name_surface = self.fonts['large'].render(squad.name, True, (255, 255, 255))
            self.screen.blit(name_surface, (20, self.screen_height - 95))
            
            # Squad size
            size_text = f"Units: {len(squad.units)}"
            size_surface = self.fonts['medium'].render(size_text, True, (200, 200, 200))
            self.screen.blit(size_surface, (20, self.screen_height - 75))
            
            # Formation
            formation_text = f"Formation: {squad.formation_type.name}"
            formation_surface = self.fonts['medium'].render(formation_text, True, (200, 200, 200))
            self.screen.blit(formation_surface, (20, self.screen_height - 55))
            
            # Unit types
            unit_types = {}
            for unit in squad.units:
                unit_type = unit.__class__.__name__
                if unit_type in unit_types:
                    unit_types[unit_type] += 1
                else:
                    unit_types[unit_type] = 1
            
            unit_type_text = ", ".join([f"{count} {utype}" for utype, count in unit_types.items()])
            type_surface = self.fonts['small'].render(unit_type_text, True, (200, 200, 200))
            self.screen.blit(type_surface, (20, self.screen_height - 35))
        
        # If individual units are selected
        elif game_state.selected_units:
            # Count units by type
            unit_types = {}
            for unit in game_state.selected_units:
                unit_type = unit.__class__.__name__
                if unit_type in unit_types:
                    unit_types[unit_type] += 1
                else:
                    unit_types[unit_type] = 1
            
            # Display selection summary
            selection_text = f"Selected: {len(game_state.selected_units)} units"
            selection_surface = self.fonts['large'].render(selection_text, True, (255, 255, 255))
            self.screen.blit(selection_surface, (20, self.screen_height - 95))
            
            # Unit types
            unit_type_text = ", ".join([f"{count} {utype}" for utype, count in unit_types.items()])
            type_surface = self.fonts['medium'].render(unit_type_text, True, (200, 200, 200))
            self.screen.blit(type_surface, (20, self.screen_height - 75))
            
            # If a single unit is selected, show more details
            if len(game_state.selected_units) == 1:
                unit = game_state.selected_units[0]
                health_text = f"Health: {int(unit.health)}/{int(unit.max_health)}"
                health_surface = self.fonts['medium'].render(health_text, True, (200, 200, 200))
                self.screen.blit(health_surface, (20, self.screen_height - 55))
                
                # Show special attributes if any
                if hasattr(unit, 'special_cooldown'):
                    cooldown_text = f"Special: {int(unit.special_cooldown_remaining)}s cooldown"
                    if unit.special_cooldown_remaining <= 0:
                        cooldown_text = "Special: Ready"
                    cooldown_surface = self.fonts['medium'].render(cooldown_text, True, (200, 200, 200))
                    self.screen.blit(cooldown_surface, (20, self.screen_height - 35))
    
    def move_camera(self, dx, dy, delta_zoom=0, delta_rotation=0):
        """
        Move the camera position and change zoom/rotation
        
        Args:
            dx, dy: Delta movement in screen space
            delta_zoom: Change in zoom factor
            delta_rotation: Change in rotation (degrees)
        """
        # Adjust for rotation when moving
        rot_rad = np.radians(self.camera_rotation)
        world_dx = dx * np.cos(rot_rad) - dy * np.sin(rot_rad)
        world_dy = dx * np.sin(rot_rad) + dy * np.cos(rot_rad)
        
        # Apply movement
        self.camera_position = (
            self.camera_position[0] + world_dx / self.camera_zoom,
            self.camera_position[1] + world_dy / self.camera_zoom,
            self.camera_position[2]  # Height stays the same
        )
        
        # Apply zoom (with limits)
        self.camera_zoom = max(0.2, min(5.0, self.camera_zoom + delta_zoom))
        
        # Apply rotation
        self.camera_rotation = (self.camera_rotation + delta_rotation) % 360
