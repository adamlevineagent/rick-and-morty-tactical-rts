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
physics_engine = PhysicsEngine(renderer)
input_handler = InputHandler()

# Set up camera position
renderer.camera_position = (0, 0, 50)  # Z is height
renderer.camera_zoom = 15

# Set up time tracking
clock = pygame.time.Clock()
last_fire_time = 0
last_spawn_time = 0

# Set up fonts
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 16)

# Debug info display
show_debug = True

# Main game loop
running = True
while running:
    # Cap frame rate
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    
    # Process input
    input_events = pygame.event.get()
    for event in input_events:
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_F1:
                show_debug = not show_debug
                
    # Process input and get commands
    input_handler.process_events(input_events, renderer)
    
    # Update game state
    game_state.update(dt)
    
    # Update mission
    mission_manager.update(game_state, dt)
    
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
    
    # Clear the screen
    screen.fill((20, 20, 30))
    
    # Render the game
    renderer.render_game_state(game_state)
    
    # Render physics objects
    physics_engine.render(dt)
    
    # Add HUD and mission info
    mission_name = game_state.mission_name
    mission_name_text = font.render(f"Mission: {mission_name}", True, (255, 255, 255))
    screen.blit(mission_name_text, (10, 10))
    
    # Game time
    minutes = int(game_state.game_time) // 60
    seconds = int(game_state.game_time) % 60
    time_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (200, 200, 200))
    screen.blit(time_text, (10, 40))
    
    # Mission objectives
    if game_state.mission_objectives:
        y_offset = 70
        obj_title = small_font.render("Objectives:", True, (220, 220, 100))
        screen.blit(obj_title, (10, y_offset))
        y_offset += 25
        
        for obj in game_state.mission_objectives:
            status = "✓" if obj.get('id') in mission_manager.current_mission.completed_objectives else " "
            obj_text = small_font.render(f"[{status}] {obj.get('description')}", True, (200, 200, 200))
            screen.blit(obj_text, (20, y_offset))
            y_offset += 20
    
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
    
    # Check for mission completion
    if game_state.mission_complete:
        # Display mission complete
        complete_text = font.render("MISSION COMPLETE", True, (100, 255, 100))
        text_width = complete_text.get_width()
        screen.blit(complete_text, (screen_width // 2 - text_width // 2, screen_height // 2 - 50))
        
        # Add instructions to continue
        continue_text = small_font.render("Press ESC to exit", True, (200, 200, 200))
        text_width = continue_text.get_width()
        screen.blit(continue_text, (screen_width // 2 - text_width // 2, screen_height // 2))
    
    # Check for mission failure
    if game_state.mission_failed:
        # Display mission failed
        failed_text = font.render("MISSION FAILED", True, (255, 100, 100))
        text_width = failed_text.get_width()
        screen.blit(failed_text, (screen_width // 2 - text_width // 2, screen_height // 2 - 50))
        
        # Add instructions to retry
        retry_text = small_font.render("Press ESC to exit", True, (200, 200, 200))
        text_width = retry_text.get_width()
        screen.blit(retry_text, (screen_width // 2 - text_width // 2, screen_height // 2))
    
    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()
sys.exit()
