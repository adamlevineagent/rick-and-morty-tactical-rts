import pygame
import numpy as np
from pygame.locals import *
import math
from typing import List, Dict, Any, Tuple, Optional

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
        self.selection_changed = False
        
        # For double click detection
        self.last_click_time = 0
        self.last_click_position = (0, 0)
        self.double_click_threshold = 300  # milliseconds
        
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
            
            # Clear selection with Escape
            if event.key == K_ESCAPE:
                self.selected_units = []
                self.selection_changed = True
                
        elif event.type == KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = False
                
            # Reset camera controls
            if event.key == K_q or event.key == K_e:
                self.camera_rotation = 0
            elif event.key == K_z or event.key == K_x:
                self.camera_zoom = 0
                
        elif event.type == MOUSEMOTION:
            self.mouse_position = event.pos
            
            # Edge scrolling - determine screen size
            w, h = pygame.display.get_surface().get_size()
            edge_size = 20  # pixels from edge that triggers scrolling
            
            # Reset camera movement first
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
                    # Check if this is a double click
                    current_time = pygame.time.get_ticks()
                    click_position = event.pos
                    
                    # Calculate distance between this click and last click
                    dx = click_position[0] - self.last_click_position[0]
                    dy = click_position[1] - self.last_click_position[1]
                    click_distance = math.sqrt(dx*dx + dy*dy)
                    
                    is_double_click = (current_time - self.last_click_time < self.double_click_threshold and 
                                      click_distance < 10)  # Must be close to same spot
                    
                    # Store this click for next double click check
                    self.last_click_time = current_time
                    self.last_click_position = click_position
                    
                    # Start selection - drag box or single click
                    self.selection_start = event.pos
                    self.is_selecting = True
                    
                    # Add selection command to queue
                    self.command_queue.append({
                        "type": "selection_start",
                        "position": event.pos,
                        "shift_held": self.keys_pressed.get(K_LSHIFT, False) or self.keys_pressed.get(K_RSHIFT, False),
                        "is_double_click": is_double_click
                    })
                
                elif event.button == 3:  # Right button
                    # Issue command with selected units
                    if len(self.selected_units) > 0:
                        # Check if attack modifier key is being held (Alt)
                        is_attack = self.keys_pressed.get(K_LALT, False) or self.keys_pressed.get(K_RALT, False)
                        
                        self.command_queue.append({
                            "type": "unit_command",
                            "units": self.selected_units.copy(),
                            "target_position": event.pos,
                            "command": "attack" if is_attack else "move"
                        })
                
        elif event.type == MOUSEBUTTONUP:
            if event.button <= 3:  # Only handle the main three buttons
                self.mouse_buttons[event.button - 1] = False
                
                if event.button == 1:  # Left button
                    # End selection
                    self.is_selecting = False
                    
                    # Calculate selection size
                    start_x, start_y = self.selection_start
                    end_x, end_y = event.pos
                    width = abs(end_x - start_x)
                    height = abs(end_y - start_y)
                    
                    # Determine if this is a point selection or a box selection
                    is_point_selection = (width < 5 and height < 5)
                    
                    # Add selection end command to queue with additional metadata
                    self.command_queue.append({
                        "type": "selection_end",
                        "start": self.selection_start,
                        "end": event.pos,
                        "is_point_selection": is_point_selection,
                        "shift_held": self.keys_pressed.get(K_LSHIFT, False) or self.keys_pressed.get(K_RSHIFT, False)
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
        Apply camera controls to the renderer
        
        Args:
            renderer: Game renderer to apply camera controls to
        """
        # Camera movement
        if self.camera_move[0] != 0 or self.camera_move[1] != 0:
            # Calculate movement direction
            dx = self.camera_move[0] * 5.0  # Increase speed from default
            dy = self.camera_move[1] * 5.0  # Increase speed from default
            
            # Apply rotation to movement direction
            angle = renderer.camera_rotation
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            
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
            rotation_speed = 0.04  # Double the rotation speed
            renderer.camera_rotation += self.camera_rotation * rotation_speed
            
        # Camera zoom
        if self.camera_zoom != 0:
            zoom_factor = 1.15 if self.camera_zoom > 0 else 0.85  # More dramatic zoom
            renderer.camera_zoom *= zoom_factor
            # Clamp zoom range
            renderer.camera_zoom = max(0.1, min(50.0, renderer.camera_zoom))
            
        # Camera pitch
        if self.camera_pitch != 0:
            pitch_speed = 2.0
            new_pitch = renderer.camera_pitch + self.camera_pitch * pitch_speed
            # Clamp pitch to reasonable range
            renderer.camera_pitch = max(10.0, min(80.0, new_pitch))

    def select_units(self, game_state, renderer, selection_rect, is_point_selection, shift_held, is_double_click=False):
        """
        Select units based on the provided selection criteria
        
        Args:
            game_state: Current game state
            renderer: Game renderer
            selection_rect: (x, y, width, height) of selection rectangle in screen space
            is_point_selection: True if single point click, False if drag selection
            shift_held: Whether shift key is held (add to current selection)
            is_double_click: Whether this was a double-click (selects all of same type)
        """
        # Get all player units for selection
        all_units = []
        for squad in game_state.player_squads:
            all_units.extend(squad.units)
            
        # Units we will include in new selection
        newly_selected = []
        
        # Check if a unit was clicked directly (point selection)
        if is_point_selection:
            clicked_unit = None
            
            # Find the unit that was clicked
            for unit in all_units:
                screen_pos = renderer.world_to_screen(unit.position)
                # Distance from click to unit center
                dx = screen_pos[0] - selection_rect[0]
                dy = screen_pos[1] - selection_rect[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Radius for selection depends on unit type and zoom
                unit_size = max(10, int(15 * renderer.camera_zoom / 10))
                
                if distance <= unit_size:
                    clicked_unit = unit
                    break
            
            if clicked_unit:
                if is_double_click:
                    # Double click - select all units of same type on screen
                    for unit in all_units:
                        if unit.type == clicked_unit.type:
                            screen_pos = renderer.world_to_screen(unit.position)
                            # Only select if on screen
                            screen_w, screen_h = pygame.display.get_surface().get_size()
                            if (0 <= screen_pos[0] <= screen_w and 
                                0 <= screen_pos[1] <= screen_h):
                                newly_selected.append(unit)
                else:
                    # Single click - select just this unit
                    newly_selected.append(clicked_unit)
        else:
            # Drag selection - select all units in the rectangle
            x, y, w, h = selection_rect
            for unit in all_units:
                screen_pos = renderer.world_to_screen(unit.position)
                if (x <= screen_pos[0] <= x + w and
                    y <= screen_pos[1] <= y + h):
                    newly_selected.append(unit)
        
        # Update the selection
        if shift_held:
            # With shift held, add/remove from current selection
            for unit in newly_selected:
                if unit in self.selected_units:
                    self.selected_units.remove(unit)
                else:
                    self.selected_units.append(unit)
        else:
            # Without shift, replace current selection
            self.selected_units = newly_selected
        
        # Mark that selection has changed
        self.selection_changed = True
