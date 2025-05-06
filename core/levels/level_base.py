from typing import Dict, List, Tuple, Optional, Any
import pygame
from core.config import Era, WINDOW_WIDTH, WINDOW_HEIGHT
from entities.player import Player
from entities.enemies import PrehistoricEnemy, MedievalEnemy, FuturisticEnemy

class Level:
    def __init__(self) -> None:
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        
        # Level properties
        self.starting_position = (100, 100)
        self.checkpoints: List[Tuple[int, int]] = []
        self.current_checkpoint = 0
        self.level_bounds = pygame.Rect(0, 0, WINDOW_WIDTH * 2, WINDOW_HEIGHT)
        self.background_color = (50, 50, 50)
        
        # Tutorial properties
        self.tutorial_messages: Dict[str, str] = {}
        self.current_message: Optional[str] = None
        self.message_timer = 0
        
        # Level requirements
        self.required_era: Optional[Era] = None
        self.completion_requirements: Dict[str, Any] = {}
        
        self._setup_level()

    def _setup_level(self) -> None:
        """Override this method to set up the level layout."""
        pass

    def _create_platform(self, x: int, y: int, width: int, height: int, 
                        color: Tuple[int, int, int] = (100, 100, 100)) -> None:
        """Helper method to create a platform/wall."""
        platform = pygame.sprite.Sprite()
        platform.image = pygame.Surface((width, height))
        platform.image.fill(color)
        platform.rect = platform.image.get_rect(topleft=(x, y))
        self.walls.add(platform)
        self.all_sprites.add(platform)

    def _add_enemy(self, enemy_type: str, x: int, y: int) -> None:
        """Add an enemy to the level."""
        enemy_classes = {
            'prehistoric': PrehistoricEnemy,
            'medieval': MedievalEnemy,
            'futuristic': FuturisticEnemy
        }
        
        if enemy_type in enemy_classes:
            enemy = enemy_classes[enemy_type](x, y)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def show_tutorial_message(self, key: str) -> None:
        """Display a tutorial message."""
        if key in self.tutorial_messages:
            self.current_message = self.tutorial_messages[key]
            self.message_timer = 5000  # Show message for 5 seconds

    def update(self, dt: float) -> None:
        """Update level elements."""
        # Update message timer
        if self.message_timer > 0:
            self.message_timer = max(0, self.message_timer - dt)
            if self.message_timer == 0:
                self.current_message = None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw level elements."""
        # Draw background
        screen.fill(self.background_color)
        
        # Draw sprites
        self.all_sprites.draw(screen)
        
        # Draw tutorial message if active
        if self.current_message and self.message_timer > 0:
            font = pygame.font.Font(None, 36)
            text = font.render(self.current_message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            screen.blit(text, text_rect)

    def get_spawn_position(self) -> Tuple[int, int]:
        """Get the current spawn position (either start or last checkpoint)."""
        if self.checkpoints and self.current_checkpoint < len(self.checkpoints):
            return self.checkpoints[self.current_checkpoint]
        return self.starting_position

    def is_completed(self) -> bool:
        """Check if level completion requirements are met."""
        # Override in specific levels
        return True