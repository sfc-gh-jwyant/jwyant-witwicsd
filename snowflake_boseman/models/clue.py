"""Clue model and generation."""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ClueType(Enum):
    """Types of clues in the game."""
    DESTINATION = "destination"  # Hints about where suspect is going
    SUSPECT = "suspect"          # Describes suspect's appearance/habits
    RED_HERRING = "red_herring"  # False lead to confuse player


@dataclass
class Clue:
    """A clue gathered during investigation."""
    id: str
    clue_type: ClueType
    text: str
    source: str = "Witness"  # Who provided the clue
    location_id: Optional[str] = None  # Where clue was found
    image_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Clue":
        """Create Clue from database row dict."""
        clue_type_str = data.get("CLUE_TYPE", "destination")
        try:
            clue_type = ClueType(clue_type_str)
        except ValueError:
            clue_type = ClueType.DESTINATION
            
        return cls(
            id=data.get("CLUE_ID", ""),
            clue_type=clue_type,
            text=data.get("TEXT", ""),
            source=data.get("SOURCE", "Witness"),
            location_id=data.get("LOCATION_ID"),
            image_url=data.get("IMAGE_URL"),
        )
    
    @property
    def type_display(self) -> str:
        """Get display name for clue type."""
        return {
            ClueType.DESTINATION: "🗺️ Destination Clue",
            ClueType.SUSPECT: "🕵️ Suspect Description",
            ClueType.RED_HERRING: "🐟 Information",
        }.get(self.clue_type, "📝 Clue")
    
    @property
    def icon(self) -> str:
        """Get icon for clue type."""
        return {
            ClueType.DESTINATION: "🗺️",
            ClueType.SUSPECT: "🕵️",
            ClueType.RED_HERRING: "🐟",
        }.get(self.clue_type, "📝")


# Difficulty clarity mapping for clue generation
DIFFICULTY_CLARITY = {
    1: "very obvious and direct",
    2: "clear but requires some thought",
    3: "somewhat cryptic with hints",
    4: "cryptic riddle-style",
    5: "extremely cryptic puzzle that requires deep knowledge",
}

