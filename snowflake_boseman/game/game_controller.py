"""Main game controller orchestrating gameplay."""

from typing import Optional
import uuid

from ..models import Location, Suspect, Clue, Player, Case, TimeManager
from ..models.case import CaseStatus, CaseProgress
from ..database.connection import execute_query, execute_write, get_current_user
from .case_generator import CaseGenerator
from .clue_generator import ClueGenerator
from .telemetry import TelemetryTracker


class GameController:
    """
    Main controller for game logic.
    
    Handles player management, case flow, travel, investigation, and arrests.
    """
    
    def __init__(self):
        """Initialize the game controller."""
        self.case_generator = CaseGenerator()
        self.clue_generator = ClueGenerator()
        self.telemetry = TelemetryTracker()
        
        self._current_player: Optional[Player] = None
        self._current_case: Optional[Case] = None
        self._time_manager: Optional[TimeManager] = None
        self._session_id: Optional[str] = None
    
    # =========================================================================
    # Player Management
    # =========================================================================
    
    def get_or_create_player(self) -> Player:
        """Get current player from Snowflake session, creating if needed."""
        if self._current_player:
            return self._current_player
        
        user_info = get_current_user()
        player_id = user_info["username"]
        
        # Check if player exists
        rows = execute_query(f"SELECT * FROM players WHERE player_id = '{player_id}'")
        
        if rows:
            self._current_player = Player.from_dict(rows[0])
        else:
            # Create new player
            execute_write(f"""
                INSERT INTO players (player_id, snowflake_user, rank, cases_solved, total_score)
                VALUES ('{player_id}', '{player_id}', 'Rookie', 0, 0)
            """)
            self._current_player = Player(
                id=player_id,
                snowflake_user=player_id,
                rank="Rookie",
                cases_solved=0,
                total_score=0,
            )
        
        # Start session tracking
        self._session_id = self.telemetry.start_session(player_id)
        
        return self._current_player
    
    def update_player_stats(self, score_delta: int = 0, case_won: bool = False) -> None:
        """Update player statistics after a case."""
        if not self._current_player:
            return
        
        self._current_player.total_score += score_delta
        if case_won:
            self._current_player.cases_solved += 1
            self._current_player.update_rank()
        
        execute_write(f"""
            UPDATE players
            SET cases_solved = {self._current_player.cases_solved},
                total_score = {self._current_player.total_score},
                rank = '{self._current_player.rank}'
            WHERE player_id = '{self._current_player.id}'
        """)
    
    # =========================================================================
    # Case Management
    # =========================================================================
    
    def start_new_case(self, difficulty: int) -> Case:
        """Start a new case for the current player."""
        player = self.get_or_create_player()
        
        # Generate new case
        case = self.case_generator.generate_case(
            player_id=player.id,
            difficulty=difficulty,
            starting_location_id="loc_bozeman"
        )
        
        self._current_case = case
        self._time_manager = TimeManager(difficulty)
        
        # Track telemetry
        self.telemetry.log_event(
            session_id=self._session_id,
            player_id=player.id,
            event_type="case_start",
            case_id=case.id,
            event_data={"difficulty": difficulty, "suspect_id": case.suspect.id}
        )
        
        return case
    
    def get_current_case(self) -> Optional[Case]:
        """Get the current active case."""
        if self._current_case and self._current_case.is_active:
            return self._current_case
        
        # Try to load from database
        player = self.get_or_create_player()
        self._current_case = self.case_generator.load_active_case_for_player(player.id)
        
        if self._current_case:
            self._time_manager = TimeManager(
                self._current_case.difficulty,
                elapsed_hours=(
                    self._current_case.progress.hours_remaining 
                    if self._current_case.progress else 0
                )
            )
        
        return self._current_case
    
    def get_current_location(self) -> Optional[Location]:
        """Get the player's current location."""
        case = self.get_current_case()
        if not case or not case.progress:
            return None
        
        return self.case_generator.get_location_by_id(case.progress.current_location_id)
    
    def get_available_destinations(self) -> list[Location]:
        """Get locations the player can travel to."""
        current = self.get_current_location()
        if not current:
            return []
        
        all_locations = self.case_generator.get_all_locations()
        
        # Filter out current location and optionally show travel time feasibility
        available = []
        for loc in all_locations:
            if loc.id != current.id:
                if self._time_manager and self._time_manager.can_travel_to(current, loc):
                    available.append(loc)
        
        # Sort by distance from current location
        available.sort(key=lambda l: current._haversine_distance(l))
        
        return available
    
    # =========================================================================
    # Game Actions
    # =========================================================================
    
    def travel_to(self, destination_id: str) -> dict:
        """
        Travel to a new location.
        
        Returns:
            dict with keys: success, hours_spent, message, arrived_at_suspect
        """
        case = self.get_current_case()
        current = self.get_current_location()
        destination = self.case_generator.get_location_by_id(destination_id)
        
        if not case or not current or not destination:
            return {"success": False, "message": "Cannot travel right now.", "hours_spent": 0}
        
        # Calculate and deduct travel time
        success, hours_spent = self._time_manager.travel(current, destination)
        
        if not success:
            return {
                "success": False,
                "message": f"Not enough time! Need {hours_spent} hours but only have {self._time_manager.hours_remaining}.",
                "hours_spent": 0
            }
        
        # Update case progress
        case.progress.current_location_id = destination_id
        case.progress.hours_remaining = self._time_manager.hours_remaining
        case.progress.locations_visited.append(destination_id)
        
        # Check if this was the correct next location
        correct_next = case.get_suspect_next_location()
        is_correct = destination_id == correct_next
        
        if is_correct:
            case.progress.correct_travels += 1
            # Suspect moves ahead
            case.progress.suspect_location_idx += 1
        else:
            case.progress.wrong_travels += 1
        
        # Check if player caught up to suspect
        arrived_at_suspect = case.is_player_at_suspect_location(destination_id)
        
        # Save progress
        self.case_generator.update_case_progress(case)
        
        # Track telemetry
        self.telemetry.log_event(
            session_id=self._session_id,
            player_id=self._current_player.id,
            event_type="travel",
            case_id=case.id,
            event_data={
                "from_location": current.id,
                "to_location": destination_id,
                "was_correct": is_correct,
                "hours_spent": hours_spent,
            }
        )
        
        # Check for time running out
        if self._time_manager.is_time_up:
            self._end_case_loss("time")
            return {
                "success": True,
                "message": "Time has run out! The suspect escaped.",
                "hours_spent": hours_spent,
                "arrived_at_suspect": False,
                "game_over": True,
            }
        
        return {
            "success": True,
            "message": f"Arrived in {destination.city}, {destination.country}. ({hours_spent} hours)",
            "hours_spent": hours_spent,
            "arrived_at_suspect": arrived_at_suspect,
        }
    
    def investigate(self) -> list[Clue]:
        """
        Investigate the current location to gather clues.
        
        Returns list of clues found.
        """
        case = self.get_current_case()
        current = self.get_current_location()
        
        if not case or not current:
            return []
        
        # Deduct investigation time
        success, hours_spent = self._time_manager.investigate()
        
        if not success:
            return []
        
        # Update time in progress
        case.progress.hours_remaining = self._time_manager.hours_remaining
        
        # Get the next location in suspect's path (what clues should hint at)
        next_location_id = case.get_suspect_next_location()
        if not next_location_id:
            # Suspect is at final location
            next_location = self.case_generator.get_location_by_id(case.location_path[-1])
        else:
            next_location = self.case_generator.get_location_by_id(next_location_id)
        
        if not next_location:
            return []
        
        # Generate clues
        all_locations = self.case_generator.get_all_locations()
        clues = self.clue_generator.generate_clues_for_location(
            current_location=current,
            next_location=next_location,
            suspect=case.suspect,
            difficulty=case.difficulty,
            all_locations=all_locations,
        )
        
        # Add clues to gathered list
        case.progress.clues_gathered.extend(clues)
        
        # Save progress
        self.case_generator.update_case_progress(case)
        
        # Track telemetry
        self.telemetry.log_event(
            session_id=self._session_id,
            player_id=self._current_player.id,
            event_type="investigate",
            case_id=case.id,
            event_data={
                "location_id": current.id,
                "clues_received": len(clues),
            }
        )
        
        # Check for time running out
        if self._time_manager.is_time_up:
            self._end_case_loss("time")
        
        return clues
    
    def attempt_arrest(self, suspect_id: str) -> dict:
        """
        Attempt to arrest a suspect at the current location.
        
        Returns dict with success, message, and game outcome.
        """
        case = self.get_current_case()
        
        if not case:
            return {"success": False, "message": "No active case."}
        
        # Check if player is at suspect's location
        is_at_suspect_location = case.is_player_at_suspect_location(
            case.progress.current_location_id
        )
        
        # Check if correct suspect
        is_correct_suspect = suspect_id == case.suspect.id
        
        # Track arrest attempt
        self.telemetry.log_event(
            session_id=self._session_id,
            player_id=self._current_player.id,
            event_type="arrest_attempt",
            case_id=case.id,
            event_data={
                "suspect_guess": suspect_id,
                "was_correct": is_correct_suspect and is_at_suspect_location,
            }
        )
        
        if is_at_suspect_location and is_correct_suspect:
            # Successful arrest!
            return self._end_case_win()
        elif not is_at_suspect_location:
            return {
                "success": False,
                "message": "The suspect isn't here! Keep following the trail.",
                "game_over": False,
            }
        else:
            # Wrong suspect
            return self._end_case_loss("wrong_arrest")
    
    # =========================================================================
    # Case Resolution
    # =========================================================================
    
    def _end_case_win(self) -> dict:
        """Handle winning a case."""
        case = self.get_current_case()
        
        if not case:
            return {"success": False, "message": "No active case."}
        
        # Calculate score
        time_budget = self._time_manager.total_hours
        time_used = self._time_manager.elapsed_hours
        locations_visited = len(case.progress.locations_visited)
        
        score = self._calculate_score(
            case.difficulty, 
            time_budget, 
            time_used, 
            locations_visited
        )
        
        # Update case status
        self.case_generator.update_case_status(case, CaseStatus.WON)
        
        # Update player stats
        self.update_player_stats(score_delta=score, case_won=True)
        
        # Save high score
        self._save_high_score(case, score, time_used, locations_visited)
        
        # Track telemetry
        self.telemetry.log_event(
            session_id=self._session_id,
            player_id=self._current_player.id,
            event_type="case_win",
            case_id=case.id,
            event_data={
                "time_remaining": self._time_manager.hours_remaining,
                "locations_visited": locations_visited,
                "score": score,
            }
        )
        
        # Record analytics
        self.telemetry.record_case_analytics(
            case=case,
            outcome="won",
            time_budget=time_budget,
            time_used=time_used,
        )
        
        self._current_case = None
        
        return {
            "success": True,
            "message": f"You caught {case.suspect.name}! Case solved!",
            "game_over": True,
            "won": True,
            "score": score,
            "rank": self._current_player.rank,
        }
    
    def _end_case_loss(self, reason: str) -> dict:
        """Handle losing a case."""
        case = self.get_current_case()
        
        if not case:
            return {"success": False, "message": "No active case."}
        
        status = CaseStatus.LOST_TIME if reason == "time" else CaseStatus.LOST_WRONG_ARREST
        self.case_generator.update_case_status(case, status)
        
        # Track telemetry
        self.telemetry.log_event(
            session_id=self._session_id,
            player_id=self._current_player.id,
            event_type="case_lose",
            case_id=case.id,
            event_data={"reason": reason}
        )
        
        # Record analytics
        self.telemetry.record_case_analytics(
            case=case,
            outcome=f"lost_{reason}",
            time_budget=self._time_manager.total_hours,
            time_used=self._time_manager.elapsed_hours,
        )
        
        self._current_case = None
        
        if reason == "time":
            message = f"{case.suspect.name} escaped! You ran out of time."
        else:
            message = f"Wrong suspect! {case.suspect.name} got away while you were distracted."
        
        return {
            "success": False,
            "message": message,
            "game_over": True,
            "won": False,
        }
    
    def _calculate_score(
        self, 
        difficulty: int, 
        time_budget: int, 
        time_used: int, 
        locations_visited: int
    ) -> int:
        """Calculate score for a completed case."""
        difficulty_multiplier = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
        time_bonus = max(0, time_budget - time_used) * 100
        efficiency_bonus = max(0, (10 - locations_visited)) * 50
        return (time_bonus + efficiency_bonus) * difficulty_multiplier.get(difficulty, 1)
    
    def _save_high_score(
        self, 
        case: Case, 
        score: int, 
        time_used: int, 
        locations_visited: int
    ) -> None:
        """Save a high score entry."""
        score_id = f"score_{uuid.uuid4().hex[:12]}"
        execute_write(f"""
            INSERT INTO high_scores (score_id, player_id, case_id, difficulty, 
                                    completion_time_hours, locations_visited, score)
            VALUES (
                '{score_id}',
                '{self._current_player.id}',
                '{case.id}',
                {case.difficulty},
                {time_used},
                {locations_visited},
                {score}
            )
        """)
    
    # =========================================================================
    # Game State Queries
    # =========================================================================
    
    def get_time_remaining(self) -> int:
        """Get hours remaining in current case."""
        if self._time_manager:
            return self._time_manager.hours_remaining
        return 0
    
    def get_time_percentage(self) -> float:
        """Get percentage of time remaining."""
        if self._time_manager:
            return self._time_manager.time_percentage
        return 100.0
    
    def get_urgency_level(self) -> str:
        """Get current urgency level (normal, warning, critical)."""
        if self._time_manager:
            return self._time_manager.urgency_level
        return "normal"
    
    def get_gathered_clues(self) -> list[Clue]:
        """Get all clues gathered in current case."""
        case = self.get_current_case()
        if case and case.progress:
            return case.progress.clues_gathered
        return []
    
    def get_all_suspects(self) -> list[Suspect]:
        """Get all possible suspects for arrest selection."""
        return self.case_generator.get_all_suspects()
    
    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """Get top scores from leaderboard."""
        rows = execute_query(f"""
            SELECT p.snowflake_user, p.rank, hs.score, hs.difficulty, 
                   hs.completion_time_hours, hs.achieved_at
            FROM high_scores hs
            JOIN players p ON hs.player_id = p.player_id
            ORDER BY hs.score DESC
            LIMIT {limit}
        """)
        return rows

