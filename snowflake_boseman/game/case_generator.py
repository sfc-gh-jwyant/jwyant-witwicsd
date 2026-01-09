"""Case generation for new investigations."""

import random
import uuid
from typing import Optional

from ..models import Location, Suspect, Case, TimeManager, DIFFICULTY_CONFIG
from ..models.case import CaseProgress, CaseStatus, STOLEN_ITEMS
from ..database.connection import execute_query, execute_write


class CaseGenerator:
    """Generates new cases for players."""
    
    def __init__(self):
        """Initialize the case generator."""
        self._locations_cache: Optional[list[Location]] = None
        self._suspects_cache: Optional[list[Suspect]] = None
    
    def get_all_locations(self) -> list[Location]:
        """Load all locations from database."""
        if self._locations_cache is None:
            rows = execute_query("SELECT * FROM locations")
            self._locations_cache = [Location.from_dict(row) for row in rows]
            
            # Load landmarks for each location
            landmark_rows = execute_query("SELECT * FROM landmarks")
            from ..models.location import Landmark
            for loc in self._locations_cache:
                loc.landmarks = [
                    Landmark.from_dict(row) 
                    for row in landmark_rows 
                    if row.get("LOCATION_ID") == loc.id
                ]
        
        return self._locations_cache
    
    def get_all_suspects(self) -> list[Suspect]:
        """Load all suspects from database."""
        if self._suspects_cache is None:
            rows = execute_query("SELECT * FROM suspects")
            self._suspects_cache = [Suspect.from_dict(row) for row in rows]
        return self._suspects_cache
    
    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        """Get a specific location by ID."""
        locations = self.get_all_locations()
        for loc in locations:
            if loc.id == location_id:
                return loc
        return None
    
    def get_suspect_by_id(self, suspect_id: str) -> Optional[Suspect]:
        """Get a specific suspect by ID."""
        suspects = self.get_all_suspects()
        for sus in suspects:
            if sus.id == suspect_id:
                return sus
        return None
    
    def generate_case(
        self, 
        player_id: str, 
        difficulty: int,
        starting_location_id: str = "loc_bozeman"
    ) -> Case:
        """
        Generate a new case for the player.
        
        Args:
            player_id: ID of the player
            difficulty: Difficulty level (1-5)
            starting_location_id: Where the player starts (default: Bozeman)
        
        Returns:
            A new Case object ready to play
        """
        config = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG[1])
        
        # Get all locations and suspects
        all_locations = self.get_all_locations()
        all_suspects = self.get_all_suspects()
        
        # Choose a random suspect (prefer Snowflake Boseman for thematic fun)
        if random.random() < 0.3:  # 30% chance of main villain
            suspect = next((s for s in all_suspects if s.id == "sus_boseman"), 
                          random.choice(all_suspects))
        else:
            suspect = random.choice(all_suspects)
        
        # Choose a random stolen item
        stolen_item = random.choice(STOLEN_ITEMS)
        
        # Generate the suspect's travel path
        num_locations = random.randint(config["min_locations"], config["max_locations"])
        location_path = self._generate_travel_path(
            all_locations, 
            starting_location_id, 
            num_locations
        )
        
        # Create case ID
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        
        # Create the case object
        case = Case(
            id=case_id,
            player_id=player_id,
            suspect=suspect,
            stolen_item=stolen_item,
            difficulty=difficulty,
            location_path=[loc.id for loc in location_path],
            status=CaseStatus.ACTIVE,
        )
        
        # Create initial progress
        case.progress = CaseProgress(
            case_id=case_id,
            current_location_id=starting_location_id,
            suspect_location_idx=1,  # Suspect starts one step ahead
            hours_remaining=config["time_budget"],
            clues_gathered=[],
            locations_visited=[starting_location_id],
        )
        
        # Save to database
        self._save_case(case)
        
        return case
    
    def _generate_travel_path(
        self, 
        all_locations: list[Location], 
        start_id: str, 
        num_locations: int
    ) -> list[Location]:
        """
        Generate a logical travel path for the suspect.
        
        The path tries to be somewhat geographically logical,
        preferring nearby locations but occasionally jumping continents.
        """
        start_location = next((l for l in all_locations if l.id == start_id), 
                             all_locations[0])
        
        path = [start_location]
        available = [l for l in all_locations if l.id != start_id]
        
        current = start_location
        
        for _ in range(num_locations - 1):
            if not available:
                break
            
            # Weight locations by inverse distance (prefer closer, but allow far)
            weights = []
            for loc in available:
                distance = current._haversine_distance(loc)
                # Inverse distance with a minimum to allow some far jumps
                weight = 1.0 / max(distance, 500) 
                # Boost same-continent locations
                if loc.continent == current.continent:
                    weight *= 2
                weights.append(weight)
            
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            # Choose next location
            next_loc = random.choices(available, weights=weights, k=1)[0]
            path.append(next_loc)
            available.remove(next_loc)
            current = next_loc
        
        return path
    
    def _save_case(self, case: Case) -> None:
        """Save a new case to the database."""
        location_path_json = str(case.location_path).replace("'", '"')
        
        # Insert case record
        execute_write(f"""
            INSERT INTO cases (case_id, player_id, suspect_id, stolen_item, difficulty, location_path, status)
            VALUES (
                '{case.id}',
                '{case.player_id}',
                '{case.suspect.id}',
                '{case.stolen_item.replace("'", "''")}',
                {case.difficulty},
                PARSE_JSON('{location_path_json}'),
                '{case.status.value}'
            )
        """)
        
        # Insert progress record
        if case.progress:
            locations_visited_json = str(case.progress.locations_visited).replace("'", '"')
            execute_write(f"""
                INSERT INTO case_progress (case_id, current_location_id, suspect_location_idx, 
                                          hours_remaining, clues_gathered, locations_visited)
                VALUES (
                    '{case.id}',
                    '{case.progress.current_location_id}',
                    {case.progress.suspect_location_idx},
                    {case.progress.hours_remaining},
                    PARSE_JSON('[]'),
                    PARSE_JSON('{locations_visited_json}')
                )
            """)
    
    def load_case(self, case_id: str) -> Optional[Case]:
        """Load an existing case from the database."""
        case_rows = execute_query(f"SELECT * FROM cases WHERE case_id = '{case_id}'")
        if not case_rows:
            return None
        
        case_data = case_rows[0]
        
        # Load suspect
        suspect = self.get_suspect_by_id(case_data.get("SUSPECT_ID", ""))
        
        # Create case
        case = Case.from_dict(case_data, suspect)
        
        # Load progress
        progress_rows = execute_query(
            f"SELECT * FROM case_progress WHERE case_id = '{case_id}'"
        )
        if progress_rows:
            case.progress = CaseProgress.from_dict(progress_rows[0])
        
        return case
    
    def load_active_case_for_player(self, player_id: str) -> Optional[Case]:
        """Load the active case for a player, if any."""
        case_rows = execute_query(f"""
            SELECT * FROM cases 
            WHERE player_id = '{player_id}' AND status = 'active'
            ORDER BY started_at DESC
            LIMIT 1
        """)
        
        if not case_rows:
            return None
        
        return self.load_case(case_rows[0].get("CASE_ID", ""))
    
    def update_case_progress(self, case: Case) -> None:
        """Update case progress in the database."""
        if not case.progress:
            return
        
        # Convert clues to JSON-safe format
        clues_json = "[]"  # Simplified - in production, serialize properly
        locations_json = str(case.progress.locations_visited).replace("'", '"')
        
        execute_write(f"""
            UPDATE case_progress
            SET current_location_id = '{case.progress.current_location_id}',
                suspect_location_idx = {case.progress.suspect_location_idx},
                hours_remaining = {case.progress.hours_remaining},
                locations_visited = PARSE_JSON('{locations_json}'),
                updated_at = CURRENT_TIMESTAMP()
            WHERE case_id = '{case.id}'
        """)
    
    def update_case_status(self, case: Case, status: CaseStatus) -> None:
        """Update the case status."""
        case.status = status
        execute_write(f"""
            UPDATE cases
            SET status = '{status.value}'
            WHERE case_id = '{case.id}'
        """)

