import pygame
from pygame.locals import *

class InputHandler:
    """
    Handles all input from the player and converts it into game commands.
    Processes keyboard, mouse, and UI interactions.
    """
    
    def __init__(self):
        # Initialize state dictionaries
        self.keys_pressed = {}
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, middle, right
        
        # Selection state
        self.selection_start = None
        self.is_selecting = False
        self.selected_units = []
        
        # Camera control state
        self.camera_move = [0, 0]  # x, y movement direction
        self.camera_rotation = 0  # -1 for counterclockwise, 1 for clockwise
        self.camera_zoom = 0  # -1 for zoom out, 1 for zoom in
        self.camera_pitch = 0  # -1 for lower pitch, 1 for higher pitch
        
        # Command queue - will be processed by the game state
        self.command_queue = []
    
    def process_event(self, event):
        """
        Process a pygame event and update input state accordingly
        
        Args:
            event: A pygame event object
        """
        # Handle keyboard events
        if event.type == KEYDOWN:
            self.keys_pressed[event.key] = True
            
            # Camera rotation
            if event.key == K_q:
                self.camera_rotation = -1
            elif event.key == K_e:
                self.camera_rotation = 1
                
            # Camera zoom
            if event.key == K_z:
                self.camera_zoom = -1
            elif event.key == K_x:
                self.camera_zoom = 1
                
            # Camera pitch
            if event.key == K_w:
                self.camera_pitch = -1
            elif event.key == K_s:
                self.camera_pitch = 1
            
        elif event.type == KEYUP:
            self.keys_pressed[event.key] = False
            
            # Reset camera controls if key is released
            if event.key == K_q and self.camera_rotation == -1:
                self.camera_rotation = 0
            elif event.key == K_e and self.camera_rotation == 1:
                self.camera_rotation = 0
                
            if event.key == K_z and self.camera_zoom == -1:
                self.camera_zoom = 0
            elif event.key == K_x and self.camera_zoom == 1:
                self.camera_zoom = 0
                
            if event.key == K_w and self.camera_pitch == -1:
                self.camera_pitch = 0
            elif event.key == K_s and self.camera_pitch == 1:
                self.camera_pitch = 0
        
        # Handle mouse events
        elif event.type == MOUSEMOTION:
            self.mouse_position = event.pos
            
            # Check for edge scrolling
            edge_size = 20
            w, h = pygame.display.get_surface().get_size()
            
            # Reset movement direction
            self.camera_move = [0, 0]
            
            # Edge scrolling - check if mouse is near screen edges
            if event.pos[0] < edge_size:
                self.camera_move[0] = -1
            elif event.pos[0] > w - edge_size:
                self.camera_move[0] = 1
                
            if event.pos[1] < edge_size:
                self.camera_move[1] = -1
            elif event.pos[1] > h - edge_size:
                self.camera_move[1] = 1
            
            # Handle drag selection
            if self.is_selecting:
                # Update selection rectangle end point
                pass
                
        elif event.type == MOUSEBUTTONDOWN:
            if event.button <= 3:  # Only handle the main three buttons
                self.mouse_buttons[event.button - 1] = True
                
                if event.button == 1:  # Left button
                    # Start selection
                    self.selection_start = event.pos
                    self.is_selecting = True
                    
                    # Add selection command to queue
                    self.command_queue.append({
                        "type": "selection_start",
                        "position": event.pos
                    })
                
                elif event.button == 3:  # Right button
                    # Issue command with selected units
                    if len(self.selected_units) > 0:
                        self.command_queue.append({
                            "type": "unit_command",
                            "units": self.selected_units.copy(),
                            "target_position": event.pos,
                            "command": "move"  # Default command is move
                        })
                
        elif event.type == MOUSEBUTTONUP:
            if event.button <= 3:  # Only handle the main three buttons
                self.mouse_buttons[event.button - 1] = False
                
                if event.button == 1:  # Left button
                    # End selection
                    self.is_selecting = False
                    
                    # Add selection end command to queue
                    self.command_queue.append({
                        "type": "selection_end",
                        "start": self.selection_start,
                        "end": event.pos
                    })
                    
    def _handle_keyboard_input(self):
        """Handle sustained keyboard input (keys being held down)"""
        # Arrow keys for camera movement
        if self.keys_pressed.get(K_LEFT, False):
            self.camera_move[0] = -1
        elif self.keys_pressed.get(K_RIGHT, False):
            self.camera_move[0] = 1
            
        if self.keys_pressed.get(K_UP, False):
            self.camera_move[1] = -1
        elif self.keys_pressed.get(K_DOWN, False):
            self.camera_move[1] = 1
    
    def get_commands(self):
        """
        Get the current command queue and reset it
        
        Returns:
            The current command queue
        """
        commands = self.command_queue
        self.command_queue = []
        return commands

    def process_events(self, events, renderer=None):
        """
        Process a list of pygame events
        
        Args:
            events: List of pygame events to process
            renderer: Optional renderer for world-to-screen conversions
        """
        for event in events:
            self.process_event(event)
            
        # After processing events, handle continuous inputs
        self._handle_continuous_inputs(renderer)
        
    def _handle_continuous_inputs(self, renderer=None):
        """
        Handle continuous inputs like held keys and edge scrolling
        
        Args:
            renderer: Optional renderer for camera control
        """
        # Handle WASD and arrow keys for camera movement
        if self.keys_pressed.get(K_w) or self.keys_pressed.get(K_UP):
            self.camera_move[1] = -1
        elif self.keys_pressed.get(K_s) or self.keys_pressed.get(K_DOWN):
            self.camera_move[1] = 1
        else:
            self.camera_move[1] = 0
            
        if self.keys_pressed.get(K_a) or self.keys_pressed.get(K_LEFT):
            self.camera_move[0] = -1
        elif self.keys_pressed.get(K_d) or self.keys_pressed.get(K_RIGHT):
            self.camera_move[0] = 1
        else:
            self.camera_move[0] = 0
            
        # Handle camera rotation with Q and E
        if self.keys_pressed.get(K_q):
            self.camera_rotation = -1
        elif self.keys_pressed.get(K_e):
            self.camera_rotation = 1
        else:
            self.camera_rotation = 0
            
        # Handle camera zoom with Z and X or mouse wheel
        if self.keys_pressed.get(K_z):
            self.camera_zoom = -1
        elif self.keys_pressed.get(K_x):
            self.camera_zoom = 1
        # Mouse wheel is handled in the process_event method
        
        # Handle camera pitch with R and F
        if self.keys_pressed.get(K_r):
            self.camera_pitch = 1
        elif self.keys_pressed.get(K_f):
            self.camera_pitch = -1
        else:
            self.camera_pitch = 0
            
        # Apply camera controls to renderer if provided
        if renderer:
            self._apply_camera_controls(renderer)
            
    def _apply_camera_controls(self, renderer):
        """
        Apply camera control inputs to the provided renderer
        
        Args:
            renderer: The game renderer to control
        """
        # Camera movement
        move_speed = 5.0 * (1.0 / max(0.1, renderer.camera_zoom))  # Slower movement when zoomed in
        if self.camera_move[0] != 0 or self.camera_move[1] != 0:
            # Convert to world space direction
            dx = self.camera_move[0] * move_speed
            dy = self.camera_move[1] * move_speed
            
            # Apply rotation to movement direction
            angle = renderer.camera_rotation
            cos_angle = pygame.math.cos(angle)
            sin_angle = pygame.math.sin(angle)
            
            # Rotate movement vector
            moved_x = dx * cos_angle - dy * sin_angle
            moved_y = dx * sin_angle + dy * cos_angle
            
            # Update camera position
            renderer.camera_position = (
                renderer.camera_position[0] + moved_x,
                renderer.camera_position[1] + moved_y,
                renderer.camera_position[2]
            )
        
        # Camera rotation
        if self.camera_rotation != 0:
            rotation_speed = 0.02
            renderer.camera_rotation += self.camera_rotation * rotation_speed
            
        # Camera zoom
        if self.camera_zoom != 0:
            zoom_factor = 1.1 if self.camera_zoom > 0 else 0.9
            renderer.camera_zoom *= zoom_factor
            # Clamp zoom range
            renderer.camera_zoom = max(0.1, min(50.0, renderer.camera_zoom))
            
        # Camera pitch
        if self.camera_pitch != 0:
            pitch_speed = 2.0
            new_pitch = renderer.camera_pitch + self.camera_pitch * pitch_speed
            # Clamp pitch to reasonable range
            renderer.camera_pitch = max(10.0, min(80.0, new_pitch))
