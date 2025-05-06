import pygame
from typing import Optional, Tuple
from core.config import Era, PLAYER_SPEED, PLAYER_JUMP_FORCE, GRAVITY, MAX_FALL_SPEED, PLAYER_MAX_HEALTH, PLAYER_MAX_STAMINA, STAMINA_REGEN_RATE, PREHISTORIC_POWER_COOLDOWN, MEDIEVAL_POWER_COOLDOWN, FUTURISTIC_POWER_COOLDOWN

class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        # Basic setup
        self.image = pygame.Surface((32, 64))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Movement properties
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_ground = False
        
        # Player stats
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.max_stamina = PLAYER_MAX_STAMINA
        self.stamina = self.max_stamina
        self.stamina_regen = STAMINA_REGEN_RATE
        
        # Cooldowns
        self.era_power_cooldown = 0
        self.slow_motion_cooldown = 0
        
        # Era-specific properties
        self.current_era = Era.MEDIEVAL
        self.era_powers = {
            Era.PREHISTORIC: self._prehistoric_power,
            Era.MEDIEVAL: self._medieval_power,
            Era.FUTURISTIC: self._futuristic_power
        }
        self.era_cooldowns = {
            Era.PREHISTORIC: PREHISTORIC_POWER_COOLDOWN,
            Era.MEDIEVAL: MEDIEVAL_POWER_COOLDOWN,
            Era.FUTURISTIC: FUTURISTIC_POWER_COOLDOWN
        }

    def take_damage(self, amount: int) -> None:
        """Apply damage to the player."""
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)

    def switch_era(self, new_era: Era) -> None:
        """Switch to a different era."""
        self.current_era = new_era
        # Reset era-specific cooldowns
        self.era_power_cooldown = 0
        # Update player appearance based on era
        self._update_appearance()

    def _update_appearance(self) -> None:
        """Update player sprite based on current era."""
        colors = {
            Era.PREHISTORIC: (139, 69, 19),  # Brown
            Era.MEDIEVAL: (128, 128, 128),   # Gray
            Era.FUTURISTIC: (0, 255, 255)    # Cyan
        }
        self.image.fill(colors[self.current_era])

    def use_era_power(self) -> None:
        """Use the current era's special power if cooldown is ready."""
        if self.era_power_cooldown <= 0 and self.stamina >= 20:
            power_func = self.era_powers.get(self.current_era)
            if power_func:
                power_func()
                self.stamina -= 20  # Use stamina for power
                self.era_power_cooldown = self.era_cooldowns[self.current_era]

    def _prehistoric_power(self) -> None:
        """Prehistoric era power - Super strength slam."""
        self.velocity.y = -15  # Jump up first
        # Slam effect will be handled in update

    def _medieval_power(self) -> None:
        """Medieval era power - Shield block."""
        # TODO: Implement shield block mechanic
        pass

    def _futuristic_power(self) -> None:
        """Futuristic era power - Time rewind."""
        # TODO: Implement time rewind mechanic
        pass

    def update(self, dt: float, walls: pygame.sprite.Group) -> None:
        """Update player state."""
        # Handle gravity
        if not self.on_ground:
            self.velocity.y = min(self.velocity.y + GRAVITY, MAX_FALL_SPEED)

        # Update position with collision checks
        self._move(dt, walls)
        
        # Regenerate stamina
        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen * dt)

        # Update cooldowns
        if self.era_power_cooldown > 0:
            self.era_power_cooldown = max(0, self.era_power_cooldown - dt)
        if self.slow_motion_cooldown > 0:
            self.slow_motion_cooldown = max(0, self.slow_motion_cooldown - dt)

    def _move(self, dt: float, walls: pygame.sprite.Group) -> None:
        """Handle movement and collision."""
        # Convert milliseconds to seconds for physics calculations
        dt_seconds = dt / 1000.0
        
        # Move horizontally
        self.rect.x += self.velocity.x * dt_seconds
        self._handle_collision(walls, 'horizontal')
        
        # Move vertically
        self.rect.y += self.velocity.y * dt_seconds
        self._handle_collision(walls, 'vertical')

    def _handle_collision(self, walls: pygame.sprite.Group, direction: str) -> None:
        """Handle collisions with walls."""
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if direction == 'horizontal':
                    if self.velocity.x > 0:
                        self.rect.right = wall.rect.left
                    else:
                        self.rect.left = wall.rect.right
                    self.velocity.x = 0
                else:  # vertical
                    if self.velocity.y > 0:
                        self.rect.bottom = wall.rect.top
                        self.velocity.y = 0
                        self.on_ground = True
                    else:
                        self.rect.top = wall.rect.bottom
                        self.velocity.y = 0

    def jump(self) -> None:
        """Make the player jump if on ground."""
        if self.on_ground:
            self.velocity.y = PLAYER_JUMP_FORCE
            self.on_ground = False

    def get_position(self) -> Tuple[int, int]:
        """Get the current position of the player."""
        return self.rect.centerx, self.rect.centery