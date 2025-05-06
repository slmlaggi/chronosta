from typing import Dict, Any
import pygame
from core.levels.level_base import Level
from core.config import Era

class MovementTutorial(Level):
    """First tutorial level focusing on basic movement."""
    def __init__(self) -> None:
        super().__init__()
        self.tutorial_messages.update({
            'start': 'Use A and D to move left and right',
            'jump': 'Press SPACE to jump',
            'platform': 'Try reaching that platform!'
        })
        self.message_triggers: Dict[str, pygame.Rect] = {}

    def _setup_level(self) -> None:
        # Main floor
        self._create_platform(0, 680, 1280, 40)
        
        # Simple obstacle course
        self._create_platform(400, 550, 100, 20)
        self._create_platform(600, 450, 100, 20)
        
        # Message trigger zones
        self.message_triggers = {
            'start': pygame.Rect(50, 0, 100, 720),
            'jump': pygame.Rect(300, 0, 100, 720),
            'platform': pygame.Rect(500, 0, 100, 720)
        }

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.message_timer == 0:
            self.show_tutorial_message('start')

class TimeManipulationTutorial(Level):
    """Second tutorial level introducing slow motion."""
    def __init__(self) -> None:
        super().__init__()
        self.tutorial_messages.update({
            'intro': 'You can manipulate time!',
            'slow': 'Hold SHIFT to slow down time',
            'practice': 'Try dodging these projectiles using slow motion'
        })

    def _setup_level(self) -> None:
        # Main floor
        self._create_platform(0, 680, 1280, 40)
        
        # Safe zones
        self._create_platform(200, 500, 100, 20)
        self._create_platform(900, 500, 100, 20)
        
        # Add a medieval enemy that shoots arrows
        self._add_enemy('medieval', 600, 630)

class EraSwitchingTutorial(Level):
    """Third tutorial level teaching era switching mechanics."""
    def __init__(self) -> None:
        super().__init__()
        self.tutorial_messages.update({
            'intro': 'You can switch between different eras!',
            'switch': 'Press Q to switch to the next era, Z for previous',
            'prehistoric': 'Prehistoric Era: Raw strength and primal powers',
            'medieval': 'Medieval Era: Balanced combat and defensive abilities',
            'futuristic': 'Futuristic Era: Advanced technology and time manipulation'
        })
        self.required_era = Era.MEDIEVAL  # Start in medieval era

    def _setup_level(self) -> None:
        # Main floor
        self._create_platform(0, 680, 1280, 40)
        
        # Era-specific sections
        # Prehistoric section with strong enemies
        self._create_platform(100, 500, 300, 20)
        self._add_enemy('prehistoric', 250, 450)
        
        # Medieval section with archers
        self._create_platform(500, 500, 300, 20)
        self._add_enemy('medieval', 650, 450)
        
        # Futuristic section with high-tech enemies
        self._create_platform(900, 500, 300, 20)
        self._add_enemy('futuristic', 1050, 450)

class PowersTutorial(Level):
    """Final tutorial level showcasing era-specific powers."""
    def __init__(self) -> None:
        super().__init__()
        self.tutorial_messages.update({
            'intro': 'Each era grants you unique powers!',
            'power': 'Press E to use your era power',
            'prehistoric': 'Prehistoric Power: Ground Slam',
            'medieval': 'Medieval Power: Shield Block',
            'futuristic': 'Futuristic Power: Time Rewind'
        })

    def _setup_level(self) -> None:
        # Main floor
        self._create_platform(0, 680, 1280, 40)
        
        # Prehistoric power test area
        self._create_platform(100, 400, 200, 20)
        self._add_enemy('prehistoric', 200, 350)
        
        # Medieval power test area
        self._create_platform(500, 400, 200, 20)
        self._add_enemy('medieval', 600, 350)
        
        # Futuristic power test area
        self._create_platform(900, 400, 200, 20)
        self._add_enemy('futuristic', 1000, 350)

        # Add checkpoints between sections
        self.checkpoints = [
            (100, 600),  # Start
            (500, 600),  # Medieval section
            (900, 600)   # Futuristic section
        ]