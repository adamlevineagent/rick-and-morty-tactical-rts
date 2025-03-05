import pygame
import numpy as np

class Renderer:
    """
    The Renderer class handles all drawing operations for the game.
    It manages the camera, terrain rendering, and sprite rendering.
    """
    
    def __init__(self, display):
        """
        Initialize the renderer.
        
        Args:
            display: The pygame display surface to render to
        """
        self.display = display
        self.width, self.height = display.get_size()
        
        # Camera settings
        self.camera_angle = 0  # 0-7 for 8 fixed angles (45 degree increments)
        self.camera_zoom = 1.0
        self.camera_pitch = 45  # degrees from overhead
        self.camera_position = [0, 0]  # Center position in world coordinates
        
        # Create surfaces for layers
        self.terrain_surface = pygame.Surface((self.width, self.height))
        self.unit_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.ui_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Debug options
        self.show_grid = True
        self.show_fps = True
        
        # Load test textures (temporary)
        self.terrain_texture = self._create_test_terrain()
        
    def _create_test_terrain(self):
        """Create a temporary test terrain texture"""
        size = 256
        terrain = pygame.Surface((size, size))
        
        # Create a checkerboard pattern
        square_size = 32
        for y in range(0, size, square_size):
            for x in range(0, size, square_size):
                color = (100, 180, 100) if (x // square_size + y // square_size) % 2 == 0 else (80, 150, 80)
                pygame.draw.rect(terrain, color, (x, y, square_size, square_size))
                
        return terrain
    
    def rotate_camera(self, direction):
        """Rotate camera by 45 degrees in the specified direction"""
        self.camera_angle = (self.camera_angle + direction) % 8
        print(f"Camera angle: {self.camera_angle * 45} degrees")
    
    def zoom_camera(self, amount):
        """Zoom camera in or out"""
        self.camera_zoom = max(0.5, min(2.0, self.camera_zoom + amount))
        print(f"Camera zoom: {self.camera_zoom:.2f}")
    
    def adjust_pitch(self, amount):
        """Adjust camera pitch within limits"""
        self.camera_pitch = max(30, min(60, self.camera_pitch + amount))
        print(f"Camera pitch: {self.camera_pitch} degrees")
    
    def move_camera(self, dx, dy):
        """Move camera position"""
        self.camera_position[0] += dx
        self.camera_position[1] += dy
    
    def world_to_screen(self, world_x, world_y, height=0):
        """
        Convert world coordinates to screen coordinates
        
        Args:
            world_x, world_y: Position in world space
            height: Height of the point above the terrain
            
        Returns:
            (screen_x, screen_y): Position in screen space
        """
        # Adjust for camera position
        rel_x = world_x - self.camera_position[0]
        rel_y = world_y - self.camera_position[1]
        
        # Apply camera rotation
        angle_rad = self.camera_angle * np.pi / 4
        rot_x = rel_x * np.cos(angle_rad) - rel_y * np.sin(angle_rad)
        rot_y = rel_x * np.sin(angle_rad) + rel_y * np.cos(angle_rad)
        
        # Apply perspective and camera pitch
        pitch_factor = np.cos(self.camera_pitch * np.pi / 180)
        screen_x = self.width / 2 + rot_x * self.camera_zoom
        screen_y = self.height / 2 + (rot_y * pitch_factor - height) * self.camera_zoom
        
        return int(screen_x), int(screen_y)
    
    def _render_terrain(self, game_state):
        """Render the terrain"""
        # Clear the terrain surface
        self.terrain_surface.fill((0, 0, 0))
        
        # Get terrain dimensions and heightmap from game state
        # For now, use test terrain
        terrain_size = 2000  # World units
        grid_size = 100  # Grid spacing
        
        # Calculate visible grid bounds
        visible_width = self.width / self.camera_zoom
        visible_height = self.height / self.camera_zoom
        min_x = self.camera_position[0] - visible_width / 2
        max_x = self.camera_position[0] + visible_width / 2
        min_y = self.camera_position[1] - visible_height / 2
        max_y = self.camera_position[1] + visible_height / 2
        
        # Draw a grid for now (temporary terrain visualization)
        if self.show_grid:
            for x in range(int(min_x // grid_size) * grid_size, int(max_x // grid_size + 1) * grid_size, grid_size):
                for y in range(int(min_y // grid_size) * grid_size, int(max_y // grid_size + 1) * grid_size, grid_size):
                    # Convert grid corner to screen coordinates
                    screen_x, screen_y = self.world_to_screen(x, y)
                    
                    # Draw a tile from the terrain texture
                    tile_rect = pygame.Rect(0, 0, self.terrain_texture.get_width(), self.terrain_texture.get_height())
                    dest_rect = pygame.Rect(
                        screen_x, 
                        screen_y, 
                        grid_size * self.camera_zoom, 
                        grid_size * self.camera_zoom * np.cos(self.camera_pitch * np.pi / 180)
                    )
                    self.terrain_surface.blit(pygame.transform.scale(self.terrain_texture, dest_rect.size), dest_rect)
        
    def _render_units(self, game_state):
        """Render all units"""
        # Clear the unit surface
        self.unit_surface.fill((0, 0, 0, 0))
        
        # Placeholder: draw some test units
        # In the actual implementation, we would iterate through all units in the game state
        test_units = [
            {"position": (0, 0), "color": (255, 0, 0), "radius": 20},
            {"position": (100, 100), "color": (0, 0, 255), "radius": 20},
            {"position": (-100, 50), "color": (0, 255, 0), "radius": 20}
        ]
        
        for unit in test_units:
            pos = unit["position"]
            screen_x, screen_y = self.world_to_screen(pos[0], pos[1])
            pygame.draw.circle(self.unit_surface, unit["color"], (screen_x, screen_y), unit["radius"])
    
    def _render_ui(self, game_state):
        """Render the user interface"""
        # Clear the UI surface
        self.ui_surface.fill((0, 0, 0, 0))
        
        # Draw a simple frame for the UI at the bottom
        ui_height = 100
        pygame.draw.rect(self.ui_surface, (40, 40, 40, 200), (0, self.height - ui_height, self.width, ui_height))
        pygame.draw.rect(self.ui_surface, (100, 100, 100, 255), (0, self.height - ui_height, self.width, ui_height), 2)
        
        # Add some UI text
        font = pygame.font.SysFont(None, 24)
        angle_text = font.render(f"Camera Angle: {self.camera_angle * 45}°", True, (255, 255, 255))
        zoom_text = font.render(f"Zoom: {self.camera_zoom:.2f}x", True, (255, 255, 255))
        pitch_text = font.render(f"Pitch: {self.camera_pitch}°", True, (255, 255, 255))
        
        self.ui_surface.blit(angle_text, (10, self.height - ui_height + 10))
        self.ui_surface.blit(zoom_text, (10, self.height - ui_height + 40))
        self.ui_surface.blit(pitch_text, (10, self.height - ui_height + 70))
        
        # Add help text
        help_text = font.render("Arrow keys: Move  Q/E: Rotate  W/S: Pitch  Z/X: Zoom  ESC: Quit", True, (255, 255, 255))
        self.ui_surface.blit(help_text, (self.width // 2 - help_text.get_width() // 2, self.height - ui_height + 40))
        
    def render(self, game_state):
        """
        Main render function - draws everything to the display
        
        Args:
            game_state: The current GameState object
        """
        # Clear the display
        self.display.fill((0, 0, 0))
        
        # Render each layer
        self._render_terrain(game_state)
        self._render_units(game_state)
        self._render_ui(game_state)
        
        # Composite layers onto the display
        self.display.blit(self.terrain_surface, (0, 0))
        self.display.blit(self.unit_surface, (0, 0))
        self.display.blit(self.ui_surface, (0, 0))
