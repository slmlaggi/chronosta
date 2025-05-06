import json
import os
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from config import Era

class SaveManager:
    def __init__(self, save_dir: str = "saves") -> None:
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum of save data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _validate_checksum(self, data: Dict[str, Any], stored_checksum: str) -> bool:
        """Validate save data integrity."""
        return self._calculate_checksum(data["game_data"]) == stored_checksum

    def save_game(self, player_data: Dict[str, Any], game_state: Dict[str, Any], 
                 save_type: str = "manual", slot: int = 0) -> bool:
        """Save game state to file."""
        try:
            save_data = {
                "game_data": {
                    "player": player_data,
                    "state": game_state,
                    "timestamp": datetime.now().isoformat(),
                    "save_type": save_type
                }
            }
            
            # Calculate checksum
            checksum = self._calculate_checksum(save_data["game_data"])
            save_data["checksum"] = checksum
            
            # Create save filename
            filename = f"save_{save_type}_{slot}.json"
            filepath = os.path.join(self.save_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, save_type: str = "manual", slot: int = 0) -> Optional[Dict[str, Any]]:
        """Load game state from file."""
        try:
            filename = f"save_{save_type}_{slot}.json"
            filepath = os.path.join(self.save_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Validate checksum
            if not self._validate_checksum(save_data, save_data["checksum"]):
                print("Save file corruption detected!")
                return self._load_fallback_save()
            
            return save_data["game_data"]
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def _load_fallback_save(self) -> Optional[Dict[str, Any]]:
        """Attempt to load the last valid checkpoint save."""
        try:
            saves = [f for f in os.listdir(self.save_dir) 
                    if f.startswith("save_checkpoint_")]
            if not saves:
                return None
                
            # Sort by modification time, newest first
            saves.sort(key=lambda x: os.path.getmtime(
                os.path.join(self.save_dir, x)), reverse=True)
            
            # Try loading saves until we find a valid one
            for save in saves:
                filepath = os.path.join(self.save_dir, save)
                with open(filepath, 'r') as f:
                    save_data = json.load(f)
                
                if self._validate_checksum(save_data, save_data["checksum"]):
                    return save_data["game_data"]
            
            return None
            
        except Exception as e:
            print(f"Error loading fallback save: {e}")
            return None

    def create_checkpoint(self, player_data: Dict[str, Any], 
                         game_state: Dict[str, Any]) -> bool:
        """Create an automatic checkpoint save."""
        return self.save_game(player_data, game_state, "checkpoint")

    def create_suspend_save(self, player_data: Dict[str, Any], 
                          game_state: Dict[str, Any]) -> bool:
        """Create a temporary suspend save."""
        success = self.save_game(player_data, game_state, "suspend")
        if success:
            # Schedule cleanup of suspend save on next load
            self._mark_suspend_for_deletion()
        return success

    def _mark_suspend_for_deletion(self) -> None:
        """Mark suspend save for deletion on next game load."""
        marker_file = os.path.join(self.save_dir, ".suspend_cleanup")
        with open(marker_file, 'w') as f:
            f.write(datetime.now().isoformat())

    def cleanup_suspend_save(self) -> None:
        """Remove suspend save if it exists."""
        suspend_save = os.path.join(self.save_dir, "save_suspend_0.json")
        marker_file = os.path.join(self.save_dir, ".suspend_cleanup")
        
        if os.path.exists(suspend_save):
            os.remove(suspend_save)
        if os.path.exists(marker_file):
            os.remove(marker_file)

    def list_save_files(self) -> Dict[str, list]:
        """List all available save files grouped by type."""
        saves = {
            "manual": [],
            "checkpoint": [],
            "suspend": []
        }
        
        try:
            for filename in os.listdir(self.save_dir):
                if filename.startswith("save_"):
                    save_type = filename.split("_")[1]
                    if save_type in saves:
                        with open(os.path.join(self.save_dir, filename), 'r') as f:
                            data = json.load(f)
                            saves[save_type].append({
                                "slot": int(filename.split("_")[-1].split(".")[0]),
                                "timestamp": data["game_data"]["timestamp"],
                                "era": data["game_data"]["state"].get("current_era", "unknown")
                            })
        except Exception as e:
            print(f"Error listing save files: {e}")
        
        return saves