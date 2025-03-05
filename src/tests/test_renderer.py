#!/usr/bin/env python3
# Test script for the game renderer and physics engine

import sys
import os
import pygame
import time
import random
import numpy as np

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import game modules
from engine.renderer import GameRenderer
from engine.physics.physics_engine import PhysicsEngine
from game.game_state import GameState
from game.units.unit_factory import UnitFactory

def test_renderer_with_physics():
    """
    A test demonstration of the game renderer with physics objects.
    Creates a simple game state with units and fires some projectiles.
    """
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game Renderer and Physics Test")
    
    # Create clock for tracking FPS
    clock = pygame.time.Clock()
    
    # Initialize game components
    renderer = GameRenderer(width, height)
    physics_engine = PhysicsEngine()
    game_state = GameState()
    
    # Create units using the UnitFactory
    unit_factory = UnitFactory()
    
    # Add some player squads
    player_squad1 = unit_factory.create_balanced_squad(
        position=(0, 0, 0),
        size=5, 
        faction="player", 
        name="Alpha Squad"
    )
    player_squad2 = unit_factory.create_archer_squad(
        position=(-50, 50, 0),
        size=3, 
        faction="player", 
        name="Bravo Squad"
    )
    
    # Add some enemy squads
    enemy_squad1 = unit_factory.create_gromflomite_squad(
        position=(100, 100, 0),
        size=8, 
        faction="enemy", 
        name="Enemy Squad Alpha"
    )
    enemy_squad2 = unit_factory.create_gromflomite_squad(
        position=(150, -50, 0),
        size=4, 
        faction="enemy", 
        name="Enemy Squad Beta"
    )
    
    # Add squads to game state
    game_state.player_squads = [player_squad1, player_squad2]
    game_state.enemy_squads = [enemy_squad1, enemy_squad2]
    
    # Select a squad for the demo
    game_state.selected_squads = [player_squad1]
    
    # Variables for the demo
    running = True
    last_time = time.time()
    frame_count = 0
    next_projectile_time = 0
    
    # Main loop
    while running:
        # Calculate delta time
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Camera controls
                elif event.key == pygame.K_LEFT:
                    renderer.move_camera(-10, 0)
                elif event.key == pygame.K_RIGHT:
                    renderer.move_camera(10, 0)
                elif event.key == pygame.K_UP:
                    renderer.move_camera(0, -10)
                elif event.key == pygame.K_DOWN:
                    renderer.move_camera(0, 10)
                elif event.key == pygame.K_q:
                    renderer.move_camera(0, 0, 0, -15)  # Rotate left
                elif event.key == pygame.K_e:
                    renderer.move_camera(0, 0, 0, 15)   # Rotate right
                elif event.key == pygame.K_z:
                    renderer.move_camera(0, 0, -0.1)    # Zoom out
                elif event.key == pygame.K_x:
                    renderer.move_camera(0, 0, 0.1)     # Zoom in
                # Test firing projectiles
                elif event.key == pygame.K_SPACE:
                    _fire_test_projectiles(physics_engine, game_state)
                # Test creating explosions
                elif event.key == pygame.K_b:
                    _create_test_explosions(physics_engine, game_state)
        
        # Auto-fire projectiles for demo purposes
        if current_time > next_projectile_time:
            _fire_test_projectiles(physics_engine, game_state)
            next_projectile_time = current_time + 2.0  # Fire every 2 seconds
        
        # Update game state and physics
        game_state.game_time += dt
        physics_engine.update(game_state, dt)
        
        # Render the game
        renderer.render_game(game_state, physics_engine)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(60)
        
        # Display FPS
        frame_count += 1
        if frame_count % 60 == 0:
            fps = clock.get_fps()
            print(f"FPS: {fps:.2f}")
    
    # Clean up
    pygame.quit()

def _fire_test_projectiles(physics_engine, game_state):
    """Fire some test projectiles from random units"""
    # Get all player units
    player_units = []
    for squad in game_state.player_squads:
        player_units.extend(squad.units)
    
    # Get all enemy units
    enemy_units = []
    for squad in game_state.enemy_squads:
        enemy_units.extend(squad.units)
    
    # Have random player units fire at random enemy units
    for _ in range(min(3, len(player_units))):
        if player_units and enemy_units:
            # Select random units
            firing_unit = random.choice(player_units)
            target_unit = random.choice(enemy_units)
            
            # Determine projectile type based on unit type
            projectile_type = "arrow"  # Default
            if firing_unit.__class__.__name__ == "PortalArcher":
                projectile_type = "portal_arrow"
            elif firing_unit.__class__.__name__ == "TechGrenadier":
                projectile_type = "grenade"
            elif firing_unit.__class__.__name__ == "Dimensioneer":
                projectile_type = "energy_bolt"
            
            # Fire projectile
            physics_engine.fire_projectile(
                start_position=firing_unit.position,
                target_unit=target_unit,
                projectile_type=projectile_type,
                owner=firing_unit,
                damage=random.uniform(5.0, 15.0)
            )
    
    # Have random enemy units fire at random player units
    for _ in range(min(2, len(enemy_units))):
        if player_units and enemy_units:
            # Select random units
            firing_unit = random.choice(enemy_units)
            target_unit = random.choice(player_units)
            
            # Fire projectile (enemies just use default arrows for now)
            physics_engine.fire_projectile(
                start_position=firing_unit.position,
                target_unit=target_unit,
                projectile_type="arrow",
                owner=firing_unit,
                damage=random.uniform(3.0, 10.0)
            )

def _create_test_explosions(physics_engine, game_state):
    """Create some test explosions at random locations"""
    # Create 1-3 random explosions
    for _ in range(random.randint(1, 3)):
        # Random position near units
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = 0
        
        # Create explosion
        physics_engine.create_explosion(
            position=(x, y, z),
            radius=random.uniform(10.0, 30.0),
            damage=random.uniform(10.0, 30.0)
        )

if __name__ == "__main__":
    test_renderer_with_physics()
