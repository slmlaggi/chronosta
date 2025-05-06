import pygame
from typing import Tuple
import math
from core.config import PROJECTILE_SPEED, PROJECTILE_BASE_DAMAGE, Era

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, target_x: int, target_y: int, era: Era) -> None:
        super().__init__()
        self.era = era
        
        # Set up projectile appearance based on era
        self.image = pygame.Surface((8, 8))
        if era == Era.PREHISTORIC:
            self.image.fill((139, 69, 19))  # Brown for rocks
        elif era == Era.MEDIEVAL:
            self.image.fill((128, 128, 128))  # Gray for arrows
        else:  # FUTURISTIC
            self.image.fill((0, 255, 255))  # Cyan for energy bolts
        
        self.rect = self.image.get_rect(center=(x, y))
        
        # Calculate direction and velocity
        angle = math.atan2(target_y - y, target_x - x)
        self.velocity = pygame.math.Vector2(
            math.cos(angle) * PROJECTILE_SPEED,
            math.sin(angle) * PROJECTILE_SPEED
        )
        
        # Set damage based on era
        self.damage = self._get_era_damage()
        
        # Track lifetime for cleanup
        self.lifetime = 5000  # 5 seconds
        self.time_alive = 0

    def _get_era_damage(self) -> int:
        """Get damage value based on projectile era."""
        if self.era == Era.PREHISTORIC:
            return PROJECTILE_BASE_DAMAGE * 1.5  # Heavy rocks
        elif self.era == Era.MEDIEVAL:
            return PROJECTILE_BASE_DAMAGE  # Standard arrows
        else:  # FUTURISTIC
            return PROJECTILE_BASE_DAMAGE * 0.8  # Rapid fire energy bolts

    def update(self, dt: float) -> None:
        """Update projectile position and check lifetime."""
        # Convert milliseconds to seconds for physics calculations
        dt_seconds = dt / 1000.0
        
        self.rect.x += self.velocity.x * dt_seconds
        self.rect.y += self.velocity.y * dt_seconds
        
        # Update lifetime and kill if expired
        self.time_alive += dt_seconds
        if self.time_alive >= self.lifetime:
            self.kill()

class Arrow(Projectile):
    """Medieval era arrow projectile."""
    def __init__(self, x: int, y: int, target_x: int, target_y: int) -> None:
        super().__init__(x, y, target_x, target_y, Era.MEDIEVAL)
        # Arrows are longer and thinner
        self.image = pygame.Surface((12, 4))
        self.image.fill((128, 128, 128))

class Rock(Projectile):
    """Prehistoric era rock projectile."""
    def __init__(self, x: int, y: int, target_x: int, target_y: int) -> None:
        super().__init__(x, y, target_x, target_y, Era.PREHISTORIC)
        # Rocks are more circular
        self.image = pygame.Surface((10, 10))
        self.image.fill((139, 69, 19))

class EnergyBolt(Projectile):
    """Futuristic era energy bolt projectile."""
    def __init__(self, x: int, y: int, target_x: int, target_y: int) -> None:
        super().__init__(x, y, target_x, target_y, Era.FUTURISTIC)
        # Energy bolts are smaller but glow
        self.image = pygame.Surface((6, 6))
        self.image.fill((0, 255, 255))
        self.glow_radius = 12
        
    def draw(self, screen: pygame.Surface) -> None:
        """Override draw to add glow effect."""
        # Draw glow
        glow = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (0, 255, 255, 128), (self.glow_radius, self.glow_radius), self.glow_radius)
        screen.blit(glow, (self.rect.centerx - self.glow_radius, self.rect.centery - self.glow_radius))