from core.levels.level_base import Level
from core.config import Era

class DemoLevel(Level):
    def __init__(self) -> None:
        super().__init__()
        self.background_color = (30, 30, 40)  # Darker background for testing
        self.tutorial_messages.update({
            'welcome': 'Welcome to the Chronosta Demo Level!',
            'era_switch': 'Press Q/Z to switch between eras',
            'movement': 'Use A/D to move, SPACE to jump',
            'power': 'Press E to use your era power',
            'slow_time': 'Hold SHIFT for slow motion'
        })

    def _setup_level(self) -> None:
        """Set up the demo level layout."""
        # Main floor
        self._create_platform(0, 680, 1280, 40)
        
        # Platforms
        self._create_platform(300, 500, 200, 20)  # Platform 1
        self._create_platform(600, 400, 200, 20)  # Platform 2
        self._create_platform(900, 300, 200, 20)  # Platform 3
        
        # Walls
        self._create_platform(0, 0, 20, 720)      # Left wall
        self._create_platform(1260, 0, 20, 720)   # Right wall
        
        # Add enemies from different eras
        self._add_enemy('prehistoric', 400, 450)  # On platform 1
        self._add_enemy('medieval', 700, 350)     # On platform 2
        self._add_enemy('futuristic', 1000, 250)  # On platform 3
        
        # Add checkpoints
        self.checkpoints = [
            (100, 600),   # Starting area
            (500, 450),   # Near middle platforms
            (900, 250)    # Near end
        ]
        
        # Set completion requirements
        self.completion_requirements = {
            'enemies_defeated': 3,
            'checkpoints_reached': len(self.checkpoints)
        }

    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Show tutorial messages based on player position and time
        if self.message_timer == 0:  # Only show new message if previous one is done
            self.show_tutorial_message('welcome')
            # Additional tutorial triggers would go here based on player position/actions