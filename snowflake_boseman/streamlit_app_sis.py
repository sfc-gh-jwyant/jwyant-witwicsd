"""
WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?

A geography mystery adventure game inspired by Carmen Sandiego.
Built with Streamlit in Snowflake.

SINGLE FILE VERSION FOR STREAMLIT IN SNOWFLAKE
(SiS doesn't support relative imports or package structures)
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
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
TABLE_PREFIX = "TEMP.JWYANT."  # e.g., "DEMO_WITWISBM.GAME." or ""

# Stage for media files (city images, landmarks, etc.)
# Images are in the media/ folder, named like "loc_paris.jpg" or "loc_paris.png"
# Full path format: @"DATABASE"."SCHEMA"."STAGE_NAME"/folder/file.ext
MEDIA_STAGE = '@"TEMP"."JWYANT"."DEMO_WITWISBM"/media'  # Stage path including media/ folder

# Available AI models for Snowflake Cortex AI_COMPLETE
# See: https://docs.snowflake.com/en/sql-reference/functions/ai_complete-single-string#arguments
AVAILABLE_AI_MODELS = [
    "llama3.1-70b",      # Default
    "llama3.1-8b",
    "llama3.1-405b",
    "llama3.3-70b",
    "llama3-8b",
    "llama3-70b",
    "llama4-maverick",
    "llama4-scout",
    "claude-4-opus",
    "claude-4-sonnet",
    "claude-3-7-sonnet",
    "claude-3-5-sonnet",
    "deepseek-r1",
    "mistral-large",
    "mistral-large2",
    "mistral-7b",
    "mixtral-8x7b",
    "openai-gpt-4.1",
    "openai-o4-mini",
    "snowflake-arctic",
    "snowflake-llama-3.1-405b",
    "snowflake-llama-3.3-70b",
]
DEFAULT_AI_MODEL = "llama3.1-70b"

# Difficulty config loaded from database - see get_difficulty_config()
# Fallback values used if database is unavailable
DIFFICULTY_CONFIG_FALLBACK = {
    1: {"name": "XS Warehouse", "description": "Extra Small challenge - clues served instantly", "time_budget": 144, "clue_clarity": "obvious", "min_locations": 3, "max_locations": 4, "red_herrings": 0, "decoy_destinations": 2},
    2: {"name": "Query Queued", "description": "Your investigation has been queued behind 3 others", "time_budget": 144, "clue_clarity": "clear", "min_locations": 4, "max_locations": 5, "red_herrings": 1, "decoy_destinations": 4},
    3: {"name": "Schema Drift", "description": "The clues keep changing when you're not looking", "time_budget": 144, "clue_clarity": "cryptic", "min_locations": 5, "max_locations": 7, "red_herrings": 2, "decoy_destinations": 6},
    4: {"name": "Cortex Hallucinating", "description": "The AI is confident but probably wrong", "time_budget": 144, "clue_clarity": "very_cryptic", "min_locations": 7, "max_locations": 9, "red_herrings": 3, "decoy_destinations": 8},
    5: {"name": "DROP PRODUCTION CASCADE", "description": "Everything is on fire. Good luck.", "time_budget": 144, "clue_clarity": "riddle", "min_locations": 9, "max_locations": 12, "red_herrings": 4, "decoy_destinations": 10},
}

INVESTIGATION_TIME = 5  # Hours per investigation (like original Carmen Sandiego)

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
    clue_type: str  # "destination", "suspect", "red_herring", "confusion"
    text: str
    location_city: str = ""  # City where clue was gathered
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
    ai_prompt_count: int = 0
    ai_token_count: int = 0  # Total tokens used across all prompts
    ai_credits_used: float = 0.0  # Total Snowflake credits used for AI
    
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
            ai_prompt_count=data.get("AI_PROMPT_COUNT", data.get("ai_prompt_count", 0)),
            ai_token_count=data.get("AI_TOKEN_COUNT", data.get("ai_token_count", 0)),
            ai_credits_used=float(data.get("AI_CREDITS_USED", data.get("ai_credits_used", 0.0))),
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
    ai_prompts: int = 0  # Number of AI prompts used in this case
    ai_tokens: int = 0   # Total tokens used in this case
    ai_credits: float = 0.0  # Credits used in this case
    ai_model: str = ""   # Model used for this case


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
        config = get_difficulty_config()
        self.total_hours = config[difficulty]["time_budget"]
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


@st.cache_data(ttl=60)  # Cache for 1 hour
def get_difficulty_config() -> Dict[int, Dict]:
    """Load difficulty configuration from the database."""
    try:
        rows = execute_query(f"""
            SELECT difficulty_id, name, description, time_budget_hours, 
                   clue_clarity, min_locations, max_locations, 
                   red_herrings, decoy_destinations
            FROM {TABLE_PREFIX}difficulty_levels
            ORDER BY difficulty_id
        """)
        
        if not rows:
            return DIFFICULTY_CONFIG_FALLBACK
        
        config = {}
        for row in rows:
            config[row["DIFFICULTY_ID"]] = {
                "name": row["NAME"],
                "description": row["DESCRIPTION"],
                "time_budget": row["TIME_BUDGET_HOURS"],
                "clue_clarity": row["CLUE_CLARITY"],
                "min_locations": row["MIN_LOCATIONS"],
                "max_locations": row["MAX_LOCATIONS"],
                "red_herrings": row["RED_HERRINGS"],
                "decoy_destinations": row["DECOY_DESTINATIONS"],
            }
        return config
    except Exception as e:
        print(f"Error loading difficulty config: {e}")
        return DIFFICULTY_CONFIG_FALLBACK


def get_current_user() -> Dict[str, str]:
    """Get current Snowflake user info."""
    try:
        # In Streamlit in Snowflake, try to get the actual logged-in user
        # st.user contains the SSO/login identity
        if hasattr(st, 'user') and st.user:
            user_info = st.user
            # user_info may have 'email' or 'user_name' depending on auth setup
            username = user_info.get('email') or user_info.get('user_name') or user_info.get('name', '')
            if username:
                return {"username": username, "role": "USER"}
        
        # Fallback: Try CURRENT_USER() but it may return service account in SiS
        session = get_snowflake_session()
        result = session.sql("""
            SELECT CURRENT_USER() as username, 
                   CURRENT_ROLE() as role
        """).collect()[0]
        
        username = result["USERNAME"]
        
        # Check if it looks like a service account (contains random numbers)
        # If so, try to get a better name
        if username and len(username) > 20 and username.upper().startswith("STPLAT"):
            # This is a Streamlit platform service account, use a friendlier name
            # Try to get email from session context
            try:
                email_result = session.sql("SELECT SYSTEM$GET_SNOWFLAKE_PLATFORM_INFO() as info").collect()
                # Parse if available, otherwise fall back
            except:
                pass
            return {"username": "Detective", "role": result["ROLE"]}
        
        return {"username": username, "role": result["ROLE"]}
    except Exception as e:
        return {"username": "Detective", "role": "PUBLIC"}


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
                INSERT INTO {TABLE_PREFIX}players (player_id, snowflake_user, rank, cases_solved, total_score, ai_prompt_count)
                VALUES ('{player_id}', '{player_id}', 'Rookie', 0, 0, 0)
            """)
            self._current_player = Player(
                id=player_id,
                snowflake_user=player_id,
                rank="Rookie",
                cases_solved=0,
                total_score=0,
                ai_prompt_count=0,
            )
        
        return self._current_player
    
    def _get_stolen_items(self) -> List[str]:
        """Get stolen items from database."""
        try:
            rows = execute_query(f"SELECT item_name FROM {TABLE_PREFIX}stolen_items ORDER BY RANDOM()")
            return [r.get("ITEM_NAME", r.get("item_name", "")) for r in rows if r.get("ITEM_NAME") or r.get("item_name")]
        except Exception as e:
            print(f"Error loading stolen items: {e}")
            return []
    
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
        diff_config = get_difficulty_config()
        config = diff_config[difficulty]
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
        
        # Load stolen items from database
        stolen_items = self._get_stolen_items()
        if not stolen_items:
            # Fallback if table doesn't exist
            stolen_items = ["the Data Cloud", "a Virtual Warehouse", "the Snowflake source code"]
        
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
    
    def get_travel_options(self) -> List[Location]:
        """Get limited travel options: previous city first, then correct destination + decoys."""
        case = self.get_current_case()
        current = self.get_current_location()
        if not case or not current:
            return []
        
        # Get the correct next location
        next_location_id = case.get_suspect_next_location()
        next_location = self.get_location_by_id(next_location_id) if next_location_id else None
        
        # Get all available destinations
        all_available = self.get_available_destinations()
        
        # Determine number of decoys based on difficulty
        diff_config = get_difficulty_config()
        config = diff_config.get(case.difficulty, diff_config[3])
        num_decoys = config.get("decoy_destinations", 5)
        
        # Find the previous city (second to last in visited list)
        visited = case.progress.locations_visited if case.progress else []
        previous_location = None
        if len(visited) >= 2:
            prev_id = visited[-2]  # Second to last is where we came from
            previous_location = self.get_location_by_id(prev_id)
        
        # Build options list (excluding previous city, we'll add it first later)
        options = []
        excluded_ids = {current.id}  # Don't include current location
        if previous_location:
            excluded_ids.add(previous_location.id)  # Will add separately as first option
        
        # Always include the correct destination if it exists and is reachable
        if next_location and next_location.id not in excluded_ids:
            if next_location in all_available:
                options.append(next_location)
                excluded_ids.add(next_location.id)
        
        # Filter available destinations
        decoy_pool = [loc for loc in all_available if loc.id not in excluded_ids]
        
        # Add random decoy destinations
        decoys = random.sample(decoy_pool, min(num_decoys, len(decoy_pool)))
        options.extend(decoys)
        
        # Shuffle the options (correct + decoys)
        random.shuffle(options)
        
        # Always add previous city as FIRST option (if we have one and can travel there)
        if previous_location and previous_location in all_available:
            options.insert(0, previous_location)
        
        return options
    
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
            self._save_case_analytics(case, "lost_time")
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
        
        # Check if player is on the correct path
        is_on_path = current.id in case.location_path
        
        if is_on_path:
            # Generate real clues - player is on the right track
            next_location_id = case.get_suspect_next_location()
            next_location = self.get_location_by_id(next_location_id) if next_location_id else None
            clues = self._generate_clues(case, current, next_location)
        else:
            # Generate confusion statements - player is at the wrong city
            clues = self._generate_confusion_statements(case, current)
        
        case.progress.clues_gathered.extend(clues)
        
        return clues
    
    def _generate_confusion_statements(self, case: Case, current: Location) -> List[Clue]:
        """Generate confusion statements when player is at the wrong location."""
        statements = []
        
        # Generate 1-2 confusion statements
        num_statements = random.randint(1, 2)
        
        for i in range(num_statements):
            statement = self._generate_confusion_with_ai(case.suspect, current)
            statements.append(statement)
        
        return statements
    
    def _generate_confusion_with_ai(self, suspect: Suspect, current: Location) -> Clue:
        """Generate a confusion statement using Cortex AI."""
        prompt = f"""You are a local witness in {current.city}, {current.country} for a detective game.
The detective is looking for a suspect, but the suspect was NEVER HERE - the detective is in the wrong city!

Generate a confused or unhelpful witness statement indicating you haven't seen anyone matching the description.

Examples of what to say:
- "I haven't seen anyone suspicious around here."
- "No one like that has come through town recently."
- "Are you sure you're in the right place? It's been quiet here."
- "I've been here all day and haven't noticed anyone unusual."
- "Maybe try asking in another city?"

RULES:
- Indicate you haven't seen the suspect
- Be polite but unhelpful
- Maybe suggest they're in the wrong place
- Keep it safe for work
- 1 sentence only

Generate ONLY the witness quote, nothing else."""

        statement_text = self._call_ai_complete(prompt)
        
        # Fallback statements if AI fails
        fallback_statements = [
            "I haven't seen anyone matching that description around here.",
            "No suspicious characters have come through lately. Are you sure you're in the right city?",
            "It's been pretty quiet here. Maybe try somewhere else?",
            "Sorry, I can't help you. No one like that has been here.",
            "I've been watching the streets all day - no one unusual passed by.",
        ]
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type="confusion",
            text=statement_text or random.choice(fallback_statements),
            location_city=current.city,
            source="confused local",
        )
    
    def _generate_clues(self, case: Case, current: Location, next_loc: Optional[Location]) -> List[Clue]:
        """Generate clues for investigation using Cortex AI."""
        clues = []
        difficulty = case.difficulty
        diff_config = get_difficulty_config()
        config = diff_config[difficulty]
        city_name = current.city
        
        # Generate destination + suspect clues in one AI call
        if next_loc:
            combined_clues = self._generate_combined_clues_with_ai(
                next_loc, case.suspect, difficulty, city_name
            )
            clues.extend(combined_clues)
        else:
            # No next location (end of path) - just generate suspect clue
            suspect_clue = self._generate_suspect_clue_with_ai(case.suspect, difficulty, city_name)
            clues.append(suspect_clue)
        
        # Add red herrings based on difficulty
        num_red_herrings = config.get("red_herrings", 0)
        if num_red_herrings > 0 and random.random() < 0.5:  # 50% chance per investigation
            red_herring = self._generate_red_herring_with_ai(difficulty, city_name)
            clues.append(red_herring)
        
        return clues
    
    def _generate_combined_clues_with_ai(self, next_loc: Location, suspect: Suspect, difficulty: int, city_name: str) -> List[Clue]:
        """Generate a single witness quote with both destination and suspect info."""
        # Check if there are multiple cities in this country
        all_locs = self.get_all_locations()
        cities_in_country = [l for l in all_locs if l.country == next_loc.country]
        multiple_cities = len(cities_in_country) > 1
        
        difficulty_desc = {
            1: "very obvious and easy to understand",
            2: "clear but not too direct",
            3: "somewhat cryptic, requiring some thought",
            4: "cryptic and puzzle-like",
            5: "extremely cryptic, like a riddle"
        }
        
        # Country naming rule
        if difficulty <= 2 and multiple_cities:
            country_rule = f"You may mention the country ({next_loc.country}) but NEVER mention the city name."
        else:
            country_rule = "Do NOT mention the country or city name directly."
        
        # Pick a random suspect attribute to hint at
        attributes = [
            f"hair color: {suspect.hair_color}",
            f"hobby: {suspect.hobby}",
            f"vehicle: {suspect.vehicle}",
            f"favorite food: {suspect.favorite_food}",
        ]
        if suspect.distinguishing_feature:
            attributes.append(f"distinguishing feature: {suspect.distinguishing_feature}")
        chosen_attr = random.choice(attributes)
        
        prompt = f"""You are a witness in a family-friendly geography detective game like Carmen Sandiego.
Generate a SINGLE witness quote that naturally combines:
1. A hint about where the suspect is heading
2. A description of what the suspect looked like

EXAMPLE: "I saw someone with red hair asking about the City of Lights."

DESTINATION INFO:
- The suspect is heading to: {next_loc.city}, {next_loc.country} (in {next_loc.continent})
- {country_rule}
- Reference landmarks, culture, geography, climate, famous nicknames, or notable features
- NEVER mention the city name "{next_loc.city}" directly

SUSPECT INFO:
- The suspect has: {chosen_attr}

DIFFICULTY: {difficulty}/5 - Make the clue {difficulty_desc.get(difficulty, 'clear')}

RULES:
- Write ONE natural witness quote (1-3 sentences)
- Combine destination hints AND suspect description naturally
- Keep it safe for work and family-friendly
- Do NOT name the suspect or city directly
- Write ONLY the quote, nothing else"""

        response = self._call_ai_complete(prompt)
        
        # Fallback if AI fails
        if not response:
            attr_value = chosen_attr.split(': ')[1]
            response = f"I saw someone with {attr_value} asking about traveling to {next_loc.continent}."
        
        # Return as a single clue
        return [Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type="witness",
            text=response,
            location_city=city_name,
            source="witness",
        )]
    
    def _generate_destination_clue_with_ai(self, next_loc: Location, difficulty: int, city_name: str) -> Clue:
        """Generate a destination clue using Cortex AI."""
        # Check if there are multiple cities in this country
        all_locs = self.get_all_locations()
        cities_in_country = [l for l in all_locs if l.country == next_loc.country]
        multiple_cities = len(cities_in_country) > 1
        
        # Build difficulty-aware prompt
        difficulty_desc = {
            1: "very obvious and easy to understand",
            2: "clear but not too direct",
            3: "somewhat cryptic, requiring some thought",
            4: "cryptic and puzzle-like",
            5: "extremely cryptic, like a riddle"
        }
        
        # Country naming rule
        if difficulty <= 2 and multiple_cities:
            country_rule = f"You may mention the country ({next_loc.country}) but NEVER mention the city name."
        else:
            country_rule = "Do NOT mention the country or city name directly."
        
        prompt = f"""You are a witness in a family-friendly geography detective game like Carmen Sandiego.
Generate a {difficulty_desc.get(difficulty, 'clear')} clue that hints at a destination.

The suspect is heading to: {next_loc.city}, {next_loc.country} (in {next_loc.continent})

RULES:
- NEVER mention the city name "{next_loc.city}" directly
- {country_rule}
- Reference landmarks, culture, geography, climate, or famous features of this place
- Keep it safe for work and appropriate for all ages
- Write as a witness quote, 2-3 sentences max
- Difficulty level: {difficulty}/5

Generate ONLY the witness quote, nothing else."""

        clue_text = self._call_ai_complete(prompt)
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type="destination",
            text=clue_text or f"I heard them mention something about {next_loc.continent}...",
            location_city=city_name,
            source="witness",
        )
    
    def _generate_suspect_clue_with_ai(self, suspect: Suspect, difficulty: int, city_name: str) -> Clue:
        """Generate a suspect clue using Cortex AI."""
        difficulty_desc = {
            1: "very obvious",
            2: "clear",
            3: "somewhat vague",
            4: "cryptic",
            5: "extremely cryptic"
        }
        
        # Pick a random attribute to hint at
        attributes = [
            f"hair color: {suspect.hair_color}",
            f"hobby: {suspect.hobby}",
            f"vehicle: {suspect.vehicle}",
            f"favorite food: {suspect.favorite_food}",
        ]
        if suspect.distinguishing_feature:
            attributes.append(f"distinguishing feature: {suspect.distinguishing_feature}")
        
        chosen_attr = random.choice(attributes)
        
        prompt = f"""You are a witness in a family-friendly detective game.
Generate a {difficulty_desc.get(difficulty, 'clear')} clue about a suspect you saw.

The suspect has this attribute: {chosen_attr}

RULES:
- Write as a witness observation, 1 sentence
- At difficulty 1-2, be direct about what you saw
- At difficulty 3-4, be vague or use metaphors
- At difficulty 5, use riddles
- Keep it safe for work
- Do NOT name the suspect directly

Generate ONLY the witness quote, nothing else."""

        clue_text = self._call_ai_complete(prompt)
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type="suspect",
            text=clue_text or f"I noticed something about them... {chosen_attr.split(': ')[1]}",
            location_city=city_name,
            source="witness",
        )
    
    def _generate_red_herring_with_ai(self, difficulty: int, city_name: str) -> Clue:
        """Generate a misleading red herring clue using Cortex AI."""
        # Pick a random wrong location
        all_locs = self.get_all_locations()
        wrong_loc = random.choice(all_locs)
        
        prompt = f"""You are a confused or mistaken witness in a detective game.
Generate a misleading clue that points to THE WRONG destination.

Hint at: {wrong_loc.city}, {wrong_loc.country} (but this is WRONG information)

RULES:
- This is a RED HERRING - intentionally misleading
- Make it sound believable but it's false information
- Do NOT mention the city name directly
- You can vaguely reference the region or landmarks
- Keep it safe for work
- Write as 1 confused witness quote

Generate ONLY the witness quote, nothing else."""

        clue_text = self._call_ai_complete(prompt)
        
        return Clue(
            id=f"clue_{uuid.uuid4().hex[:8]}",
            clue_type="red_herring",
            text=clue_text or "I think I saw them heading... somewhere with old buildings?",
            location_city=city_name,
            source="confused witness",
        )
    
    def _call_ai_complete(self, prompt: str) -> Optional[str]:
        """Call Snowflake Cortex AI_COMPLETE function with token counting."""
        try:
            session = get_snowflake_session()
            # Escape single quotes in prompt
            safe_prompt = prompt.replace("'", "''")
            
            # Get selected model from session state
            model = st.session_state.get("ai_model", DEFAULT_AI_MODEL)
            
            # Use a compatible model name for token counting (some models may not be supported)
            token_count_model = model if model in [
                "llama3-70b", "llama3-8b", "llama3.1-405b", "llama3.1-70b", "llama3.1-8b",
                "llama3.3-70b", "llama4-maverick", "llama4-scout", "mistral-7b", 
                "mistral-large", "mistral-large2", "mixtral-8x7b", "deepseek-r1",
                "snowflake-arctic", "snowflake-llama-3.1-405b", "snowflake-llama-3.3-70b"
            ] else "llama3.1-70b"  # Default to a supported model for counting
            
            # Step 1: Get the AI response
            response = None
            result = session.sql(f"""
                SELECT AI_COMPLETE(
                    model => '{model}',
                    prompt => '{safe_prompt}',
                    model_parameters => {{'guardrails': TRUE, 'max_tokens': 150, 'temperature': 0.7}}
                ) as response
            """).collect()
            
            if result and len(result) > 0:
                response = result[0]['RESPONSE']
                if response:
                    response = response.strip().strip('"').strip("'")
            
            # Step 2: Count tokens and calculate credits in a single SQL query
            # Join with cortex_credit_rates to get cost per million tokens
            input_tokens = 0
            output_tokens = 0
            credits_used = 0.0
            if response:
                safe_response = response.replace("'", "''")
                try:
                    token_result = session.sql(f"""
                        SELECT 
                            SNOWFLAKE.CORTEX.COUNT_TOKENS('{token_count_model}', '{safe_prompt}') as prompt_tokens,
                            SNOWFLAKE.CORTEX.COUNT_TOKENS('{token_count_model}', '{safe_response}') as response_tokens,
                            COALESCE(cr.credits_per_million_input_tokens, 0.36) as input_rate,
                            COALESCE(cr.credits_per_million_output_tokens, 0.36) as output_rate
                        FROM (SELECT 1) dummy
                        LEFT JOIN {TABLE_PREFIX}cortex_credit_rates cr ON cr.model_name = '{model}'
                    """).collect()
                    if token_result and len(token_result) > 0:
                        input_tokens = token_result[0]['PROMPT_TOKENS'] or 0
                        output_tokens = token_result[0]['RESPONSE_TOKENS'] or 0
                        input_rate = float(token_result[0]['INPUT_RATE'] or 0.36)
                        output_rate = float(token_result[0]['OUTPUT_RATE'] or 0.36)
                        # Calculate credits: (tokens / 1,000,000) * rate
                        credits_used = (input_tokens / 1_000_000 * input_rate) + (output_tokens / 1_000_000 * output_rate)
                except Exception:
                    # Fallback to rough estimates
                    input_tokens = len(prompt) // 4
                    output_tokens = len(response) // 4
                    # Use default llama3.1-70b rate (0.36) as fallback
                    credits_used = (input_tokens + output_tokens) / 1_000_000 * 0.36
            
            total_tokens = input_tokens + output_tokens
            
            # Update player's total token, prompt, and credit counts
            if self._current_player:
                self._current_player.ai_prompt_count += 1
                self._current_player.ai_token_count += total_tokens
                self._current_player.ai_credits_used += credits_used
                execute_write(f"""
                    UPDATE {TABLE_PREFIX}players 
                    SET ai_prompt_count = ai_prompt_count + 1,
                        ai_token_count = ai_token_count + {total_tokens},
                        ai_credits_used = ai_credits_used + {credits_used}
                    WHERE player_id = '{self._current_player.id}'
                """)
            
            # Update case-level tracking
            if self._current_case and self._current_case.progress:
                self._current_case.progress.ai_prompts += 1
                self._current_case.progress.ai_tokens += total_tokens
                self._current_case.progress.ai_credits += credits_used
                self._current_case.progress.ai_model = model
            
            return response
        except Exception as e:
            # Log error but don't crash - return None to use fallback
            print(f"AI_COMPLETE error: {e}")
            return None
    
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
            # Lower score is better (like golf) - track best score
            if self._current_player.total_score == 0 or score < self._current_player.total_score:
                self._current_player.total_score = score
            self._current_player.update_rank()
            self._update_player_stats(self._current_player)
            
            # Save analytics and high score
            self._save_case_analytics(case, "won")
            self._save_high_score(case, score)
            
            return {
                "won": True,
                "message": f"You caught {case.suspect.name}! Case solved! Your score: {score:,} (lower is better, like golf!)",
                "score": score,
                "game_over": True,  # Case is complete, return to menu
            }
        elif not is_at_location:
            # Wrong location - game over
            case.status = CaseStatus.LOST_WRONG_ARREST
            self._save_case_analytics(case, "lost_wrong_arrest")
            return {
                "won": False,
                "message": f"The suspect isn't here! While you searched the wrong city, {case.suspect.name} escaped!",
                "game_over": True,
            }
        else:
            # Wrong suspect - game over
            case.status = CaseStatus.LOST_WRONG_ARREST
            self._save_case_analytics(case, "lost_wrong_arrest")
            return {
                "won": False,
                "message": f"Wrong suspect! While you arrested the wrong person, {case.suspect.name} got away!",
                "game_over": True,
            }
    
    def _calculate_score(self, case: Case) -> float:
        """Calculate score for completed case.
        
        Score is based on AI credits used - lower is better (like golf).
        Credits = tokens * rate per million tokens for the model used.
        """
        if case.progress:
            # Score is AI credits used (already calculated during gameplay)
            # Multiply by 1000000 to get a readable number, round to int
            return round(case.progress.ai_credits * 1000000)
        return 0
    
    def _update_player_stats(self, player: Player) -> bool:
        """Update player stats in the database."""
        try:
            execute_write(f"""
                UPDATE {TABLE_PREFIX}players 
                SET cases_solved = {player.cases_solved},
                    total_score = {player.total_score},
                    rank = '{player.rank}'
                WHERE player_id = '{player.id}'
            """)
            return True
        except Exception as e:
            print(f"Error updating player stats: {e}")
            return False
    
    def _save_case_analytics(self, case: Case, outcome: str) -> bool:
        """Save case analytics to database."""
        try:
            progress = case.progress
            diff_config = get_difficulty_config()
            time_budget = diff_config[case.difficulty]["time_budget"]
            time_used = time_budget - (self._time_manager.hours_remaining if self._time_manager else 0)
            
            execute_write(f"""
                INSERT INTO {TABLE_PREFIX}case_analytics (
                    case_id, player_id, difficulty, outcome,
                    total_locations_in_path, locations_visited,
                    correct_travels, wrong_travels, clues_gathered,
                    time_budget_hours, time_used_hours,
                    ai_prompts, ai_tokens, ai_credits, ai_model,
                    started_at, ended_at
                ) VALUES (
                    '{case.id}', '{case.player_id}', {case.difficulty}, '{outcome}',
                    {len(case.location_path)}, {len(progress.locations_visited) if progress else 0},
                    {progress.correct_travels if progress else 0}, {progress.wrong_travels if progress else 0},
                    {len(progress.clues_gathered) if progress else 0},
                    {time_budget}, {time_used},
                    {progress.ai_prompts if progress else 0}, {progress.ai_tokens if progress else 0},
                    {progress.ai_credits if progress else 0.0}, '{progress.ai_model if progress and progress.ai_model else "unknown"}',
                    CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
                )
            """)
            return True
        except Exception as e:
            print(f"Error saving case analytics: {e}")
            return False
    
    def _save_high_score(self, case: Case, score: int) -> bool:
        """Save high score to database."""
        try:
            progress = case.progress
            diff_config = get_difficulty_config()
            time_budget = diff_config[case.difficulty]["time_budget"]
            completion_time = time_budget - (self._time_manager.hours_remaining if self._time_manager else 0)
            
            score_id = f"score_{uuid.uuid4().hex[:12]}"
            execute_write(f"""
                INSERT INTO {TABLE_PREFIX}high_scores (
                    score_id, player_id, case_id, difficulty,
                    completion_time_hours, locations_visited, score
                ) VALUES (
                    '{score_id}', '{case.player_id}', '{case.id}', {case.difficulty},
                    {completion_time}, {len(progress.locations_visited) if progress else 0}, {score}
                )
            """)
            return True
        except Exception as e:
            print(f"Error updating player stats: {e}")
            return False
    
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
    """Apply Snowflake-branded CSS theme."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Snowflake brand colors */
    :root {
        --snowflake-blue: #29B5E8;
        --snowflake-dark: #11567F;
        --snowflake-navy: #0D1B2A;
        --snowflake-light: #E8F4F8;
        --snowflake-white: #FFFFFF;
        --snowflake-accent: #FF6B35;
        --snowflake-gray: #6B7280;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--snowflake-navy) 0%, #1a3a52 50%, var(--snowflake-dark) 100%);
    }
    
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 1400px;
    }
    
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.25rem !important;
    }
    
    /* Compact dividers */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--snowflake-blue) !important;
        font-weight: 600 !important;
        margin-bottom: 0.25rem !important;
    }
    
    h1 {
        font-size: 1.8rem !important;
        background: linear-gradient(90deg, var(--snowflake-blue), #56CCF2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-top: 0 !important;
    }
    
    h2 {
        font-size: 1.3rem !important;
    }
    
    h3, .stSubheader {
        font-size: 1.1rem !important;
    }
    
    h5 {
        font-size: 0.9rem !important;
        margin-top: 0.25rem !important;
    }
    
    p, div, span, label, li {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--snowflake-light) !important;
    }
    
    /* Primary buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--snowflake-blue) 0%, #1E88E5 100%);
        color: white !important;
        border: none;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(41, 181, 232, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #3BC5F8 0%, #29B5E8 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(41, 181, 232, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(41, 181, 232, 0.3);
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--snowflake-blue);
    }
    
    /* Metrics - compact */
    [data-testid="stMetricValue"] {
        color: var(--snowflake-blue) !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--snowflake-light) !important;
        font-size: 0.75rem !important;
    }
    
    [data-testid="stMetric"] {
        padding: 0.25rem !important;
    }
    
    /* Compact buttons */
    .stButton > button {
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
    }
    
    /* City images - fill space, min 720x480 */
    .stImage {
        margin-bottom: 0.25rem !important;
    }
    
    .stImage img {
        width: 100% !important;
        min-width: 720px !important;
        min-height: 480px !important;
        max-height: 600px !important;
        object-fit: cover;
    }
    
    /* Info boxes compact */
    .stAlert {
        padding: 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    .stAlert p {
        font-size: 0.85rem !important;
        margin: 0 !important;
    }
    
    /* Expanders compact */
    .streamlit-expanderHeader {
        padding: 0.25rem !important;
        font-size: 0.85rem !important;
    }
    
    /* Column gaps */
    [data-testid="column"] {
        padding: 0 0.25rem !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        background: rgba(41, 181, 232, 0.1);
        border: 1px solid rgba(41, 181, 232, 0.3);
        border-radius: 8px;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(41, 181, 232, 0.2) !important;
    }
    
    /* Captions */
    .stCaption, small {
        color: var(--snowflake-gray) !important;
    }
    
    /* Cards/containers */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(41, 181, 232, 0.2);
        border-radius: 8px;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(41, 181, 232, 0.3);
        border-radius: 8px;
        color: white;
    }
    
    /* Snowflake logo accent bar */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--snowflake-blue), #56CCF2, var(--snowflake-blue));
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)


def render_stage_image(location_id: str, alt_text: str, use_container_width: bool = True, width: int = None):
    """
    Render an image from the Snowflake stage.
    Images are stored as loc_[city].jpg or loc_[city].png in the media/ folder.
    
    In Streamlit in Snowflake, use st.image with the stage path.
    """
    # Try jpg, jpeg, and png extensions
    extensions = ["jpg", "jpeg", "png"]
    session = get_snowflake_session()
    
    for ext in extensions:
        try:
            # Construct the stage file path
            image_path = f"{MEDIA_STAGE}/{location_id}.{ext}"
            
            # Try to read the image from stage using GET
            try:
                result = session.file.get(image_path, "/tmp/")
                local_path = f"/tmp/{location_id}.{ext}"
                if width:
                    st.image(local_path, caption=alt_text, width=width)
                else:
                    st.image(local_path, caption=alt_text, use_container_width=use_container_width)
                return True
            except Exception:
                # Alternative: Try using the stage URL directly
                try:
                    if width:
                        st.image(image_path, caption=alt_text, width=width)
                    else:
                        st.image(image_path, caption=alt_text, use_container_width=use_container_width)
                    return True
                except:
                    pass
        except Exception:
            continue
    
    # Fallback to placeholder
    render_art_placeholder("Location", alt_text, width or 300, (width * 2 // 3) if width else 200)
    return False


def get_dynamic_city_description(controller: "GameController", location: Location) -> str:
    """
    Generate a dynamic, colorful city description using AI_COMPLETE.
    Caches the description in session state to avoid regenerating on every rerun.
    """
    cache_key = f"city_desc_{location.id}"
    
    # Check if we already have a cached description for this location
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Generate a new description using AI via controller's _call_ai_complete
    prompt = f"""You are a colorful, enthusiastic travel guide for a family-friendly geography game.
Write a 2-3 sentence welcome message for a detective arriving in {location.city}, {location.country}.

RULES:
- Be warm, friendly, and exciting - make the player feel like they're on an adventure!
- Mention 1-2 unique things about this city (landmarks, culture, food, climate, or fun facts)
- Keep it safe for work and appropriate for all ages
- Use vivid, descriptive language that paints a picture
- Do NOT mention any crimes, suspects, or detective work
- Write as if you're a friendly local greeting a visitor

Generate ONLY the welcome message, nothing else."""
    
    description = controller._call_ai_complete(prompt)
    
    if description:
        # Cache the description
        st.session_state[cache_key] = description
        return description
    
    # Fallback to static description or default
    if location.description:
        return location.description
    return f"Welcome to {location.city}, {location.country}! This fascinating city awaits your investigation."


def render_art_placeholder(art_type: str, alt_text: str, width: int = 200, height: int = 150):
    """Render a placeholder for missing art with Snowflake styling."""
    st.markdown(f"""
    <div style="
        width: {width}px;
        height: {height}px;
        background: linear-gradient(135deg, rgba(17, 86, 127, 0.5) 0%, rgba(13, 27, 42, 0.8) 100%);
        border: 2px dashed rgba(41, 181, 232, 0.5);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #29B5E8;
        font-family: 'Inter', -apple-system, sans-serif;
        border-radius: 12px;
        margin: 10px auto;
        box-shadow: 0 4px 20px rgba(41, 181, 232, 0.1);
    ">
        <span style="font-size: 2em;">🖼️</span>
        <span style="font-size: 0.8em; margin-top: 8px; font-weight: 600;">{art_type.upper()}</span>
        <span style="font-size: 0.7em; opacity: 0.7; color: #E8F4F8;">{alt_text}</span>
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
    
    # Simple header using native Streamlit
    st.title("🔍 Where in the World is Snowflake Boseman Montana? 🔍")
    st.subheader("A geography mystery adventure")
    
    # Splash image and rules side by side
    col_img, col_rules = st.columns([2, 1])
    
    with col_img:
        render_stage_image("main_splash", "Where in the World is Snowflake Boseman Montana?", width=720)
    
    with col_rules:
        st.markdown("### 📋 How to Play")
        st.markdown("""
        **The Case:** Snowflake Boseman Montana has stolen something valuable and fled! Track them across the globe before time runs out.
        
        **🔍 Investigate** - Question witnesses for clues about the suspect's next destination and appearance.
        
        **✈️ Travel** - Fly to cities based on clues. Each flight costs time based on distance.
        
        **🚨 Arrest** - When you've found the suspect, issue a warrant! But be sure—wrong arrests end your case.
        
        **⏱️ Time** - You have 144 hours (6 days). Investigations take 5 hours each.
        
        **🏆 Scoring** - Lower is better! Score = AI credits used. Be efficient with your investigations.
        """)
    
    st.divider()
    
    # Player info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Agent", player.display_name)
    with col2:
        st.metric("Rank", f"{player.rank_icon} {player.rank}")
    with col3:
        st.metric("Cases Solved", player.cases_solved)
    
    st.divider()
    
    # Continue button if there's an active case
    if has_active_case:
        st.warning("📋 You have a case in progress!")
        if st.button("▶️ CONTINUE INVESTIGATION", use_container_width=True, type="primary"):
            result = {"action": "continue"}
    
    st.subheader("🆕 Start New Case")
    
    col_diff, col_model = st.columns(2)
    
    with col_diff:
        # Difficulty selector
        diff_config = get_difficulty_config()
        difficulty = st.selectbox(
            "Select Difficulty",
            options=list(diff_config.keys()),
            format_func=lambda x: f"{diff_config[x]['name']} - {diff_config[x]['description']}",
        )
    
    with col_model:
        # AI Model selector
        ai_model = st.selectbox(
            "AI Model",
            options=AVAILABLE_AI_MODELS,
            index=AVAILABLE_AI_MODELS.index(st.session_state.ai_model),
            help="Snowflake Cortex AI model for generating clues"
        )
        # Update session state when model changes
        if ai_model != st.session_state.ai_model:
            st.session_state.ai_model = ai_model
    
    # Show difficulty details
    config = diff_config[difficulty]
    st.caption(f"⏱️ Time: {config['time_budget']} hours | 📍 Locations: {config['min_locations']}-{config['max_locations']} | 🔴 Red Herrings: {config['red_herrings']} | 🤖 Model: {ai_model}")
    
    if st.button("🔍 START NEW CASE", use_container_width=True, type="primary"):
        result = {"action": "new_case", "difficulty": difficulty}
    
    return result


def render_investigation(controller: GameController, case: Case, location: Location, player: Player) -> Dict:
    """Render investigation screen."""
    result = {"action": None}
    
    # Title and case header
    st.title(f"📍 {location.city}, {location.country}")
    
    # Compact header with case info and time
    diff_config = get_difficulty_config()
    urgency = controller.get_urgency_level()
    hours = controller.get_time_remaining()
    
    # Time display with urgency coloring
    if urgency == "critical":
        time_html = f'<span style="color: #ff4b4b; font-weight: bold;">⏱️ {hours} hours remaining!</span>'
    elif urgency == "warning":
        time_html = f'<span style="color: #ffa726; font-weight: bold;">⏱️ {hours} hours remaining</span>'
    else:
        time_html = f'<span style="color: #4caf50;">⏱️ {hours} hours remaining</span>'
    
    st.markdown(f"""
    **Case:** {case.stolen_item} stolen! | 
    **Difficulty:** {diff_config[case.difficulty]['name']} | 
    **Rank:** {player.rank} | 
    {time_html}
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader(f"🏙️ Welcome to {location.city}")
        
        # Display city image from stage
        if location.image_url:
            # If image_url is set, use it directly
            try:
                st.image(location.image_url, caption=f"{location.city}, {location.country}", use_container_width=True)
            except:
                render_stage_image(location.id, f"{location.city}, {location.country}")
        else:
            # Try to load from stage using location_id
            render_stage_image(location.id, f"{location.city}, {location.country}")
        
        # Generate dynamic city description with AI
        city_desc = get_dynamic_city_description(controller, location)
        st.markdown(f'<div style="padding: 1rem; margin-bottom: 1rem; background: rgba(41, 181, 232, 0.15); border: 1px solid rgba(41, 181, 232, 0.3); border-radius: 8px;"><p style="margin: 0; font-size: 0.9rem;">{city_desc.strip(chr(34) + chr(92))}</p></div>', unsafe_allow_html=True)
    
    with col_right:
        st.subheader("📔 Clue Notebook")
        
        clues = controller.get_gathered_clues()
        if clues:
            # Group clues by city
            clues_by_city = {}
            for clue in clues:
                city = clue.location_city or "Unknown"
                if city not in clues_by_city:
                    clues_by_city[city] = []
                clues_by_city[city].append(clue)
            
            # Display clues in a scrollable container (480px to match image height)
            clue_html = '<div style="min-height: 480px; max-height: 480px; overflow-y: auto; padding: 0.5rem; padding-bottom: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">'
            for city, city_clues in clues_by_city.items():
                clue_html += f'<p style="margin-bottom: 0.25rem;"><b>{city}:</b></p>'
                for clue in city_clues:
                    clean_text = clue.text.strip('"\\')
                    clue_html += f'<p style="font-size: 0.85rem; margin: 0.25rem 0; padding-left: 0.5rem; border-left: 2px solid #29B5E8;">"{clean_text}"</p>'
            clue_html += '</div>'
            st.markdown(clue_html, unsafe_allow_html=True)
        else:
            # Empty notebook placeholder with same height
            st.markdown('<div style="min-height: 480px; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;"><p style="color: #29B5E8;">No clues yet. Investigate to gather clues!</p></div>', unsafe_allow_html=True)
    
    st.divider()
    
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
    
    # Compact metrics bar - all in one row
    st.markdown("---")
    
    # Format values
    case_locs = len(case.progress.locations_visited) if case.progress else 0
    case_prompts = case.progress.ai_prompts if case.progress else 0
    case_tokens = case.progress.ai_tokens if case.progress else 0
    case_tok_str = f"{case_tokens // 1000}K" if case_tokens >= 1000 else str(case_tokens)
    case_credits = case.progress.ai_credits if case.progress else 0.0
    case_cred_str = f"{case_credits:.4f}" if case_credits < 1 else f"{case_credits:.2f}"
    
    player_tok = player.ai_token_count
    player_tok_str = f"{player_tok // 1000}K" if player_tok >= 1000 else str(player_tok)
    player_cred = player.ai_credits_used
    player_cred_str = f"{player_cred:.4f}" if player_cred < 1 else f"{player_cred:.2f}"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 0.5rem; background: rgba(41, 181, 232, 0.1); border-radius: 8px;">
        <div><b>📊 This Case:</b> 📍 {case_locs} locations | 🤖 {case_prompts} prompts | 🔢 {case_tok_str} tokens | 💰 {case_cred_str} credits</div>
        <div><b>🎮 Lifetime:</b> 🏆 {player.cases_solved} solved | ⭐ {player.total_score} pts | 🤖 {player.ai_prompt_count} prompts | 🔢 {player_tok_str} tokens | 💰 {player_cred_str} credits</div>
    </div>
    """, unsafe_allow_html=True)
    
    return result


def render_travel(controller: GameController, case: Case, current_location: Location) -> Dict:
    """Render travel screen with map and limited destination options."""
    result = {"action": None}
    
    st.title(f"✈️ Travel from {current_location.city}")
    st.caption(f"Current location: {current_location.city}, {current_location.country} ({current_location.continent})")
    
    col_back, col_time = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Investigation", use_container_width=True):
            return {"action": "back"}
    with col_time:
        st.metric("Time Remaining", f"{controller.get_time_remaining()} hrs")
    
    st.divider()
    
    # Get limited travel options (correct + decoys, randomized)
    destinations = controller.get_travel_options()
    
    if not destinations:
        st.warning("⚠️ No destinations available with remaining time!")
        return result
    
    # Create two columns: map on left, destinations on right
    col_map, col_list = st.columns([2, 1])
    
    with col_map:
        st.subheader("🗺️ Select a Destination")
        
        # Build map data with pydeck for labels
        
        # Current location data
        current_df = pd.DataFrame([{
            "name": f"📍 YOU ARE HERE",
            "city": current_location.city,
            "lat": current_location.latitude,
            "lon": current_location.longitude,
        }])
        
        # Destination data
        dest_df = pd.DataFrame([{
            "name": loc.city,
            "city": f"{loc.city}, {loc.country}",
            "lat": loc.latitude,
            "lon": loc.longitude,
            "id": loc.id,
            "travel_time": current_location.get_travel_time_to(loc),
        } for loc in destinations])
        
        # Build travel path lines from visited locations
        visited_ids = case.progress.locations_visited if case.progress else []
        path_data = []
        if len(visited_ids) > 1:
            for i in range(len(visited_ids) - 1):
                from_loc = controller.get_location_by_id(visited_ids[i])
                to_loc = controller.get_location_by_id(visited_ids[i + 1])
                if from_loc and to_loc:
                    path_data.append({
                        "from_lon": from_loc.longitude,
                        "from_lat": from_loc.latitude,
                        "to_lon": to_loc.longitude,
                        "to_lat": to_loc.latitude,
                        "from_city": from_loc.city,
                        "to_city": to_loc.city,
                    })
        
        # Visited cities markers (excluding current - already shown in red)
        visited_cities = []
        for loc_id in visited_ids[:-1]:  # All except current (last one)
            loc = controller.get_location_by_id(loc_id)
            if loc:
                visited_cities.append({
                    "name": f"✓ {loc.city}",
                    "city": loc.city,
                    "lat": loc.latitude,
                    "lon": loc.longitude,
                })
        visited_df = pd.DataFrame(visited_cities) if visited_cities else pd.DataFrame()
        
        # Calculate center point for initial view
        all_lats = [current_location.latitude] + [loc.latitude for loc in destinations]
        all_lons = [current_location.longitude] + [loc.longitude for loc in destinations]
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
        
        # Create pydeck layers
        layers = []
        
        # Travel path lines - orange/gold dashed effect
        if path_data:
            path_df = pd.DataFrame(path_data)
            path_layer = pdk.Layer(
                "LineLayer",
                data=path_df,
                get_source_position=["from_lon", "from_lat"],
                get_target_position=["to_lon", "to_lat"],
                get_color=[255, 193, 7, 200],  # Gold/amber
                get_width=3,
                pickable=False,
            )
            layers.append(path_layer)
        
        # Visited cities - smaller gray markers
        if not visited_df.empty:
            visited_layer = pdk.Layer(
                "ScatterplotLayer",
                data=visited_df,
                get_position=["lon", "lat"],
                get_radius=50000,
                get_fill_color=[158, 158, 158, 180],  # Gray
                pickable=False,
            )
            visited_text_layer = pdk.Layer(
                "TextLayer",
                data=visited_df,
                get_position=["lon", "lat"],
                get_text="name",
                get_size=10,
                get_color=[200, 200, 200],
                get_angle=0,
                get_text_anchor="'middle'",
                get_alignment_baseline="'bottom'",
                get_pixel_offset=[0, -10],
            )
            layers.extend([visited_layer, visited_text_layer])
        
        # Current location - red marker
        current_layer = pdk.Layer(
            "ScatterplotLayer",
            data=current_df,
            get_position=["lon", "lat"],
            get_radius=80000,
            get_fill_color=[255, 107, 107, 200],  # Red
            pickable=False,
        )
        layers.append(current_layer)
        
        # Current location label
        current_text_layer = pdk.Layer(
            "TextLayer",
            data=current_df,
            get_position=["lon", "lat"],
            get_text="name",
            get_size=14,
            get_color=[255, 255, 255],
            get_angle=0,
            get_text_anchor="'middle'",
            get_alignment_baseline="'bottom'",
            get_pixel_offset=[0, -15],
        )
        layers.append(current_text_layer)
        
        # Destination markers - teal
        dest_layer = pdk.Layer(
            "ScatterplotLayer",
            data=dest_df,
            get_position=["lon", "lat"],
            get_radius=60000,
            get_fill_color=[78, 205, 196, 200],  # Teal
            pickable=True,
            auto_highlight=True,
        )
        layers.append(dest_layer)
        
        # Destination labels
        dest_text_layer = pdk.Layer(
            "TextLayer",
            data=dest_df,
            get_position=["lon", "lat"],
            get_text="name",
            get_size=12,
            get_color=[255, 255, 255],
            get_angle=0,
            get_text_anchor="'middle'",
            get_alignment_baseline="'bottom'",
            get_pixel_offset=[0, -12],
        )
        layers.append(dest_text_layer)
        
        # Create the deck
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=1.5,
            pitch=0,
        )
        
        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style="dark",  # Built-in style: "dark", "light", "road", "satellite"
            tooltip={"text": "{city}\n⏱️ {travel_time} hrs"},
        )
        
        # Display the map
        st.pydeck_chart(deck)
        
        # Legend
        st.caption("🔴 Your location | ⚪ Visited | 🟡 Travel path | 🔵 Click a destination on the right")
    
    with col_list:
        st.subheader("✈️ Fly To:")
        
        # Determine if first destination is the previous city (go back option)
        visited = case.progress.locations_visited if case.progress else []
        previous_id = visited[-2] if len(visited) >= 2 else None
        
        # Show destination buttons as a selectable list
        for i, loc in enumerate(destinations):
            travel_time = current_location.get_travel_time_to(loc)
            
            # Check if this is the "go back" option (previous city)
            is_go_back = (loc.id == previous_id)
            
            if is_go_back:
                button_label = f"← GO BACK: {loc.city}, {loc.country}\n⏱️ {travel_time} hrs"
                button_help = f"Return to {loc.city} ({loc.continent})"
            else:
                button_label = f"✈️ {loc.city}, {loc.country}\n⏱️ {travel_time} hrs"
                button_help = f"Fly to {loc.city} ({loc.continent})"
            
            if st.button(
                button_label,
                key=f"travel_{loc.id}",
                use_container_width=True,
                help=button_help
            ):
                result = {"action": "travel_to", "destination_id": loc.id}
    
    return result


def render_suspect_mugshot(suspect_id: str, suspect_name: str):
    """Render suspect mugshot from stage - responsive sizing."""
    extensions = ["png", "jpeg", "jpg"]
    session = get_snowflake_session()
    
    for ext in extensions:
        try:
            image_path = f'{MEDIA_STAGE}/{suspect_id}.{ext}'
            try:
                result = session.file.get(image_path, "/tmp/")
                local_path = f"/tmp/{suspect_id}.{ext}"
                st.image(local_path, use_container_width=True)
                return True
            except:
                try:
                    st.image(image_path, use_container_width=True)
                    return True
                except:
                    pass
        except:
            continue
    
    # Fallback placeholder - responsive
    st.markdown(f"""
    <div style="width: 100%; aspect-ratio: 3/4; background: rgba(0,0,0,0.3); 
                border: 2px dashed #29B5E8; border-radius: 8px; 
                display: flex; align-items: center; justify-content: center;">
        <span style="color: #29B5E8;">🕵️ {suspect_name[:15]}</span>
    </div>
    """, unsafe_allow_html=True)
    return False


def render_arrest(controller: GameController, suspects: List[Suspect]) -> Optional[str]:
    """Render arrest screen with responsive mugshots layout."""
    st.markdown("### 🚨 Issue Arrest Warrant")
    st.markdown("Select the suspect you believe committed the crime:")
    
    # Display suspects in 2-column grid
    for i in range(0, len(suspects), 2):
        cols = st.columns(2, gap="medium")
        
        for j, col in enumerate(cols):
            if i + j < len(suspects):
                suspect = suspects[i + j]
                
                with col:
                    with st.container(border=True):
                        # Image on top
                        render_suspect_mugshot(suspect.id, suspect.name)
                        
                        # Name below image
                        st.markdown(f"**{suspect.name}**")
                        
                        # Details below name
                        st.markdown(f"🎨 Hair: {suspect.hair_color} · 👁️ Eyes: {suspect.eye_color}")
                        st.markdown(f"🎯 Hobby: {suspect.hobby}")
                        st.markdown(f"🚗 Vehicle: {suspect.vehicle}")
                        st.markdown(f"🍽️ Food: {suspect.favorite_food}")
                        st.markdown(f"✨ Feature: {suspect.distinguishing_feature}")
                        
                        # Arrest button at bottom
                        if st.button(f"🚨 ARREST", key=f"arrest_{suspect.id}", use_container_width=True):
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
    
    if "current_case" not in st.session_state:
        st.session_state.current_case = None
    
    if "time_manager" not in st.session_state:
        st.session_state.time_manager = None
    
    if "case_result" not in st.session_state:
        st.session_state.case_result = None
    
    if "ai_model" not in st.session_state:
        st.session_state.ai_model = DEFAULT_AI_MODEL
    
    # Restore case to controller from session state
    controller = st.session_state.controller
    if st.session_state.current_case and not controller._current_case:
        controller._current_case = st.session_state.current_case
        controller._time_manager = st.session_state.time_manager


def main():
    """Main application entry point."""
    try:
        st.set_page_config(
            page_title="Where is Snowflake Boseman Montana?",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except:
        pass  # Already set
    
    apply_theme()
    init_session_state()
    
    controller: GameController = st.session_state.controller
    
    # Get player
    try:
        player = controller.get_or_create_player()
    except Exception as e:
        st.error(f"❌ Error connecting to database: {e}")
        st.info("Make sure the database tables are created. Run deploy_standard.sql and seed_data.sql first.")
        st.exception(e)
        st.stop()
    
    # Route based on game state (compare by .value to avoid enum class mismatch on rerun)
    state = st.session_state.game_state
    state_value = state.value if hasattr(state, 'value') else state
    
    if state_value == GameState.MAIN_MENU.value:
        try:
            has_case = controller.get_current_case() is not None
            result = render_main_menu(player, has_case)
            
            if result["action"] == "new_case":
                try:
                    case = controller.start_new_case(result.get("difficulty", 1))
                    # Store in session state for persistence
                    st.session_state.current_case = case
                    st.session_state.time_manager = controller._time_manager
                    st.session_state.game_state = GameState.INVESTIGATION
                    st.rerun()
                except Exception as e:
                    st.error(f"Error starting new case: {e}")
                    st.exception(e)
            elif result["action"] == "continue":
                st.session_state.game_state = GameState.INVESTIGATION
                st.rerun()
        except Exception as e:
            st.error(f"Error in main menu: {e}")
            st.exception(e)
    
    elif state_value == GameState.INVESTIGATION.value:
        try:
            case = controller.get_current_case()
            location = controller.get_current_location()
            
            if not case or not location:
                st.warning("No active case found. Returning to main menu.")
                st.session_state.game_state = GameState.MAIN_MENU
                st.session_state.current_case = None
                st.session_state.time_manager = None
                st.rerun()
                return
            
            # Check if case is still active (not won/lost)
            if not case.is_active:
                st.warning("This case is already closed. Starting fresh...")
                st.session_state.game_state = GameState.MAIN_MENU
                st.session_state.current_case = None
                st.session_state.time_manager = None
                st.rerun()
                return
            
            # Check if time has run out
            if controller.get_time_remaining() <= 0:
                case.status = CaseStatus.LOST_TIME
                controller._save_case_analytics(case, "lost_time")
                st.session_state.case_result = {
                    "won": False,
                    "message": "Time ran out! The suspect escaped!",
                    "score": 0,
                }
                st.session_state.game_state = GameState.CASE_RESULT
                st.rerun()
                return
            
            result = render_investigation(controller, case, location, player)
        except Exception as e:
            st.error(f"Error in investigation: {e}")
            st.exception(e)
            if st.button("Return to Main Menu"):
                st.session_state.game_state = GameState.MAIN_MENU
                st.rerun()
            return
        
        if result["action"] == "investigate":
            clues = controller.investigate()
            # Update session state with modified case
            st.session_state.current_case = controller._current_case
            st.session_state.time_manager = controller._time_manager
            
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
    
    elif state_value == GameState.TRAVEL.value:
        case = controller.get_current_case()
        location = controller.get_current_location()
        
        if not case or not location or not case.is_active:
            st.session_state.game_state = GameState.MAIN_MENU
            st.session_state.current_case = None
            st.session_state.time_manager = None
            st.rerun()
            return
        
        result = render_travel(controller, case, location)
        
        if result["action"] == "back":
            st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
        
        elif result["action"] == "travel_to":
            travel_result = controller.travel_to(result["destination_id"])
            
            # Update session state with modified case
            st.session_state.current_case = controller._current_case
            st.session_state.time_manager = controller._time_manager
            
            if travel_result.get("game_over"):
                st.session_state.case_result = {
                    "won": False,
                    "message": travel_result.get("message", "Game over!"),
                    "score": 0,
                }
                st.session_state.game_state = GameState.CASE_RESULT
            else:
                st.session_state.game_state = GameState.INVESTIGATION
            st.rerun()
    
    elif state_value == GameState.ARREST.value:
        case = controller.get_current_case()
        
        if not case or not case.is_active:
            st.session_state.game_state = GameState.MAIN_MENU
            st.session_state.current_case = None
            st.session_state.time_manager = None
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
    
    elif state_value == GameState.CASE_RESULT.value:
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
            # Clear all case-related state when leaving a finished case
            st.session_state.case_result = None
            st.session_state.current_case = None
            st.session_state.time_manager = None
            st.session_state.controller = GameController()  # Reset controller
            st.session_state.game_state = GameState.MAIN_MENU
            st.rerun()


if __name__ == "__main__":
    main()
