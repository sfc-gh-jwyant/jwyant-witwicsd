"""
WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?

A geography mystery adventure game inspired by Carmen Sandiego.
Built with Streamlit in Snowflake.

SINGLE FILE VERSION FOR STREAMLIT IN SNOWFLAKE
(SiS doesn't support relative imports or package structures)
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import random
import math
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

# Database and Schema Configuration
# Set TABLE_PREFIX to use explicit fully-qualified table names
# Set to empty string "" to use the session's default context
TABLE_PREFIX = "DEMO_WITWISBM.GAME."  # e.g., "DEMO_WITWISBM.GAME." or ""


DIFFICULTY_CONFIG = {
    1: {
        "name": "SELECT * FROM clues",
        "description": "All clues visible, lots of time",
        "time_budget": 72,
        "clue_clarity": "obvious",
        "min_locations": 3,
        "max_locations": 4,
        "red_herrings": 0,
    },
    2: {
        "name": "WITH (NOLOCK)",
        "description": "Clear hints, moderate challenge",
        "time_budget": 48,
        "clue_clarity": "clear",
        "min_locations": 4,
        "max_locations": 5,
        "red_herrings": 1,
    },
    3: {
        "name": "Foreign Key Violation",
        "description": "Cryptic clues, tighter deadline",
        "time_budget": 36,
        "clue_clarity": "cryptic",
        "min_locations": 5,
        "max_locations": 7,
        "red_herrings": 2,
    },
    4: {
        "name": "Deadlock Victim",
        "description": "Very cryptic, time pressure",
        "time_budget": 24,
        "clue_clarity": "very_cryptic",
        "min_locations": 6,
        "max_locations": 8,
        "red_herrings": 3,
    },
    5: {
        "name": "Little Bobby Tables",
        "description": "Expert mode - riddles only",
        "time_budget": 12,
        "clue_clarity": "riddle",
        "min_locations": 8,
        "max_locations": 10,
        "red_herrings": 4,
    },
}

INVESTIGATION_TIME = 2  # Hours per investigation

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Landmark:
    """A notable landmark at a location."""
    id: str
    name: str
    landmark_type: str
    clue_facts: List[str] = field(default_factory=list)
    image_url: Optional[str] = None


@dataclass
class Location:
    """A city/location in the game world."""
    id: str
    city: str
    country: str
    continent: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    landmarks: List[Landmark] = field(default_factory=list)
    
    def get_travel_time_to(self, other: "Location") -> int:
        """Calculate travel time in hours to another location."""
        distance = self._haversine_distance(other)
        hours = max(1, int(distance / 800))  # ~800 km/hr average
        return hours
    
    def _haversine_distance(self, other: "Location") -> float:
        """Calculate great-circle distance in km."""
        R = 6371  # Earth radius in km
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))


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
        return cls(
            id=data.get("SUSPECT_ID", data.get("suspect_id", "")),
            name=data.get("NAME", data.get("name", "")),
            hair_color=data.get("HAIR_COLOR", data.get("hair_color", "")),
            eye_color=data.get("EYE_COLOR", data.get("eye_color", "")),
            hobby=data.get("HOBBY", data.get("hobby", "")),
            vehicle=data.get("VEHICLE", data.get("vehicle", "")),
            favorite_food=data.get("FAVORITE_FOOD", data.get("favorite_food", "")),
            distinguishing_feature=data.get("DISTINGUISHING_FEATURE", data.get("distinguishing_feature", "")),
            mugshot_url=data.get("MUGSHOT_URL", data.get("mugshot_url")),
        )


@dataclass
class Clue:
    """A clue discovered during investigation."""
    id: str
    clue_type: str  # "destination", "suspect", "red_herring"
    text: str
    difficulty_min: int = 1
    source: str = "witness"


@dataclass
class Player:
    """A player in the game."""
    id: str
    snowflake_user: str
    rank: str = "Rookie"
    cases_solved: int = 0
    total_score: int = 0
    
    @property
    def display_name(self) -> str:
        return self.snowflake_user.split("@")[0].title()
    
    @property
    def rank_icon(self) -> str:
        icons = {
            "Rookie": "🔰",
            "Gumshoe": "🔎",
            "Detective": "🕵️",
            "Investigator": "🎖️",
            "Super Sleuth": "⭐",
            "Master Detective": "🏆",
        }
        return icons.get(self.rank, "🔰")
    
    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        return cls(
            id=data.get("PLAYER_ID", data.get("player_id", "")),
            snowflake_user=data.get("SNOWFLAKE_USER", data.get("snowflake_user", "")),
            rank=data.get("RANK", data.get("rank", "Rookie")),
            cases_solved=data.get("CASES_SOLVED", data.get("cases_solved", 0)),
            total_score=data.get("TOTAL_SCORE", data.get("total_score", 0)),
        )
    
    def update_rank(self) -> None:
        """Update rank based on cases solved."""
        if self.cases_solved >= 50:
            self.rank = "Master Detective"
        elif self.cases_solved >= 25:
            self.rank = "Super Sleuth"
        elif self.cases_solved >= 10:
            self.rank = "Investigator"
        elif self.cases_solved >= 5:
            self.rank = "Detective"
        elif self.cases_solved >= 1:
            self.rank = "Gumshoe"


class CaseStatus(Enum):
    ACTIVE = "active"
    WON = "won"
    LOST_TIME = "lost_time"
    LOST_WRONG_ARREST = "lost_wrong_arrest"
    ABANDONED = "abandoned"


@dataclass
class CaseProgress:
    """Tracks progress within a case."""
    current_location_id: str
    suspect_location_idx: int = 0
    hours_remaining: int = 72
    clues_gathered: List[Clue] = field(default_factory=list)
    locations_visited: List[str] = field(default_factory=list)
    correct_travels: int = 0
    wrong_travels: int = 0


@dataclass
class Case:
    """A case/investigation in the game."""
    id: str
    player_id: str
    suspect: Suspect
    stolen_item: str
    difficulty: int
    location_path: List[str]
    status: CaseStatus = CaseStatus.ACTIVE
    progress: Optional[CaseProgress] = None
    
    @property
    def is_active(self) -> bool:
        return self.status == CaseStatus.ACTIVE
    
    def get_suspect_next_location(self) -> Optional[str]:
        """Get the next location in suspect's path."""
        if self.progress and self.progress.suspect_location_idx < len(self.location_path) - 1:
            return self.location_path[self.progress.suspect_location_idx + 1]
        return None
    
    def is_player_at_suspect_location(self, player_location_id: str) -> bool:
        """Check if player has caught up to suspect."""
        if not self.progress:
            return False
        suspect_loc_idx = min(self.progress.suspect_location_idx, len(self.location_path) - 1)
        suspect_current_loc = self.location_path[suspect_loc_idx]
        return player_location_id == suspect_current_loc


class TimeManager:
    """Manages time budget for a case."""
    
    def __init__(self, difficulty: int, elapsed_hours: int = 0):
        self.difficulty = difficulty
        self.total_hours = DIFFICULTY_CONFIG[difficulty]["time_budget"]
        self.elapsed_hours = elapsed_hours
    
    @property
    def hours_remaining(self) -> int:
        return max(0, self.total_hours - self.elapsed_hours)
    
    @property
    def is_time_up(self) -> bool:
        return self.hours_remaining <= 0
    
    @property
    def time_percentage(self) -> float:
        return (self.hours_remaining / self.total_hours) * 100
    
    @property
    def urgency_level(self) -> str:
        pct = self.time_percentage
        if pct <= 15:
            return "critical"
        elif pct <= 35:
            return "warning"
        return "normal"
    
    def travel(self, from_loc: Location, to_loc: Location) -> tuple[bool, int]:
        """Deduct travel time. Returns (success, hours_spent)."""
        hours = from_loc.get_travel_time_to(to_loc)
        if hours > self.hours_remaining:
            return False, hours
        self.elapsed_hours += hours
        return True, hours
    
    def investigate(self) -> tuple[bool, int]:
        """Deduct investigation time."""
        if INVESTIGATION_TIME > self.hours_remaining:
            return False, INVESTIGATION_TIME
        self.elapsed_hours += INVESTIGATION_TIME
        return True, INVESTIGATION_TIME
    
    def can_travel_to(self, from_loc: Location, to_loc: Location) -> bool:
        """Check if there's enough time to travel."""
        hours = from_loc.get_travel_time_to(to_loc)
        return hours <= self.hours_remaining


# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

@st.cache_resource
def get_snowflake_session():
    """Get the Snowflake session."""
    # In Streamlit in Snowflake, use the active session
    from snowflake.snowpark.context import get_active_session
    return get_active_session()


def execute_query(sql: str) -> List[Dict]:
    """Execute a read query and return results as list of dicts."""
    try:
        session = get_snowflake_session()
        result = session.sql(sql).collect()
        return [row.as_dict() for row in result]
    except Exception as e:
        st.error(f"Query error: {e}")
        st.exception(e)
        return []


def execute_write(sql: str) -> bool:
    """Execute a write query."""
    try:
        session = get_snowflake_session()
        session.sql(sql).collect()
        return True
    except Exception as e:
        st.error(f"Write error: {e}")
        return False


def get_current_user() -> Dict[str, str]:
    """Get current Snowflake user info."""
    try:
        session = get_snowflake_session()
        result = session.sql("""
            SELECT CURRENT_USER() as username, 
                   CURRENT_ROLE() as role
        """).collect()[0]
        return {"username": result["USERNAME"], "role": result["ROLE"]}
    except Exception:
        return {"username": "demo_user", "role": "PUBLIC"}


# =============================================================================
# GAME LOGIC
# =============================================================================

class GameController:
    """Main controller for game logic."""
    
    def __init__(self):
        self._current_player: Optional[Player] = None
        self._current_case: Optional[Case] = None
        self._time_manager: Optional[TimeManager] = None
        self._locations_cache: List[Location] = []
        self._suspects_cache: List[Suspect] = []
    
    def get_or_create_player(self) -> Player:
        """Get current player from Snowflake session."""
        if self._current_player:
            return self._current_player
        
        user_info = get_current_user()
        player_id = user_info["username"]
        
        rows = execute_query(f"SELECT * FROM {TABLE_PREFIX}players WHERE player_id = '{player_id}'")
        
        if rows:
            self._current_player = Player.from_dict(rows[0])
        else:
            execute_write(f"""
                INSERT INTO {TABLE_PREFIX}players (player_id, snowflake_user, rank, cases_solved, total_score)
                VALUES ('{player_id}', '{player_id}', 'Rookie', 0, 0)
            """)
            self._current_player = Player(
                id=player_id,
                snowflake_user=player_id,
                rank="Rookie",
                cases_solved=0,
                total_score=0,
            )
        
        return self._current_player
    
    def get_all_locations(self) -> List[Location]:
        """Get all locations from database."""
        if self._locations_cache:
            return self._locations_cache
        
        rows = execute_query(f"SELECT * FROM {TABLE_PREFIX}locations")
        self._locations_cache = [
            Location(
                id=r.get("LOCATION_ID", r.get("location_id", "")),
                city=r.get("CITY", r.get("city", "")),
                country=r.get("COUNTRY", r.get("country", "")),
                continent=r.get("CONTINENT", r.get("continent", "")),
                latitude=float(r.get("LATITUDE", r.get("latitude", 0))),
                longitude=float(r.get("LONGITUDE", r.get("longitude", 0))),
                description=r.get("DESCRIPTION", r.get("description")),
                image_url=r.get("IMAGE_URL", r.get("image_url")),
            )
            for r in rows
        ]
        return self._locations_cache
    
    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        """Get a specific location by ID."""
        locations = self.get_all_locations()
        for loc in locations:
            if loc.id == location_id:
                return loc
        return None
    
    def get_all_suspects(self) -> List[Suspect]:
        """Get all suspects from database."""
        if self._suspects_cache:
            return self._suspects_cache
        
        rows = execute_query(f"SELECT * FROM {TABLE_PREFIX}suspects")
        self._suspects_cache = [Suspect.from_dict(r) for r in rows]
        return self._suspects_cache
    
    def start_new_case(self, difficulty: int) -> Case:
        """Start a new case."""
        player = self.get_or_create_player()
        locations = self.get_all_locations()
        suspects = self.get_all_suspects()
        
        if not locations or not suspects:
            raise ValueError("No locations or suspects available")
        
        # Pick random suspect and generate path
        suspect = random.choice(suspects)
        config = DIFFICULTY_CONFIG[difficulty]
        num_locations = random.randint(config["min_locations"], config["max_locations"])
        
        # Start at Bozeman
        start_loc = self.get_location_by_id("loc_bozeman") or locations[0]
        path = [start_loc.id]
        
        # Generate path through random locations
        available = [l for l in locations if l.id != start_loc.id]
        for _ in range(num_locations - 1):
            if available:
                next_loc = random.choice(available)
                path.append(next_loc.id)
                available.remove(next_loc)
        
        # Create case
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        stolen_items = [
            "the Declaration of Independence",
            "the Hope Diamond",
            "the Mona Lisa",
            "the Crown Jewels",
            "ancient scrolls",
            "a rare data warehouse",
            "the Snowflake source code",
        ]
        
        case = Case(
            id=case_id,
            player_id=player.id,
            suspect=suspect,
            stolen_item=random.choice(stolen_items),
            difficulty=difficulty,
            location_path=path,
            status=CaseStatus.ACTIVE,
            progress=CaseProgress(
                current_location_id=start_loc.id,
                hours_remaining=config["time_budget"],
                locations_visited=[start_loc.id],
            ),
        )
        
        self._current_case = case
        self._time_manager = TimeManager(difficulty)
        
        return case
    
    def get_current_case(self) -> Optional[Case]:
        """Get the current active case."""
        return self._current_case
    
    def get_current_location(self) -> Optional[Location]:
        """Get player's current location."""
        case = self.get_current_case()
        if not case or not case.progress:
            return None
        return self.get_location_by_id(case.progress.current_location_id)
    
    def get_available_destinations(self) -> List[Location]:
        """Get locations the player can travel to."""
        current = self.get_current_location()
        if not current:
            return []
        
        available = []
        for loc in self.get_all_locations():
            if loc.id != current.id:
                if self._time_manager and self._time_manager.can_travel_to(current, loc):
                    available.append(loc)
        
        available.sort(key=lambda l: current._haversine_distance(l))
        return available
    
    def travel_to(self, destination_id: str) -> Dict:
        """Travel to a new location."""
        case = self.get_current_case()
        current = self.get_current_location()
        destination = self.get_location_by_id(destination_id)
        
        if not case or not current or not destination:
            return {"success": False, "message": "Cannot travel right now."}
        
        success, hours_spent = self._time_manager.travel(current, destination)
        
        if not success:
            return {
                "success": False,
                "message": f"Not enough time! Need {hours_spent} hours.",
            }
        
        # Update progress
        case.progress.current_location_id = destination_id
        case.progress.hours_remaining = self._time_manager.hours_remaining
        case.progress.locations_visited.append(destination_id)
        
        # Check if correct direction
        correct_next = case.get_suspect_next_location()
        is_correct = destination_id == correct_next
        
        if is_correct:
            case.progress.correct_travels += 1
            case.progress.suspect_location_idx += 1
        else:
            case.progress.wrong_travels += 1
        
        arrived_at_suspect = case.is_player_at_suspect_location(destination_id)
        
        if self._time_manager.is_time_up:
            case.status = CaseStatus.LOST_TIME
            return {
                "success": True,
                "message": "Time has run out! The suspect escaped.",
                "game_over": True,
            }
        
        return {
            "success": True,
            "message": f"Arrived in {destination.city}, {destination.country}. ({hours_spent} hours)",
            "hours_spent": hours_spent,
            "arrived_at_suspect": arrived_at_suspect,
        }
    
    def investigate(self) -> List[Clue]:
        """Investigate current location for clues."""
        case = self.get_current_case()
        current = self.get_current_location()
        
        if not case or not current:
            return []
        
        success, _ = self._time_manager.investigate()
        if not success:
            return []
        
        case.progress.hours_remaining = self._time_manager.hours_remaining
        
        # Generate clues
        next_location_id = case.get_suspect_next_location()
        next_location = self.get_location_by_id(next_location_id) if next_location_id else None
        
        clues = self._generate_clues(case, current, next_location)
        case.progress.clues_gathered.extend(clues)
        
        return clues
    
    def _generate_clues(self, case: Case, current: Location, next_loc: Optional[Location]) -> List[Clue]:
        """Generate clues for investigation."""
        clues = []
        
        # Destination clue
        if next_loc:
            dest_hints = [
                f"I overheard them mention heading to a city in {next_loc.continent}.",
                f"They were looking at maps of {next_loc.country}.",
                f"Someone mentioned they're going somewhere near latitude {next_loc.latitude:.0f}.",
            ]
            clues.append(Clue(
                id=f"clue_{uuid.uuid4().hex[:8]}",
                clue_type="destination",
                text=random.choice(dest_hints),
                source="witness",
            ))
        
        # Suspect clue
        suspect_hints = [
            f"The person had {case.suspect.hair_color.lower()} hair.",
            f"They mentioned something about {case.suspect.hobby.lower()}.",
            f"I think they were driving a {case.suspect.vehicle.lower()}.",
            f"They ordered {case.suspect.favorite_food.lower()} at the restaurant.",
        ]
        clues.append(Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type="suspect",
            text=random.choice(suspect_hints),
            source="witness",
        ))
        
        return clues
    
    def attempt_arrest(self, suspect_id: str) -> Dict:
        """Attempt to arrest a suspect."""
        case = self.get_current_case()
        if not case:
            return {"success": False, "message": "No active case."}
        
        is_at_location = case.is_player_at_suspect_location(case.progress.current_location_id)
        is_correct = suspect_id == case.suspect.id
        
        if is_at_location and is_correct:
            # Win!
            case.status = CaseStatus.WON
            score = self._calculate_score(case)
            
            self._current_player.cases_solved += 1
            self._current_player.total_score += score
            self._current_player.update_rank()
            
            return {
                "won": True,
                "message": f"You caught {case.suspect.name}! Case solved!",
                "score": score,
            }
        elif not is_at_location:
            return {
                "won": False,
                "message": "The suspect isn't here! Keep following the trail.",
                "game_over": False,
            }
        else:
            case.status = CaseStatus.LOST_WRONG_ARREST
            return {
                "won": False,
                "message": f"Wrong suspect! {case.suspect.name} got away.",
                "game_over": True,
            }
    
    def _calculate_score(self, case: Case) -> int:
        """Calculate score for completed case."""
        multiplier = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
        time_bonus = max(0, self._time_manager.hours_remaining) * 100
        efficiency = max(0, 10 - len(case.progress.locations_visited)) * 50
        return (time_bonus + efficiency) * multiplier.get(case.difficulty, 1)
    
    def get_time_remaining(self) -> int:
        return self._time_manager.hours_remaining if self._time_manager else 0
    
    def get_time_percentage(self) -> float:
        return self._time_manager.time_percentage if self._time_manager else 100.0
    
    def get_urgency_level(self) -> str:
        return self._time_manager.urgency_level if self._time_manager else "normal"
    
    def get_gathered_clues(self) -> List[Clue]:
        case = self.get_current_case()
        return case.progress.clues_gathered if case and case.progress else []


# =============================================================================
# UI COMPONENTS
# =============================================================================

def apply_theme():
    """Apply custom CSS theme."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #5C1A1A 0%, #3D2817 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #C4A35A !important;
    }
    
    p, div, span, label {
        font-family: 'Source Sans Pro', sans-serif !important;
    }
    
    .stButton > button {
        background: linear-gradient(180deg, #C4A35A 0%, #8B7355 100%);
        color: #2A1810;
        border: 2px solid #3D2817;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(180deg, #D4B86A 0%, #9B8365 100%);
        border-color: #C4A35A;
        transform: translateY(-2px);
    }
    
    .stSelectbox > div > div {
        background: #D4B896;
        color: #2A1810;
    }
    </style>
    """, unsafe_allow_html=True)


def render_art_placeholder(art_type: str, alt_text: str, width: int = 200, height: int = 150):
    """Render a placeholder for missing art."""
    st.markdown(f"""
    <div style="
        width: {width}px;
        height: {height}px;
        background: linear-gradient(135deg, #3D2817 0%, #5C1A1A 100%);
        border: 2px dashed #C4A35A;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #C4A35A;
        font-family: 'Source Sans Pro', sans-serif;
        border-radius: 8px;
        margin: 10px auto;
    ">
        <span style="font-size: 2em;">🖼️</span>
        <span style="font-size: 0.8em; margin-top: 8px;">{art_type.upper()}</span>
        <span style="font-size: 0.7em; opacity: 0.7;">{alt_text}</span>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# GAME STATES
# =============================================================================

class GameState(Enum):
    MAIN_MENU = "main_menu"
    INVESTIGATION = "investigation"
    TRAVEL = "travel"
    ARREST = "arrest"
    CASE_RESULT = "case_result"


# =============================================================================
# PAGES
# =============================================================================

def render_main_menu(player: Player, has_active_case: bool) -> Dict:
    """Render main menu."""
    result = {"action": None}
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; margin-bottom: 30px;">
        <h1 style="color: #C4A35A; font-size: 2em; margin-bottom: 10px;">
            🔍 WHERE IN THE WORLD IS 🔍
        </h1>
        <h2 style="color: #F5E6D3; font-size: 1.8em; margin: 0;">
            ❄️ SNOWFLAKE BOSEMAN MONTANA? ❄️
        </h2>
        <p style="color: #D4B896; font-size: 14px; margin-top: 16px; font-style: italic;">
            A geography mystery adventure
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Player card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="
            background: #D4B896;
            border: 3px solid #3D2817;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <div style="font-size: 32px;">{player.rank_icon}</div>
            <div style="color: #2A1810; font-size: 18px; font-weight: bold;">
                Agent {player.display_name}
            </div>
            <div style="color: #555; font-size: 14px;">Rank: {player.rank}</div>
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 16px;">
                <div style="color: #3D2817;">
                    <div style="font-size: 24px; font-weight: bold;">{player.cases_solved}</div>
                    <div style="font-size: 11px;">Cases Solved</div>
                </div>
                <div style="color: #3D2817;">
                    <div style="font-size: 24px; font-weight: bold;">{player.total_score:,}</div>
                    <div style="font-size: 11px;">Total Score</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if has_active_case:
            if st.button("▶️ CONTINUE INVESTIGATION", use_container_width=True, type="primary"):
                result = {"action": "continue"}
            st.markdown("<br>", unsafe_allow_html=True)
        
        difficulty = st.selectbox(
            "Difficulty",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{DIFFICULTY_CONFIG[x]['name']}",
            label_visibility="collapsed",
        )
        
        if st.button("🔍 START NEW CASE", use_container_width=True):
            result = {"action": "new_case", "difficulty": difficulty}
    
    return result


def render_investigation(controller: GameController, case: Case, location: Location, player: Player) -> Dict:
    """Render investigation screen."""
    result = {"action": None}
    
    # Header with case info
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.markdown(f"""
        <div style="background: #D4B896; padding: 15px; border-radius: 8px;">
            <div style="color: #2A1810; font-weight: bold;">📋 Current Case</div>
            <div style="color: #555; font-size: 14px;">Stolen: {case.stolen_item}</div>
            <div style="color: #555; font-size: 14px;">Difficulty: {DIFFICULTY_CONFIG[case.difficulty]['name']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 15px;">
            <div style="color: #C4A35A; font-size: 24px; font-weight: bold;">
                📍 {location.city}, {location.country}
            </div>
            <div style="color: #D4B896;">{location.continent}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        urgency = controller.get_urgency_level()
        time_color = "#4CAF50" if urgency == "normal" else "#FFC107" if urgency == "warning" else "#F44336"
        st.markdown(f"""
        <div style="background: #3D2817; padding: 15px; border-radius: 8px; text-align: center;">
            <div style="color: {time_color}; font-size: 24px; font-weight: bold;">
                ⏱️ {controller.get_time_remaining()} hrs
            </div>
            <div style="color: #D4B896; font-size: 12px;">Time Remaining</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Location art placeholder
        render_art_placeholder("Location", location.city, 400, 250)
        
        if location.description:
            st.markdown(f"""
            <div style="background: #D4B896; padding: 15px; border-radius: 8px; margin-top: 15px;">
                <div style="color: #2A1810;">{location.description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### 📔 Clue Notebook")
        
        clues = controller.get_gathered_clues()
        if clues:
            for clue in clues[-5:]:  # Show last 5 clues
                icon = "🌍" if clue.clue_type == "destination" else "🔎"
                st.markdown(f"""
                <div style="background: #F5E6D3; padding: 10px; border-radius: 4px; margin-bottom: 8px; border-left: 3px solid #C4A35A;">
                    <span>{icon}</span> {clue.text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No clues yet. Investigate to gather clues!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 INVESTIGATE", use_container_width=True):
            result = {"action": "investigate"}
    
    with col2:
        if st.button("✈️ TRAVEL", use_container_width=True):
            result = {"action": "travel"}
    
    with col3:
        if st.button("🚨 ARREST", use_container_width=True):
            result = {"action": "arrest"}
    
    with col4:
        if st.button("🏠 MAIN MENU", use_container_width=True):
            result = {"action": "main_menu"}
    
    return result


def render_travel(controller: GameController, case: Case, current_location: Location) -> Dict:
    """Render travel screen."""
    result = {"action": None}
    
    st.markdown(f"### ✈️ Travel from {current_location.city}")
    
    if st.button("← Back to Investigation"):
        return {"action": "back"}
    
    destinations = controller.get_available_destinations()
    
    if not destinations:
        st.warning("No destinations available with remaining time!")
        return result
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Group by continent
    by_continent: Dict[str, List[Location]] = {}
    for loc in destinations:
        if loc.continent not in by_continent:
            by_continent[loc.continent] = []
        by_continent[loc.continent].append(loc)
    
    for continent, locs in sorted(by_continent.items()):
        with st.expander(f"🌍 {continent} ({len(locs)} destinations)"):
            for loc in locs[:10]:  # Limit per continent
                travel_time = current_location.get_travel_time_to(loc)
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{loc.city}**, {loc.country}")
                
                with col2:
                    st.markdown(f"⏱️ {travel_time} hrs")
                
                with col3:
                    if st.button("Go", key=f"travel_{loc.id}"):
                        result = {"action": "travel_to", "destination_id": loc.id}
    
    return result


def render_arrest(controller: GameController, suspects: List[Suspect]) -> Optional[str]:
    """Render arrest screen."""
    st.markdown("### 🚨 Issue Arrest Warrant")
    st.markdown("Select the suspect you believe committed the crime:")
    
    for suspect in suspects:
        with st.expander(f"🕵️ {suspect.name}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                render_art_placeholder("Suspect", suspect.name, 120, 160)
            
            with col2:
                st.markdown(f"""
                - **Hair:** {suspect.hair_color}
                - **Eyes:** {suspect.eye_color}
                - **Hobby:** {suspect.hobby}
                - **Vehicle:** {suspect.vehicle}
                - **Favorite Food:** {suspect.favorite_food}
                """)
            
            if st.button(f"🚨 ARREST {suspect.name.upper()}", key=f"arrest_{suspect.id}"):
                return suspect.id
    
    return None


def render_case_result(won: bool, case: Case, player: Player, score: int, message: str) -> Dict:
    """Render case result screen."""
    result = {"action": None}
    
    if won:
        st.balloons()
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <h1 style="color: #4CAF50;">🎉 CASE SOLVED! 🎉</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <h1 style="color: #F44336;">❌ CASE FAILED ❌</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #D4B896; padding: 20px; border-radius: 8px; text-align: center; margin: 20px auto; max-width: 500px;">
        <div style="color: #2A1810; font-size: 18px; margin-bottom: 15px;">{message}</div>
        <div style="color: #3D2817; font-size: 24px; font-weight: bold;">Score: {score:,}</div>
        <div style="color: #555; margin-top: 10px;">Rank: {player.rank}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 MAIN MENU", use_container_width=True):
            result = {"action": "main_menu"}
    
    with col2:
        if st.button("🔍 NEW CASE", use_container_width=True):
            result = {"action": "new_case"}
    
    return result


# =============================================================================
# MAIN APP
# =============================================================================

def init_session_state():
    """Initialize session state."""
    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState.MAIN_MENU
    
    if "controller" not in st.session_state:
        st.session_state.controller = GameController()
    
    if "case_result" not in st.session_state:
        st.session_state.case_result = None


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Where is Snowflake Boseman Montana?",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    apply_theme()
    
    # Show title immediately so user knows app is loading
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #C4A35A;">🔍 Where in the World is Snowflake Boseman Montana? 🔍</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Test database connection first
    try:
        session = get_snowflake_session()
        st.success("✅ Connected to Snowflake!")
    except Exception as e:
        st.error(f"❌ Failed to connect to Snowflake: {e}")
        st.exception(e)
        st.stop()
    
    init_session_state()
    
    controller: GameController = st.session_state.controller
    
    # Get player
    try:
        player = controller.get_or_create_player()
        st.success(f"✅ Welcome, {player.display_name}!")
    except Exception as e:
        st.error(f"Error creating player: {e}")
        st.exception(e)
        st.info("Make sure the database tables are created. Run deploy_standard.sql and seed_data.sql first.")
        st.stop()
    
    # Route based on game state
    state = st.session_state.game_state
    
    if state == GameState.MAIN_MENU:
        has_case = controller.get_current_case() is not None
        result = render_main_menu(player, has_case)
        
        if result["action"] == "new_case":
            controller.start_new_case(result.get("difficulty", 1))
            st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
        elif result["action"] == "continue":
            st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
    
    elif state == GameState.INVESTIGATION:
        case = controller.get_current_case()
        location = controller.get_current_location()
        
        if not case or not location:
            st.session_state.game_state = GameState.MAIN_MENU
            st.rerun()
            return
        
        result = render_investigation(controller, case, location, player)
        
        if result["action"] == "investigate":
            clues = controller.investigate()
            if clues:
                st.success(f"Found {len(clues)} clue(s)!")
            if controller.get_time_remaining() <= 0:
                st.session_state.case_result = {
                    "won": False,
                    "message": "Time ran out!",
                    "score": 0,
                }
                st.session_state.game_state = GameState.CASE_RESULT
            st.rerun()
        
        elif result["action"] == "travel":
            st.session_state.game_state = GameState.TRAVEL
            st.rerun()
        
        elif result["action"] == "arrest":
            st.session_state.game_state = GameState.ARREST
            st.rerun()
        
        elif result["action"] == "main_menu":
            st.session_state.game_state = GameState.MAIN_MENU
            st.rerun()
    
    elif state == GameState.TRAVEL:
        case = controller.get_current_case()
        location = controller.get_current_location()
        
        if not case or not location:
            st.session_state.game_state = GameState.MAIN_MENU
            st.rerun()
            return
        
        result = render_travel(controller, case, location)
        
        if result["action"] == "back":
            st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
        
        elif result["action"] == "travel_to":
            travel_result = controller.travel_to(result["destination_id"])
            
            if travel_result.get("game_over"):
                st.session_state.case_result = {
                    "won": False,
                    "message": travel_result.get("message", "Game over!"),
                    "score": 0,
                }
                st.session_state.game_state = GameState.CASE_RESULT
            else:
                st.success(travel_result.get("message", "Traveled!"))
                if travel_result.get("arrived_at_suspect"):
                    st.info("🎯 The suspect is here!")
                st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
    
    elif state == GameState.ARREST:
        case = controller.get_current_case()
        
        if not case:
            st.session_state.game_state = GameState.MAIN_MENU
            st.rerun()
            return
        
        if st.button("← Back to Investigation"):
            st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
            return
        
        suspects = controller.get_all_suspects()
        selected = render_arrest(controller, suspects)
        
        if selected:
            arrest_result = controller.attempt_arrest(selected)
            st.session_state.case_result = {
                "won": arrest_result.get("won", False),
                "message": arrest_result.get("message", ""),
                "score": arrest_result.get("score", 0),
            }
            
            if arrest_result.get("game_over", True):
                st.session_state.game_state = GameState.CASE_RESULT
            st.rerun()
    
    elif state == GameState.CASE_RESULT:
        case_result = st.session_state.case_result or {}
        case = controller.get_current_case()
        
        # Create dummy case if needed
        if not case:
            case = Case(
                id="done",
                player_id=player.id,
                suspect=Suspect(
                    id="unknown", name="Unknown", hair_color="", eye_color="",
                    hobby="", vehicle="", favorite_food=""
                ),
                stolen_item="",
                difficulty=1,
                location_path=[],
            )
        
        player = controller.get_or_create_player()
        
        result = render_case_result(
            won=case_result.get("won", False),
            case=case,
            player=player,
            score=case_result.get("score", 0),
            message=case_result.get("message", ""),
        )
        
        if result["action"] in ("main_menu", "new_case"):
            st.session_state.case_result = None
            st.session_state.controller = GameController()  # Reset controller
            st.session_state.game_state = GameState.MAIN_MENU
            st.rerun()


if __name__ == "__main__":
    main()
