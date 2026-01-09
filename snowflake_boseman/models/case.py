"""Case model representing an active investigation."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum

from .location import Location
from .suspect import Suspect
from .clue import Clue


class CaseStatus(Enum):
    """Status of a case."""
    ACTIVE = "active"
    WON = "won"
    LOST_TIME = "lost_time"
    LOST_WRONG_ARREST = "lost_wrong_arrest"
    ABANDONED = "abandoned"


# Stolen items for case variety
STOLEN_ITEMS = [
    "the Crown Jewels of England",
    "the Mona Lisa",
    "the Hope Diamond",
    "the Declaration of Independence",
    "King Tut's golden mask",
    "the Rosetta Stone",
    "the Holy Grail",
    "the Statue of Liberty's torch",
    "a NASA moon rock",
    "the original Bitcoin wallet",
    "the recipe for Coca-Cola",
    "Einstein's original E=mc² notes",
    "Cleopatra's lost crown",
    "the Dead Sea Scrolls",
    "a priceless Fabergé egg",
    "Van Gogh's Starry Night",
    "the Olympic flame",
    "a dinosaur fossil",
    "the Liberty Bell",
    "Shakespeare's first folio",
]


@dataclass
class CaseProgress:
    """Tracks progress within an active case."""
    case_id: str
    current_location_id: str
    suspect_location_idx: int = 0  # Where suspect currently is in their path
    hours_remaining: int = 72
    clues_gathered: list[Clue] = field(default_factory=list)
    locations_visited: list[str] = field(default_factory=list)
    correct_travels: int = 0
    wrong_travels: int = 0
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "CaseProgress":
        """Create CaseProgress from database row dict."""
        # Parse clues from stored array
        clues_data = data.get("CLUES_GATHERED", []) or []
        clues = []
        for clue_data in clues_data:
            if isinstance(clue_data, dict):
                clues.append(Clue.from_dict(clue_data))
        
        return cls(
            case_id=data.get("CASE_ID", ""),
            current_location_id=data.get("CURRENT_LOCATION_ID", ""),
            suspect_location_idx=data.get("SUSPECT_LOCATION_IDX", 0),
            hours_remaining=data.get("HOURS_REMAINING", 72),
            clues_gathered=clues,
            locations_visited=data.get("LOCATIONS_VISITED", []) or [],
            updated_at=data.get("UPDATED_AT"),
        )
    
    @property
    def is_time_up(self) -> bool:
        """Check if time has run out."""
        return self.hours_remaining <= 0


@dataclass
class Case:
    """An investigation case."""
    id: str
    player_id: str
    suspect: Suspect
    stolen_item: str
    difficulty: int
    location_path: list[str]  # List of location IDs the suspect will visit
    status: CaseStatus = CaseStatus.ACTIVE
    started_at: Optional[datetime] = None
    progress: Optional[CaseProgress] = None
    
    @classmethod
    def from_dict(cls, data: dict, suspect: Optional[Suspect] = None) -> "Case":
        """Create Case from database row dict."""
        status_str = data.get("STATUS", "active")
        try:
            status = CaseStatus(status_str)
        except ValueError:
            status = CaseStatus.ACTIVE
            
        return cls(
            id=data.get("CASE_ID", ""),
            player_id=data.get("PLAYER_ID", ""),
            suspect=suspect or Suspect.from_dict({}),
            stolen_item=data.get("STOLEN_ITEM", ""),
            difficulty=data.get("DIFFICULTY", 1),
            location_path=data.get("LOCATION_PATH", []) or [],
            status=status,
            started_at=data.get("STARTED_AT"),
        )
    
    @property
    def difficulty_name(self) -> str:
        """Get the fun name for this difficulty level."""
        names = {
            1: "SELECT * FROM clues",
            2: "WITH (NOLOCK)",
            3: "Foreign Key Violation",
            4: "Deadlock Victim",
            5: "Little Bobby Tables",
        }
        return names.get(self.difficulty, "Unknown")
    
    @property
    def is_active(self) -> bool:
        """Check if case is still active."""
        return self.status == CaseStatus.ACTIVE
    
    @property
    def is_won(self) -> bool:
        """Check if case was won."""
        return self.status == CaseStatus.WON
    
    def get_suspect_current_location(self) -> Optional[str]:
        """Get the location ID where suspect currently is."""
        if self.progress and self.progress.suspect_location_idx < len(self.location_path):
            return self.location_path[self.progress.suspect_location_idx]
        return self.location_path[-1] if self.location_path else None
    
    def get_suspect_next_location(self) -> Optional[str]:
        """Get the location ID where suspect is heading next."""
        if self.progress:
            next_idx = self.progress.suspect_location_idx + 1
            if next_idx < len(self.location_path):
                return self.location_path[next_idx]
        return None
    
    def is_player_at_suspect_location(self, current_location_id: str) -> bool:
        """Check if player is at same location as suspect."""
        suspect_location = self.get_suspect_current_location()
        return current_location_id == suspect_location

