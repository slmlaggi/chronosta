from enum import Enum, auto

class Era(Enum):
    PREHISTORIC = auto()
    MEDIEVAL = auto()
    FUTURISTIC = auto()

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Player settings (adjusted for seconds-based time)
PLAYER_SPEED = 300.0  # pixels per second
PLAYER_JUMP_FORCE = -600.0  # pixels per second
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_STAMINA = 100
STAMINA_REGEN_RATE = 20.0  # per second

# Physics settings (adjusted for seconds-based time)
GRAVITY = 1200.0  # pixels per second squared
MAX_FALL_SPEED = 800.0  # pixels per second

# Time manipulation settings
SLOW_MOTION_FACTOR = 0.5  # 50% speed
SLOW_MOTION_DURATION = 5000  # 5 seconds in milliseconds
SLOW_MOTION_COOLDOWN = 30000  # 30 seconds in milliseconds

# Era-specific power cooldowns (in milliseconds)
PREHISTORIC_POWER_COOLDOWN = 15000  # 15 seconds
MEDIEVAL_POWER_COOLDOWN = 3000  # 3 seconds
FUTURISTIC_POWER_COOLDOWN = 60000  # 60 seconds

# Combat settings
MELEE_DAMAGE = 20
PROJECTILE_BASE_DAMAGE = 15
PROJECTILE_SPEED = 600.0  # pixels per second

# Save system
SAVE_COST = 50  # In-game currency cost for manual saves
MAX_SAVE_SLOTS = 3

# Asset paths
ASSET_DIR = "assets"
SPRITE_DIR = f"{ASSET_DIR}/sprites"
SOUND_DIR = f"{ASSET_DIR}/sounds"

# Keybindings
class Keys:
    MOVE_LEFT = "a"
    MOVE_RIGHT = "d"
    JUMP = "space"
    ATTACK = "mouse1"
    BLOCK = "mouse2"
    SLOW_TIME = "shift"
    ERA_POWER = "e"
    SWITCH_ERA_NEXT = "q"
    SWITCH_ERA_PREV = "z"
    PAUSE = "escape"
    QUICK_SAVE = "f5"
    QUICK_LOAD = "f9"