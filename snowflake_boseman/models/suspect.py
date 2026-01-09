"""Suspect model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Suspect:
    """A suspect in the game."""
    id: str
    name: str
    hair_color: str
    eye_color: str
    hobby: str
    vehicle: str
    favorite_food: str
    distinguishing_feature: str = ""
    mugshot_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Suspect":
        """Create Suspect from database row dict."""
        return cls(
            id=data.get("SUSPECT_ID", ""),
            name=data.get("NAME", ""),
            hair_color=data.get("HAIR_COLOR", ""),
            eye_color=data.get("EYE_COLOR", ""),
            hobby=data.get("HOBBY", ""),
            vehicle=data.get("VEHICLE", ""),
            favorite_food=data.get("FAVORITE_FOOD", ""),
            distinguishing_feature=data.get("DISTINGUISHING_FEATURE", ""),
            mugshot_url=data.get("MUGSHOT_URL"),
        )
    
    @property
    def traits(self) -> dict[str, str]:
        """Get all identifying traits as a dictionary."""
        return {
            "Hair Color": self.hair_color,
            "Eye Color": self.eye_color,
            "Hobby": self.hobby,
            "Vehicle": self.vehicle,
            "Favorite Food": self.favorite_food,
            "Distinguishing Feature": self.distinguishing_feature,
        }
    
    def matches_clues(self, known_traits: dict[str, str]) -> bool:
        """Check if this suspect matches the known clues."""
        for trait_name, trait_value in known_traits.items():
            if trait_name in self.traits:
                if self.traits[trait_name].lower() != trait_value.lower():
                    return False
        return True

