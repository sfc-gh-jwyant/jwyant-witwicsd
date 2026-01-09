"""Time management for game mechanics."""

from dataclasses import dataclass
from typing import Optional

from .location import Location


# Difficulty configuration
# Format: (time_budget_hours, clue_clarity, num_locations, num_red_herrings)
DIFFICULTY_CONFIG = {
    1: {
        "name": "SELECT * FROM clues",
        "time_budget": 72,
        "clarity": "very obvious",
        "min_locations": 3,
        "max_locations": 4,
        "red_herrings": 0,
        "description": "Easy mode - all clues are crystal clear",
    },
    2: {
        "name": "WITH (NOLOCK)",
        "time_budget": 48,
        "clarity": "clear",
        "min_locations": 4,
        "max_locations": 5,
        "red_herrings": 1,
        "description": "Normal mode - clues require some thought",
    },
    3: {
        "name": "Foreign Key Violation",
        "time_budget": 36,
        "clarity": "cryptic",
        "min_locations": 5,
        "max_locations": 7,
        "red_herrings": 2,
        "description": "Hard mode - cryptic clues and false leads",
    },
    4: {
        "name": "Deadlock Victim",
        "time_budget": 24,
        "clarity": "very cryptic",
        "min_locations": 6,
        "max_locations": 8,
        "red_herrings": 3,
        "description": "Expert mode - riddles and misdirection",
    },
    5: {
        "name": "Little Bobby Tables",
        "time_budget": 12,
        "clarity": "riddles only",
        "min_locations": 8,
        "max_locations": 10,
        "red_herrings": 4,
        "description": "Nightmare mode - only for the bravest detectives",
    },
}

# Time costs for actions
INVESTIGATION_TIME_COST = 2  # Hours spent investigating at a location
TRAVEL_TIME_MINIMUM = 2      # Minimum travel time even for nearby cities


@dataclass
class TimeManager:
    """Manages game time and travel calculations."""
    
    difficulty: int
    total_hours: int
    elapsed_hours: int = 0
    
    def __init__(self, difficulty: int, elapsed_hours: int = 0):
        """Initialize time manager for given difficulty."""
        self.difficulty = difficulty
        config = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG[1])
        self.total_hours = config["time_budget"]
        self.elapsed_hours = elapsed_hours
    
    @property
    def hours_remaining(self) -> int:
        """Get hours remaining."""
        return max(0, self.total_hours - self.elapsed_hours)
    
    @property
    def is_time_up(self) -> bool:
        """Check if time has run out."""
        return self.hours_remaining <= 0
    
    @property
    def time_percentage(self) -> float:
        """Get percentage of time remaining (0-100)."""
        if self.total_hours == 0:
            return 0
        return (self.hours_remaining / self.total_hours) * 100
    
    @property
    def urgency_level(self) -> str:
        """Get urgency level based on time remaining."""
        pct = self.time_percentage
        if pct > 50:
            return "normal"
        elif pct > 25:
            return "warning"
        else:
            return "critical"
    
    def travel(self, from_loc: Location, to_loc: Location) -> tuple[bool, int]:
        """
        Deduct travel time for moving between locations.
        
        Returns:
            Tuple of (success, hours_spent)
            Success is False if not enough time remaining.
        """
        travel_time = from_loc.get_travel_time_to(to_loc)
        
        if travel_time > self.hours_remaining:
            return False, travel_time
        
        self.elapsed_hours += travel_time
        return True, travel_time
    
    def investigate(self) -> tuple[bool, int]:
        """
        Deduct time for investigating at current location.
        
        Returns:
            Tuple of (success, hours_spent)
            Success is False if not enough time remaining.
        """
        if INVESTIGATION_TIME_COST > self.hours_remaining:
            return False, INVESTIGATION_TIME_COST
        
        self.elapsed_hours += INVESTIGATION_TIME_COST
        return True, INVESTIGATION_TIME_COST
    
    def can_travel_to(self, from_loc: Location, to_loc: Location) -> bool:
        """Check if there's enough time to travel to destination."""
        travel_time = from_loc.get_travel_time_to(to_loc)
        return travel_time <= self.hours_remaining
    
    def can_investigate(self) -> bool:
        """Check if there's enough time to investigate."""
        return INVESTIGATION_TIME_COST <= self.hours_remaining
    
    def format_time_remaining(self) -> str:
        """Format remaining time for display."""
        hours = self.hours_remaining
        if hours >= 24:
            days = hours // 24
            remaining_hours = hours % 24
            if remaining_hours > 0:
                return f"{days}d {remaining_hours}h"
            return f"{days} day{'s' if days > 1 else ''}"
        return f"{hours} hour{'s' if hours != 1 else ''}"
    
    @staticmethod
    def get_difficulty_info(difficulty: int) -> dict:
        """Get configuration info for a difficulty level."""
        return DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG[1])

