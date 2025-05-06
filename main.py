import sys
import pygame
from typing import NoReturn

from managers.state_manager import GameStateManager
from managers.time_manager import TimeManager
from core.config import FPS, WINDOW_WIDTH, WINDOW_HEIGHT

class Game:
    def __init__(self) -> None:
        """Initialize the game with basic setup."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chronosta")
        self.clock = pygame.time.Clock()
        
        # Initialize managers in correct order
        self.time_manager = TimeManager()
        self.state_manager = GameStateManager()
        self.state_manager.time_manager = self.time_manager
        self.state_manager.initialize_states()  # Initialize states after setting time_manager
        
        self.running = True
        self.accumulated_time = 0
        self.fixed_time_step = 1000 / FPS  # Convert FPS to milliseconds
        self.max_frame_time = self.fixed_time_step * 5  # Prevent spiral of death

    def handle_events(self) -> None:
        """Process all game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.state_manager.handle_event(event)

    def fixed_update(self, dt: float) -> None:
        """Update game state with fixed time step."""
        # Update time effects first
        self.time_manager.update()
        
        # Scale delta time by time_scale for slow motion effects
        scaled_dt = dt * self.time_manager.get_time_scale()
        
        # Update game state with scaled time
        self.state_manager.update(scaled_dt)

    def render(self, interpolation: float) -> None:
        """Render the current game state.
        
        Args:
            interpolation: Float between 0 and 1 representing partial time step
        """
        self.screen.fill((0, 0, 0))  # Clear screen
        
        # Draw game state
        self.state_manager.draw(self.screen)
        
        # Draw time effects (like era transitions) on top
        self.time_manager.draw_transition(self.screen)
        
        pygame.display.flip()

    def run(self) -> NoReturn:
        """Main game loop with fixed time step updates."""
        while self.running:
            # Handle input events
            self.handle_events()
            
            # Calculate time since last frame
            frame_time = self.clock.tick(FPS)
            
            # Prevent spiral of death
            frame_time = min(frame_time, self.max_frame_time)
            
            self.accumulated_time += frame_time
            
            # Update physics and game state with fixed time step
            while self.accumulated_time >= self.fixed_time_step:
                self.fixed_update(self.fixed_time_step)
                self.accumulated_time -= self.fixed_time_step
            
            # Calculate interpolation for smooth rendering
            interpolation = self.accumulated_time / self.fixed_time_step
            
            # Render at display refresh rate with interpolation
            self.render(interpolation)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

