#!/usr/bin/env python3
# Rick and Morty Tactical RTS - Main Entry Point
import sys
import os
import pygame
import time
from pygame.locals import *

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import game modules
from engine.renderer import GameRenderer
from engine.input.input_handler import InputHandler
from engine.physics.physics_engine import PhysicsEngine
from game.game_state import GameState

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set up the display
        self.width = 1280
        self.height = 720
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Rick and Morty Tactical RTS")
        
        # Create clock for tracking FPS
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # Initialize game components
        self.renderer = GameRenderer(self.width, self.height)
        self.input_handler = InputHandler()
        self.physics_engine = PhysicsEngine()
        self.game_state = GameState()
        
        # Game state variables
        self.running = True
        self.frame_count = 0
        self.last_time = time.time()
        
    def handle_events(self):
        """Process all events from the event queue"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    
            # Pass event to input handler
            self.input_handler.process_event(event)
    
    def update(self, dt):
        """Update game state"""
        # Process input and update game state
        commands = self.input_handler.get_commands()
        self.game_state.update(commands, dt)
        
        # Update physics
        self.physics_engine.update(self.game_state, dt)
        
    def render(self):
        """Render the current frame"""
        # Use our new game renderer
        self.renderer.render_game(self.game_state, self.physics_engine)
    
    def run(self):
        """Main game loop"""
        print("Starting Rick and Morty Tactical RTS...")
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            # Handle events, update game state, and render
            self.handle_events()
            self.update(dt)
            self.render()
            
            # Display debug info
            self.frame_count += 1
            if self.frame_count % 100 == 0:
                fps = self.clock.get_fps()
                print(f"FPS: {fps:.2f}")
            
            # Cap the framerate
            self.clock.tick(self.target_fps)
        
        # Clean up
        pygame.quit()
        print("Game exited.")

if __name__ == "__main__":
    game = Game()
    game.run()
