"""Player model."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# Rank progression based on cases solved
RANK_THRESHOLDS = [
    (0, "Rookie"),
    (3, "Gumshoe"),
    (7, "Detective"),
    (15, "Investigator"),
    (25, "Senior Agent"),
    (40, "Super Sleuth"),
    (60, "Master Detective"),
    (100, "Legend"),
]


@dataclass
class Player:
    """A player in the game."""
    id: str
    snowflake_user: str
    email: Optional[str] = None
    rank: str = "Rookie"
    cases_solved: int = 0
    total_score: int = 0
    created_at: Optional[datetime] = None
    current_case_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create Player from database row dict."""
        return cls(
            id=data.get("PLAYER_ID", ""),
            snowflake_user=data.get("SNOWFLAKE_USER", ""),
            email=data.get("EMAIL"),
            rank=data.get("RANK", "Rookie"),
            cases_solved=data.get("CASES_SOLVED", 0),
            total_score=data.get("TOTAL_SCORE", 0),
            created_at=data.get("CREATED_AT"),
        )
    
    @property
    def display_name(self) -> str:
        """Get display name (username without domain if email-style)."""
        name = self.snowflake_user
        if "@" in name:
            name = name.split("@")[0]
        return name.replace("_", " ").title()
    
    def calculate_rank(self) -> str:
        """Calculate rank based on cases solved."""
        current_rank = "Rookie"
        for threshold, rank_name in RANK_THRESHOLDS:
            if self.cases_solved >= threshold:
                current_rank = rank_name
        return current_rank
    
    def update_rank(self) -> bool:
        """Update rank if player has leveled up. Returns True if rank changed."""
        new_rank = self.calculate_rank()
        if new_rank != self.rank:
            self.rank = new_rank
            return True
        return False
    
    @property
    def rank_icon(self) -> str:
        """Get icon for current rank."""
        icons = {
            "Rookie": "🔰",
            "Gumshoe": "👟",
            "Detective": "🔍",
            "Investigator": "📋",
            "Senior Agent": "🎖️",
            "Super Sleuth": "🦸",
            "Master Detective": "🏆",
            "Legend": "👑",
        }
        return icons.get(self.rank, "🔰")
    
    def cases_until_next_rank(self) -> Optional[int]:
        """Get number of cases needed for next rank."""
        for threshold, rank_name in RANK_THRESHOLDS:
            if threshold > self.cases_solved:
                return threshold - self.cases_solved
        return None  # Already at max rank

