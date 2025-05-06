import pygame
from typing import Optional, Tuple
from abc import ABC, abstractmethod
import math
from core.config import Era
from entities.projectiles import Arrow, Rock, EnergyBolt

class Enemy(pygame.sprite.Sprite, ABC):
    def __init__(self, x: int, y: int, health: int = 100) -> None:
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health
        self.max_health = health
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_frozen = False

    @abstractmethod
    def update(self, dt: float, player_pos: Tuple[int, int]) -> None:
        """Update enemy behavior based on player position."""
        pass

    def take_damage(self, amount: int) -> None:
        """Apply damage to the enemy."""
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.kill()

class PrehistoricEnemy(Enemy):
    """Prehistoric era enemy with charging behavior."""
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, health=150)
        self.image.fill((139, 69, 19))  # Brown color
        self.charge_cooldown = 0
        self.charge_speed = 8.0
        self.normal_speed = 2.0
        self.is_charging = False

    def update(self, dt: float, player_pos: Tuple[int, int]) -> None:
        if self.is_frozen:
            return

        # Convert milliseconds to seconds for physics calculations
        dt_seconds = dt / 1000.0
        
        if self.charge_cooldown > 0:
            self.charge_cooldown -= dt_seconds
            return

        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 200 and not self.is_charging:
            self.is_charging = True
            self.charge_cooldown = 3.0  # 3 second cooldown
        
        speed = self.charge_speed if self.is_charging else self.normal_speed
        if dist > 0:
            self.velocity.x = (dx / dist) * speed
            self.velocity.y = (dy / dist) * speed

        self.rect.x += self.velocity.x * dt_seconds
        self.rect.y += self.velocity.y * dt_seconds

class MedievalEnemy(Enemy):
    """Medieval era enemy with ranged attacks."""
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, health=80)
        self.image.fill((128, 128, 128))  # Gray color
        self.attack_range = 300
        self.attack_cooldown = 0
        self.projectiles = pygame.sprite.Group()

    def update(self, dt: float, player_pos: Tuple[int, int]) -> None:
        if self.is_frozen:
            return

        # Convert milliseconds to seconds for physics calculations
        dt_seconds = dt / 1000.0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt_seconds

        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)

        # Keep distance from player
        if dist < self.attack_range * 0.5:
            self.velocity.x = -(dx / dist) * 2
            self.velocity.y = -(dy / dist) * 2
        elif dist > self.attack_range:
            self.velocity.x = (dx / dist) * 2
            self.velocity.y = (dy / dist) * 2
        else:
            self.velocity.x = 0
            self.velocity.y = 0
            if self.attack_cooldown <= 0:
                # Fire arrow at player
                arrow = Arrow(self.rect.centerx, self.rect.centery, 
                            player_pos[0], player_pos[1])
                self.projectiles.add(arrow)
                self.attack_cooldown = 2.0

        self.rect.x += self.velocity.x * dt_seconds
        self.rect.y += self.velocity.y * dt_seconds
        
        # Update projectiles
        self.projectiles.update(dt)
        # Remove projectiles that have expired
        for projectile in self.projectiles:
            if projectile.time_alive >= projectile.lifetime:
                projectile.kill()

class FuturisticEnemy(Enemy):
    """Futuristic era enemy with teleportation and energy attacks."""
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, health=60)
        self.image.fill((0, 255, 255))  # Cyan color
        self.teleport_cooldown = 0
        self.attack_cooldown = 0
        self.last_positions = []  # For time rewind effect
        self.projectiles = pygame.sprite.Group()

    def update(self, dt: float, player_pos: Tuple[int, int]) -> None:
        if self.is_frozen:
            return

        # Convert milliseconds to seconds for physics calculations
        dt_seconds = dt / 1000.0

        # Store position for time rewind
        self.last_positions.append((self.rect.x, self.rect.y))
        if len(self.last_positions) > 300:  # 5 seconds at 60 FPS
            self.last_positions.pop(0)

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt_seconds
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt_seconds

        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)

        # Teleport if player is too close
        if dist < 100 and self.teleport_cooldown <= 0:
            self.teleport(player_pos)
            self.teleport_cooldown = 5.0
        else:
            # Normal movement
            if dist > 0:
                self.velocity.x = (dx / dist) * 3
                self.velocity.y = (dy / dist) * 3

            # Fire energy bolts if in range
            if dist < 400 and self.attack_cooldown <= 0:
                bolt = EnergyBolt(self.rect.centerx, self.rect.centery,
                                player_pos[0], player_pos[1])
                self.projectiles.add(bolt)
                self.attack_cooldown = 1.0  # Faster firing rate than medieval

            self.rect.x += self.velocity.x * dt_seconds
            self.rect.y += self.velocity.y * dt_seconds
        
        # Update projectiles
        self.projectiles.update(dt)
        # Remove expired projectiles
        for projectile in self.projectiles:
            if projectile.time_alive >= projectile.lifetime:
                projectile.kill()

    def teleport(self, player_pos: Tuple[int, int]) -> None:
        """Teleport away from the player."""
        angle = math.atan2(self.rect.centery - player_pos[1],
                          self.rect.centerx - player_pos[0])
        self.rect.centerx = player_pos[0] + math.cos(angle) * 300
        self.rect.centery = player_pos[1] + math.sin(angle) * 300