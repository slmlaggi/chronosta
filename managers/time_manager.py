import pygame
from typing import List, Optional
from core.config import Era, SLOW_MOTION_DURATION, SLOW_MOTION_COOLDOWN, SLOW_MOTION_FACTOR

class TimeManager:
    def __init__(self) -> None:
        self.time_scale = 1.0
        self.slow_motion_active = False
        self.slow_motion_end_time = 0
        self.slow_motion_cooldown_end = 0
        
        # Era transition
        self.transitioning = False
        self.transition_progress = 0.0
        self.transition_speed = 0.002  # Adjust for faster/slower transitions
        self.current_era = Era.MEDIEVAL
        self.target_era = Era.MEDIEVAL
        
        # Surfaces for transition effect
        self.current_surface: Optional[pygame.Surface] = None
        self.target_surface: Optional[pygame.Surface] = None

    def start_slow_motion(self) -> bool:
        """Attempt to start slow motion effect."""
        current_time = pygame.time.get_ticks()
        if (not self.slow_motion_active and 
            current_time >= self.slow_motion_cooldown_end):
            self.slow_motion_active = True
            self.time_scale = SLOW_MOTION_FACTOR
            self.slow_motion_end_time = current_time + SLOW_MOTION_DURATION
            return True
        return False

    def update(self) -> None:
        """Update time effects."""
        current_time = pygame.time.get_ticks()
        
        # Update slow motion
        if self.slow_motion_active:
            if current_time >= self.slow_motion_end_time:
                self.slow_motion_active = False
                self.time_scale = 1.0
                self.slow_motion_cooldown_end = current_time + SLOW_MOTION_COOLDOWN
        
        # Update era transition
        if self.transitioning:
            self.transition_progress += self.transition_speed
            if self.transition_progress >= 1.0:
                self.transitioning = False
                self.transition_progress = 0.0
                self.current_era = self.target_era
                self.current_surface = None
                self.target_surface = None

    def start_era_transition(self, target_era: Era, current_screen: pygame.Surface) -> None:
        """Begin transition to a new era."""
        if self.transitioning or target_era == self.current_era:
            return
            
        self.transitioning = True
        self.transition_progress = 0.0
        self.target_era = target_era
        
        # Create surfaces for transition effect
        if self.current_surface is None:
            self.current_surface = current_screen.copy()
        self.target_surface = pygame.Surface(current_screen.get_size())
        self.target_surface.fill(self._get_era_color(target_era))

    def draw_transition(self, screen: pygame.Surface) -> None:
        """Draw the era transition effect."""
        if not self.transitioning or not self.current_surface or not self.target_surface:
            return
            
        # Draw current era with fading alpha
        current_alpha = int(255 * (1 - self.transition_progress))
        self.current_surface.set_alpha(current_alpha)
        screen.blit(self.current_surface, (0, 0))
        
        # Draw target era with increasing alpha
        target_alpha = int(255 * self.transition_progress)
        self.target_surface.set_alpha(target_alpha)
        screen.blit(self.target_surface, (0, 0))

    def get_time_scale(self) -> float:
        """Get the current time scale factor."""
        return self.time_scale

    @staticmethod
    def _get_era_color(era: Era) -> tuple[int, int, int]:
        """Get the characteristic color for each era."""
        colors = {
            Era.PREHISTORIC: (139, 69, 19),  # Brown
            Era.MEDIEVAL: (128, 128, 128),    # Gray
            Era.FUTURISTIC: (0, 255, 255)     # Cyan
        }
        return colors[era]