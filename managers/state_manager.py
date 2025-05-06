from enum import Enum, auto
from typing import Optional, Dict, Type
import pygame

from entities.player import Player
from core.config import PLAYER_SPEED, Era
from core.levels.demo_level import DemoLevel
from core.levels.tutorial_levels import MovementTutorial, TimeManipulationTutorial, EraSwitchingTutorial, PowersTutorial

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    ERA_TRANSITION = auto()

class BaseState:
    def __init__(self, manager: 'GameStateManager') -> None:
        self.manager = manager

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass

class MenuState(BaseState):
    def __init__(self, manager: 'GameStateManager') -> None:
        super().__init__(manager)
        self.title_alpha = 255
        self.alpha_direction = -1
        self.alpha_speed = 128  # Alpha change per second
        self.selected_option = 0
        self.menu_options = ["Tutorial", "Demo Level"]

    def update(self, dt: float) -> None:
        # Animate title text alpha
        self.title_alpha += self.alpha_direction * self.alpha_speed * (dt / 1000)
        if self.title_alpha <= 128:
            self.title_alpha = 128
            self.alpha_direction = 1
        elif self.title_alpha >= 255:
            self.title_alpha = 255
            self.alpha_direction = -1

    def draw(self, screen: pygame.Surface) -> None:
        # Draw animated title
        title_font = pygame.font.Font(None, 74)
        option_font = pygame.font.Font(None, 36)
        
        # Draw title
        text = title_font.render('Chronosta', True, (255, 255, 255))
        text.set_alpha(int(self.title_alpha))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
        screen.blit(text, text_rect)

        # Draw menu options
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = option_font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 
                                            screen.get_height() // 2 + i * 50))
            screen.blit(text, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                # Set the appropriate starting level based on selection
                self.manager.start_game(self.selected_option == 1)  # True for demo, False for tutorial

class PlayingState(BaseState):
    def __init__(self, manager: 'GameStateManager') -> None:
        super().__init__(manager)
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        # Level management
        self.levels = [
            MovementTutorial(),
            TimeManipulationTutorial(),
            EraSwitchingTutorial(),
            PowersTutorial(),
            DemoLevel()
        ]
        self.current_level_index = 0
        self.current_level = self.levels[self.current_level_index]
        
        # Create player at level starting position
        spawn_pos = self.current_level.get_spawn_position()
        self.player = Player(*spawn_pos)
        self.all_sprites.add(self.player)
        
        # Initialize time manager
        self.time_manager = manager.time_manager

    def _reset_game_state(self) -> None:
        """Reset game state when starting a new game."""
        # Reset player position to level start
        spawn_pos = self.current_level.get_spawn_position()
        self.player.rect.x, self.player.rect.y = spawn_pos
        self.player.velocity = pygame.math.Vector2(0, 0)  # Reset velocity
        self.player.on_ground = False
        
        # Sync sprites with current level
        self._sync_sprites_with_level()

    def next_level(self) -> None:
        """Advance to the next level."""
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            self.current_level = self.levels[self.current_level_index]
            self._reset_game_state()

    def _sync_sprites_with_level(self) -> None:
        """Sync sprite groups with current level."""
        self.walls = self.current_level.walls
        self.enemies = self.current_level.enemies
        self.projectiles = self.current_level.projectiles
        
        # Update all_sprites group
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.walls)
        self.all_sprites.add(self.enemies)
        self.all_sprites.add(self.projectiles)

    def update(self, dt: float) -> None:
        # Scale delta time by time effects
        scaled_dt = dt * self.time_manager.get_time_scale()
        
        # Update current level
        self.current_level.update(scaled_dt)
        
        # Update player with scaled time
        self.player.update(scaled_dt, self.walls)
        
        # Update enemies with scaled time
        for enemy in self.enemies:
            enemy.update(scaled_dt, self.player.get_position())
        
        # Update projectiles with scaled time
        for projectile in self.projectiles:
            projectile.update(scaled_dt)
            
        # Check for collisions
        self._handle_collisions()
        
        # Check level completion
        if self.current_level.is_completed():
            self.next_level()

    def draw(self, screen: pygame.Surface) -> None:
        # Draw current level
        self.current_level.draw(screen)
        
        # Draw all sprites
        self.all_sprites.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.set_state(GameState.PAUSED)
            elif event.key == pygame.K_SPACE:
                self.player.jump()
            # Era switching controls
            elif event.key == pygame.K_q:  # Next era
                current_era = self.player.current_era
                if current_era == Era.PREHISTORIC:
                    target_era = Era.MEDIEVAL
                elif current_era == Era.MEDIEVAL:
                    target_era = Era.FUTURISTIC
                elif current_era == Era.FUTURISTIC:
                    target_era = Era.PREHISTORIC
                self.manager.start_era_transition(target_era)
            elif event.key == pygame.K_z:  # Previous era
                current_era = self.player.current_era
                if current_era == Era.PREHISTORIC:
                    target_era = Era.FUTURISTIC
                elif current_era == Era.MEDIEVAL:
                    target_era = Era.PREHISTORIC
                elif current_era == Era.FUTURISTIC:
                    target_era = Era.MEDIEVAL
                self.manager.start_era_transition(target_era)
            elif event.key == pygame.K_e:  # Use era power
                self.player.use_era_power()
            elif event.key == pygame.K_LSHIFT:  # Slow motion
                self.manager.time_manager.start_slow_motion()
        
        # Handle continuous keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:  # Move left
            self.player.velocity.x = -PLAYER_SPEED
        elif keys[pygame.K_d]:  # Move right
            self.player.velocity.x = PLAYER_SPEED
        else:
            self.player.velocity.x = 0

    def _handle_collisions(self) -> None:
        # Check projectile collisions with enemies
        pygame.sprite.groupcollide(self.projectiles, self.enemies, True, True)
        
        # Check enemy collisions with player
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hits:
            self.player.take_damage(10)  # Example damage value

class PausedState(BaseState):
    def __init__(self, manager: 'GameStateManager') -> None:
        super().__init__(manager)
        self.overlay_alpha = 0
        self.target_alpha = 128
        self.fade_speed = 512  # Alpha change per second
        self.selected_option = 0
        self.menu_options = ["Resume", "Return to Menu"]

    def update(self, dt: float) -> None:
        # Fade in overlay
        if self.overlay_alpha < self.target_alpha:
            self.overlay_alpha = min(self.target_alpha, 
                                   self.overlay_alpha + self.fade_speed * (dt / 1000))

    def draw(self, screen: pygame.Surface) -> None:
        # Draw game world in background
        self.manager.states[GameState.PLAYING].draw(screen)
        
        # Draw pause overlay with fade effect
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.overlay_alpha)))
        screen.blit(overlay, (0, 0))
        
        # Draw PAUSED text
        title_font = pygame.font.Font(None, 74)
        option_font = pygame.font.Font(None, 36)
        
        text = title_font.render('PAUSED', True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
        screen.blit(text, text_rect)

        # Draw menu options
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = option_font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 
                                            screen.get_height() // 2 + i * 50))
            screen.blit(text, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Resume game
                self.manager.set_state(GameState.PLAYING)
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:
                    # Resume game
                    self.manager.set_state(GameState.PLAYING)
                else:
                    # Return to main menu
                    self.manager.set_state(GameState.MENU)

class EraTransitionState(BaseState):
    def __init__(self, manager: 'GameStateManager') -> None:
        super().__init__(manager)
        self.transition_alpha = 0
        self.fade_speed = 512  # Alpha change per second
        self.fading_in = True
        self.target_era = Era.MEDIEVAL

    def start_transition(self, target_era: Era) -> None:
        self.target_era = target_era
        self.transition_alpha = 0
        self.fading_in = True

    def update(self, dt: float) -> None:
        if self.fading_in:
            self.transition_alpha = min(255, self.transition_alpha + self.fade_speed * (dt / 1000))
            if self.transition_alpha >= 255:
                self.fading_in = False
                # Change era when screen is fully black
                playing_state = self.manager.states[GameState.PLAYING]
                playing_state.player.switch_era(self.target_era)
        else:
            self.transition_alpha = max(0, self.transition_alpha - self.fade_speed * (dt / 1000))
            if self.transition_alpha <= 0:
                self.manager.set_state(GameState.PLAYING)

    def draw(self, screen: pygame.Surface) -> None:
        # Draw game world in background
        self.manager.states[GameState.PLAYING].draw(screen)
        
        # Draw fade overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.transition_alpha)))
        screen.blit(overlay, (0, 0))

class GameStateManager:
    def __init__(self) -> None:
        self.states: Dict[GameState, BaseState] = {}
        self.current_state: Optional[GameState] = None
        self.time_manager = None
        
        # Set initial state to None until time_manager is set
        self.current_state = None

    def initialize_states(self) -> None:
        """Initialize all game states after time_manager is set."""
        # Initialize all game states
        self.states[GameState.MENU] = MenuState(self)
        self.states[GameState.PLAYING] = PlayingState(self)
        self.states[GameState.PAUSED] = PausedState(self)
        self.states[GameState.ERA_TRANSITION] = EraTransitionState(self)
        
        # Set initial state
        self.set_state(GameState.MENU)

    def set_state(self, state: GameState) -> None:
        self.current_state = state

    def start_era_transition(self, target_era: Era) -> None:
        """Start transition to a new era."""
        era_state = self.states[GameState.ERA_TRANSITION]
        era_state.start_transition(target_era)
        self.set_state(GameState.ERA_TRANSITION)

    def start_game(self, demo: bool = False) -> None:
        """Start a new game session."""
        playing_state = self.states[GameState.PLAYING]
        
        # Set the appropriate level
        if demo:
            playing_state.current_level_index = len(playing_state.levels) - 1  # Last level is demo
        else:
            playing_state.current_level_index = 0  # First level is tutorial
            
        playing_state.current_level = playing_state.levels[playing_state.current_level_index]
        playing_state._reset_game_state()  # Reset player position and sprites
        self.set_state(GameState.PLAYING)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current_state:
            self.states[self.current_state].handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_state:
            self.states[self.current_state].update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        if self.current_state:
            self.states[self.current_state].draw(screen)