#!/usr/bin/env python3
import os
import sys
import pygame
import time
import math
import random
from pygame.locals import *

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our game modules
from engine.renderer.game_renderer import GameRenderer
from engine.physics.physics_engine import PhysicsEngine
from engine.input.input_handler import InputHandler
from game.game_state import GameState
from game.mission.mission_manager import MissionManager
from game.units.dimensioneer import Dimensioneer
from game.units.portal_archer import PortalArcher
from game.units.squad import Squad

# Initialize pygame
pygame.init()

# Set up the display
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mission Test - Tactical RTS Game")

# Create the game state
game_state = GameState(mission_mode=True)

# Create the mission manager and load missions
mission_manager = MissionManager()
mission_manager.create_default_missions()
mission_manager.load_all_missions()

# Start the first mission
first_mission_id = list(mission_manager.missions.keys())[0]
mission_manager.start_mission(first_mission_id, game_state)

# Create the game renderer, physics engine, and input handler
renderer = GameRenderer(screen)
input_handler = InputHandler()
physics_engine = PhysicsEngine(renderer)

# Give renderer access to input handler for selection rendering
renderer.input_handler = input_handler

# Set up camera position
renderer.camera_position = (0, 0, 50)  # Z is height
renderer.camera_zoom = 15

# Set up time tracking
clock = pygame.time.Clock()
last_fire_time = 0
last_spawn_time = 0
last_enemy_spawn_time = 0

# Set up fonts
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 16)

# Debug info display
show_debug = True

# Function to spawn enemy units for testing
def spawn_enemy_unit(game_state, position=None):
    """Spawn an enemy unit at the given position or a random position"""
    # Generate random position if none provided
    if position is None:
        # Spawn within visible area of the camera
        cam_x, cam_y = renderer.camera_position[0], renderer.camera_position[1]
        view_range = 40  # Units
        position = (
            cam_x + random.uniform(-view_range/2, view_range/2),
            cam_y + random.uniform(-view_range/2, view_range/2),
            0
        )
    
    # Choose random unit type
    unit_type = random.choice(["dimensioneer", "portal_archer"])
    
    # Create the appropriate unit
    if unit_type == "dimensioneer":
        enemy_unit = Dimensioneer(position, faction="enemy")
        enemy_unit.knockback_power = 1.5
    else:
        enemy_unit = PortalArcher(position, faction="enemy")
    
    # Create a new squad for this unit if it's not part of mission spawns
    squad_name = f"Test Enemy {random.randint(1000, 9999)}"
    squad = Squad(position, "enemy", squad_name)
    squad.add_unit(enemy_unit)
    
    # Add to enemy squads
    game_state.enemy_squads.append(squad)
    
    return enemy_unit

# Main game loop
running = True
while running:
    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_F1:
                show_debug = not show_debug
            elif event.key == K_e and (event.mod & KMOD_CTRL):
                # Ctrl+E to spawn enemy units
                spawn_enemy_unit(game_state)
                
    # Process input
    input_handler.process_events(events, renderer)
    
    # Time tracking
    dt = clock.tick(60) / 1000.0  # time in seconds since last frame
    
    # Process commands
    commands = input_handler.get_commands()
    for command in commands:
        if command["type"] == "camera_move":
            # Move camera
            delta = command["delta"]
            renderer.camera_position = (
                renderer.camera_position[0] + delta[0],
                renderer.camera_position[1] + delta[1],
                renderer.camera_position[2]
            )
        elif command["type"] == "camera_rotate":
            # Rotate camera
            renderer.camera_rotation += command["angle"]
        elif command["type"] == "camera_zoom":
            # Zoom camera
            renderer.camera_zoom += command["amount"]
            renderer.camera_zoom = max(5, min(30, renderer.camera_zoom))
        elif command["type"] == "selection_start":
            # Start unit selection
            pass  # Just tracking the start position, actual selection happens at end
        elif command["type"] == "selection_end":
            # Complete unit selection
            start_pos = command["start"]
            end_pos = command["end"]
            
            # Create selection rectangle
            x = min(start_pos[0], end_pos[0])
            y = min(start_pos[1], end_pos[1])
            width = abs(end_pos[0] - start_pos[0])
            height = abs(end_pos[1] - start_pos[1])
            
            # Use the new select_units method from input_handler
            input_handler.select_units(
                game_state, 
                renderer, 
                (x, y, width, height), 
                command.get("is_point_selection", False),
                command.get("shift_held", False),
                command.get("is_double_click", False)
            )
            
        elif command["type"] == "unit_command":
            # Process unit command (move, attack, etc.)
            target_pos = renderer.screen_to_world(command["target_position"])
            
            # Check what type of command this is
            command_type = command.get("command", "move")
            
            if command_type == "move":
                # Move command
                for unit in command["units"]:
                    unit.set_destination(target_pos)
            elif command_type == "attack":
                # Attack command - find a target or move to position
                target_unit = None
                
                # Look for enemy units near the clicked position
                click_radius = 5.0  # world units
                for squad in game_state.enemy_squads:
                    for unit in squad.units:
                        dx = unit.position[0] - target_pos[0]
                        dy = unit.position[1] - target_pos[1]
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        if distance <= click_radius:
                            target_unit = unit
                            break
                    if target_unit:
                        break
                
                for unit in command["units"]:
                    if target_unit:
                        # Attack the target unit
                        unit.target = target_unit
                        unit.state = "attacking"
                    else:
                        # No target found, just move there
                        unit.set_destination(target_pos)
    
    # Update mission
    mission_manager.update(game_state, dt)
    
    # Check mission completion/failure
    if mission_manager.current_mission:
        # Check win condition
        if mission_manager.current_mission.check_win_condition(game_state):
            game_state.mission_complete = True
        
        # Check loss condition
        if mission_manager.current_mission.check_loss_condition(game_state):
            game_state.mission_failed = True
    
    # Update physics (projectiles, explosions, etc.)
    physics_engine.update(dt, game_state)
    
    # Execute test functions
    current_time = time.time()
    
    # Automatically fire projectiles from player units every few seconds
    if current_time - last_fire_time > 3.0:
        # Get all player units
        player_units = game_state.get_all_player_units()
        enemy_units = game_state.get_all_enemy_units()
        
        if player_units and enemy_units:
            # Select a random player unit
            shooter = random.choice(player_units)
            
            # Pick a random enemy as target
            target = random.choice(enemy_units)
            
            # Fire a projectile
            start_pos = shooter.position
            target_pos = target.position
            
            # Calculate direction vector
            dx = target_pos[0] - start_pos[0]
            dy = target_pos[1] - start_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Normalize
                dx /= distance
                dy /= distance
                
                # Add some random spread
                dx += random.uniform(-0.1, 0.1)
                dy += random.uniform(-0.1, 0.1)
                
                # Create projectile
                physics_engine.create_projectile(
                    start_pos,
                    (dx, dy, 0.1), 
                    shooter.faction,
                    shooter.damage,
                    random.choice(['energy', 'portal', 'grenade'])
                )
        
        last_fire_time = current_time
    
    # Periodic enemy spawn for testing combat
    current_time = pygame.time.get_ticks() / 1000  # time in seconds
    if current_time - last_enemy_spawn_time > 5.0:  # Spawn every 5 seconds
        # Only spawn if there are fewer than 10 enemy units
        total_enemies = sum(len(squad.units) for squad in game_state.enemy_squads)
        if total_enemies < 10:
            spawn_enemy_unit(game_state)
            last_enemy_spawn_time = current_time
    
    # Update game state
    game_state.update(dt)
    
    # Clear the screen
    screen.fill((0, 0, 0))
    
    # Only update game if mission is not complete/failed
    if not game_state.mission_complete and not game_state.mission_failed:
        # Render game
        renderer.render_game(game_state, physics_engine)
    
    # Draw selection box if selecting
    if input_handler.is_selecting and input_handler.selection_start:
        start_pos = input_handler.selection_start
        end_pos = pygame.mouse.get_pos()
        
        # Create selection rectangle
        rect_x = min(start_pos[0], end_pos[0])
        rect_y = min(start_pos[1], end_pos[1])
        rect_w = abs(start_pos[0] - end_pos[0])
        rect_h = abs(start_pos[1] - end_pos[1])
        
        # Draw selection rectangle
        selection_rect = pygame.Rect(rect_x, rect_y, rect_w, rect_h)
        pygame.draw.rect(screen, (0, 255, 0), selection_rect, 2)
    
    # Render selected units indicator
    num_selected = len(input_handler.selected_units)
    if num_selected > 0:
        sel_text = f"Selected: {num_selected} units"
        sel_surface = font.render(sel_text, True, (0, 255, 0))
        screen.blit(sel_surface, (10, screen_height - 60))
    
    # Display some controls help
    lines = [
        "Controls:",
        "WASD/Arrows: Move Camera",
        "Q/E: Rotate Camera",
        "Z/X: Zoom Camera",
        "Left Mouse: Select Units (click or drag)",
        "Shift+Click: Add to Selection",
        "Double-Click: Select All Units of Same Type",
        "Right Mouse: Move Selected Units",
        "Alt+Right Mouse: Attack/Move to Attack",
        "Ctrl+E: Spawn Enemy Unit",
        "F1: Toggle Debug Info",
        "Esc: Clear Selection / Exit"
    ]
    y = 20
    for line in lines:
        text = small_font.render(line, True, (255, 255, 255))
        screen.blit(text, (20, y))
        y += 20
    
    # Add HUD and mission info
    mission_name = game_state.mission_name
    mission_name_text = font.render(f"Mission: {mission_name}", True, (255, 255, 255))
    screen.blit(mission_name_text, (10, 10))
    
    # Game time
    minutes = int(game_state.game_time) // 60
    seconds = int(game_state.game_time) % 60
    time_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (200, 200, 200))
    screen.blit(time_text, (10, 40))
    
    # Mission objectives with better formatting
    if game_state.mission_objectives:
        y_offset = 70
        obj_title = small_font.render("Objectives:", True, (220, 220, 100))
        screen.blit(obj_title, (10, y_offset))
        y_offset += 25
        
        for obj in game_state.mission_objectives:
            completed = obj.get('id') in mission_manager.current_mission.completed_objectives
            status = "✓" if completed else "□"
            color = (100, 255, 100) if completed else (200, 200, 200)
            
            obj_text = small_font.render(f"{status} {obj.get('description')}", True, color)
            screen.blit(obj_text, (20, y_offset))
            y_offset += 20
    
    # Check for mission completion
    if game_state.mission_complete:
        # Overlay for completed mission
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Display mission complete
        complete_text = font.render("MISSION COMPLETE", True, (100, 255, 100))
        text_width = complete_text.get_width()
        screen.blit(complete_text, (screen_width // 2 - text_width // 2, screen_height // 2 - 50))
        
        # Show objectives completed
        if game_state.mission_objectives:
            y_offset = screen_height // 2
            for obj in game_state.mission_objectives:
                completed = obj.get('id') in mission_manager.current_mission.completed_objectives
                status = "✓" if completed else "□"
                color = (100, 255, 100) if completed else (200, 200, 200)
                
                obj_text = small_font.render(f"{status} {obj.get('description')}", True, color)
                text_width = obj_text.get_width()
                screen.blit(obj_text, (screen_width // 2 - text_width // 2, y_offset))
                y_offset += 20
        
        # Add instructions to continue
        continue_text = small_font.render("Press ESC to exit", True, (200, 200, 200))
        text_width = continue_text.get_width()
        screen.blit(continue_text, (screen_width // 2 - text_width // 2, y_offset + 20))
    
    # Check for mission failure
    if game_state.mission_failed:
        # Overlay for failed mission
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Display mission failed
        failed_text = font.render("MISSION FAILED", True, (255, 100, 100))
        text_width = failed_text.get_width()
        screen.blit(failed_text, (screen_width // 2 - text_width // 2, screen_height // 2 - 50))
        
        # Show reason for failure
        if len(game_state.player_squads) == 0:
            reason_text = small_font.render("All units lost", True, (255, 150, 150))
        elif game_state.time_limit > 0 and game_state.game_time >= game_state.time_limit:
            reason_text = small_font.render("Time limit exceeded", True, (255, 150, 150))
        else:
            reason_text = small_font.render("Mission objectives not met", True, (255, 150, 150))
            
        text_width = reason_text.get_width()
        screen.blit(reason_text, (screen_width // 2 - text_width // 2, screen_height // 2))
        
        # Add instructions to retry
        retry_text = small_font.render("Press ESC to exit", True, (200, 200, 200))
        text_width = retry_text.get_width()
        screen.blit(retry_text, (screen_width // 2 - text_width // 2, screen_height // 2 + 40))
    
    # Debug info
    if show_debug:
        # Show squad counts
        y_offset = screen_height - 120
        player_count = sum(len(squad.units) for squad in game_state.player_squads)
        enemy_count = sum(len(squad.units) for squad in game_state.enemy_squads)
        proj_count = len(physics_engine.projectiles)
        exp_count = len(physics_engine.explosions)
        
        debug_text = small_font.render(f"Player Units: {player_count}", True, (100, 200, 255))
        screen.blit(debug_text, (10, y_offset))
        y_offset += 20
        
        debug_text = small_font.render(f"Enemy Units: {enemy_count}", True, (255, 100, 100))
        screen.blit(debug_text, (10, y_offset))
        y_offset += 20
        
        debug_text = small_font.render(f"Projectiles: {proj_count}", True, (200, 200, 200))
        screen.blit(debug_text, (10, y_offset))
        y_offset += 20
        
        debug_text = small_font.render(f"Explosions: {exp_count}", True, (255, 200, 100))
        screen.blit(debug_text, (10, y_offset))
        y_offset += 20
        
        debug_text = small_font.render(f"FPS: {int(clock.get_fps())}", True, (200, 200, 200))
        screen.blit(debug_text, (10, y_offset))
    
    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()
sys.exit()
