import pygame
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import math

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
    
    def screen_to_world(self, screen_pos):
        """
        Convert screen coordinates to world coordinates
        
        Args:
            screen_pos: 2D screen position (x, y)
            
        Returns:
            3D world position (x, y, 0) - z is always 0 for ground level
        """
        # Get relative screen position from center
        rel_screen_x = screen_pos[0] - self.screen_width // 2
        rel_screen_y = screen_pos[1] - self.screen_height // 2
        
        # Apply inverse scaling (zoom)
        scale = self.camera_zoom
        rel_x = rel_screen_x / scale
        rel_y = rel_screen_y / scale
        
        # Apply inverse camera rotation
        rot_rad = self.camera_rotation
        cos_rot = np.cos(rot_rad)
        sin_rot = np.sin(rot_rad)
        
        world_rel_x = rel_x * cos_rot + rel_y * sin_rot
        world_rel_y = -rel_x * sin_rot + rel_y * cos_rot
        
        # Apply camera position offset
        world_x = world_rel_x + self.camera_position[0]
        world_y = world_rel_y + self.camera_position[1]
        
        return (world_x, world_y, 0)  # Z is assumed to be 0 (ground level)
    
    def render_game(self, game_state, physics_engine):
        """
        Render the complete game scene
        
        Args:
            game_state: Current game state
            physics_engine: Physics engine instance for rendering effects
        """
        # Initialize the screen if it hasn't been set
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Render terrain grid for orientation
        self._render_terrain_grid()
        
        # Render squads and units
        self._render_player_squads(game_state.player_squads)
        self._render_enemy_squads(game_state.enemy_squads)
        
        # Render projectiles and effects from physics engine
        self._render_physics_effects(physics_engine)
        
        # Render UI elements
        self._render_ui(game_state)
    
    def render_game_state(self, game_state, physics_engine=None):
        """Alias for render_game for compatibility"""
        self.render_game(game_state, physics_engine)
    
    def _render_player_squads(self, squads):
        """Render all player squads and their units"""
        for squad in squads:
            self._render_squad(squad, (0, 255, 0), True)  # Green for player
    
    def _render_enemy_squads(self, squads):
        """Render all enemy squads and their units"""
        for squad in squads:
            self._render_squad(squad, (255, 0, 0), False)  # Red for enemies
            
    def _render_squad(self, squad, color, is_player=True):
        """Render a squad and all its units"""
        # Render each unit in the squad
        for unit in squad.units:
            # Get unit's screen position
            screen_pos = self.world_to_screen(unit.position)
            
            # Skip if off screen
            if (screen_pos[0] < -50 or screen_pos[0] > self.screen_width + 50 or
                screen_pos[1] < -50 or screen_pos[1] > self.screen_height + 50):
                continue
            
            # Determine unit size based on zoom
            unit_size = max(5, int(10 * self.camera_zoom / 10))
            
            # Check if unit is selected
            is_selected = hasattr(self, 'input_handler') and unit in getattr(self, 'input_handler').selected_units
            
            # Draw outline if selected
            if is_selected:
                pygame.draw.circle(self.screen, (255, 255, 0), screen_pos, unit_size + 3)
            
            # Determine color and shape based on unit type
            unit_type = unit.type if hasattr(unit, 'type') else "unknown"
            
            # Player vs enemy base colors
            player_base = (80, 120, 255) if is_player else (200, 0, 0)
            player_highlight = (140, 180, 255) if is_player else (255, 100, 100)
            
            # Unit-specific rendering based on type
            if unit_type == "dimensioneer":
                # SWORD-SHAPED for Dimensioneer (melee warriors)
                # Base color
                sword_color = (0, 100, 255) if is_player else (200, 0, 0)
                # Draw sword hilt/guard (horizontal rectangle)
                hilt_width = unit_size * 1.6
                hilt_height = unit_size * 0.5
                hilt_rect = pygame.Rect(
                    screen_pos[0] - hilt_width/2,
                    screen_pos[1] - hilt_height/2,
                    hilt_width,
                    hilt_height
                )
                pygame.draw.rect(self.screen, sword_color, hilt_rect)
                
                # Draw sword blade (vertical rectangle)
                blade_width = unit_size * 0.4
                blade_height = unit_size * 2.2
                blade_rect = pygame.Rect(
                    screen_pos[0] - blade_width/2,
                    screen_pos[1] - blade_height/2,
                    blade_width,
                    blade_height
                )
                pygame.draw.rect(self.screen, (200, 230, 255) if is_player else (255, 150, 150), blade_rect)
                
                # Draw sword point (triangle)
                blade_top = screen_pos[1] - blade_height/2
                point_height = unit_size * 0.6
                triangle_points = [
                    (screen_pos[0] - blade_width/2, blade_top),
                    (screen_pos[0] + blade_width/2, blade_top),
                    (screen_pos[0], blade_top - point_height)
                ]
                pygame.draw.polygon(self.screen, (200, 230, 255) if is_player else (255, 150, 150), triangle_points)
                
            elif unit_type == "portal_archer":
                # BOW-SHAPED for Portal Archer (ranged units)
                # Draw bow curve (arc)
                bow_color = (0, 180, 0) if is_player else (180, 0, 0)
                bow_rect = pygame.Rect(
                    screen_pos[0] - unit_size,
                    screen_pos[1] - unit_size,
                    unit_size * 2,
                    unit_size * 2
                )
                
                # Calculate arrow angle based on unit rotation
                rotation = unit.rotation if hasattr(unit, 'rotation') else 0
                arrow_angle = math.radians(90 - rotation)  # Convert to radians and adjust
                
                # Draw the bow (semicircle) rotated to face the same direction as unit
                start_angle = arrow_angle - math.pi/2
                end_angle = arrow_angle + math.pi/2
                pygame.draw.arc(self.screen, bow_color, bow_rect, start_angle, end_angle, width=max(2, int(unit_size/4)))
                
                # Draw arrow (line with arrowhead)
                arrow_length = unit_size * 1.5
                arrow_end_x = screen_pos[0] + arrow_length * math.cos(arrow_angle)
                arrow_end_y = screen_pos[1] - arrow_length * math.sin(arrow_angle)
                pygame.draw.line(self.screen, (100, 255, 100) if is_player else (255, 100, 100), 
                                screen_pos, (arrow_end_x, arrow_end_y), max(1, int(unit_size/5)))
                
                # Arrowhead
                arrowhead_size = unit_size * 0.4
                left_angle = arrow_angle + math.pi * 3/4
                right_angle = arrow_angle - math.pi * 3/4
                left_point = (arrow_end_x + arrowhead_size * math.cos(left_angle),
                             arrow_end_y - arrowhead_size * math.sin(left_angle))
                right_point = (arrow_end_x + arrowhead_size * math.cos(right_angle),
                              arrow_end_y - arrowhead_size * math.sin(right_angle))
                pygame.draw.polygon(self.screen, (100, 255, 100) if is_player else (255, 100, 100), 
                                    [(arrow_end_x, arrow_end_y), left_point, right_point])
                
            elif unit_type == "tech_grenadier":
                # GRENADE/BOMB-SHAPED for Tech Grenadier
                grenade_color = (200, 130, 0) if is_player else (200, 0, 0)
                
                # Draw grenade body (circle)
                pygame.draw.circle(self.screen, grenade_color, screen_pos, unit_size)
                
                # Draw pin and handle
                pin_offset = unit_size * 0.7
                pin_pos = (screen_pos[0], screen_pos[1] - pin_offset)
                pin_size = unit_size * 0.4
                pygame.draw.circle(self.screen, (150, 150, 150), pin_pos, pin_size)
                
                # Draw handle
                handle_start = (screen_pos[0], screen_pos[1] - pin_offset + pin_size)
                handle_end = (screen_pos[0] + unit_size, screen_pos[1] - unit_size * 1.2)
                pygame.draw.line(self.screen, (150, 150, 150), handle_start, handle_end, max(1, int(unit_size/5)))
                
                # Draw warning markings
                warning_rect = pygame.Rect(
                    screen_pos[0] - unit_size * 0.5,
                    screen_pos[1] - unit_size * 0.5,
                    unit_size,
                    unit_size
                )
                # Add warning stripes
                stripe_width = max(1, int(unit_size/4))
                pygame.draw.line(self.screen, (0, 0, 0), 
                                (warning_rect.left, warning_rect.top), 
                                (warning_rect.right, warning_rect.bottom), stripe_width)
                pygame.draw.line(self.screen, (0, 0, 0), 
                                (warning_rect.left, warning_rect.bottom), 
                                (warning_rect.right, warning_rect.top), stripe_width)
                
            else:
                # Default unit: Triangle pointing in direction of rotation
                rotation = unit.rotation if hasattr(unit, 'rotation') else 0
                angle_rad = math.radians(rotation)
                
                # Calculate triangle points based on unit's rotation
                point1 = (screen_pos[0] + unit_size * math.cos(angle_rad),
                        screen_pos[1] - unit_size * math.sin(angle_rad))
                point2 = (screen_pos[0] + unit_size * math.cos(angle_rad + 2.5),
                        screen_pos[1] - unit_size * math.sin(angle_rad + 2.5))
                point3 = (screen_pos[0] + unit_size * math.cos(angle_rad - 2.5),
                        screen_pos[1] - unit_size * math.sin(angle_rad - 2.5))
                
                # Draw triangle
                pygame.draw.polygon(self.screen, color, [point1, point2, point3])
            
            # Draw unit type indicator label only when zoomed in enough
            if self.camera_zoom > 10:
                small_font = pygame.font.SysFont('Arial', 10)
                type_text = small_font.render(unit_type[:4], True, (255, 255, 255))
                self.screen.blit(type_text, (screen_pos[0] - type_text.get_width()//2, screen_pos[1] + unit_size + 2))
            
            # Show health bar for units
            health_pct = unit.health / unit.max_health
            health_width = int(unit_size * 2 * health_pct)
            health_height = max(1, int(unit_size / 3))
            
            # Position health bar above unit
            health_x = screen_pos[0] - unit_size
            health_y = screen_pos[1] - unit_size - health_height - 2
            
            # Background (gray)
            pygame.draw.rect(self.screen, (100, 100, 100), 
                         (health_x, health_y, unit_size * 2, health_height))
            
            # Foreground (green to red based on health)
            health_color = (int(255 * (1 - health_pct)), int(255 * health_pct), 0)
            pygame.draw.rect(self.screen, health_color, 
                         (health_x, health_y, health_width, health_height))
            
            # Draw unit's state or destination if moving
            if unit.state == "moving" and hasattr(unit, 'destination'):
                # Get destination screen position
                dest_screen = self.world_to_screen(unit.destination)
                
                # Draw line to destination
                pygame.draw.line(self.screen, (150, 150, 150), screen_pos, dest_screen, 1)
    
    def _render_terrain_grid(self):
        """
        Render the terrain grid for orientation
        
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
    
    def _render_physics_effects(self, physics_engine):
        """
        Render physics effects
        
        Args:
            physics_engine: Physics engine instance
        """
        # Render projectiles and effects from physics engine
        physics_engine.render(self.screen, self)
    
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
