"""Telemetry tracking for game analytics."""

import uuid
import json
from typing import Optional, Any
from datetime import datetime

from ..models import Case
from ..database.connection import execute_write, execute_query


class TelemetryTracker:
    """Tracks game events for analytics and debugging."""
    
    def __init__(self):
        """Initialize the telemetry tracker."""
        self._session_start_time: Optional[datetime] = None
    
    def start_session(self, player_id: str) -> str:
        """
        Start a new game session.
        
        Returns the session ID.
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        self._session_start_time = datetime.now()
        
        try:
            execute_write(f"""
                INSERT INTO game_sessions (session_id, player_id, cases_started, cases_completed)
                VALUES ('{session_id}', '{player_id}', 0, 0)
            """)
        except Exception:
            # Telemetry should never break the game
            pass
        
        return session_id
    
    def end_session(self, session_id: str) -> None:
        """End the current game session."""
        if not session_id:
            return
        
        duration = 0
        if self._session_start_time:
            duration = int((datetime.now() - self._session_start_time).total_seconds())
        
        try:
            execute_write(f"""
                UPDATE game_sessions
                SET ended_at = CURRENT_TIMESTAMP(),
                    duration_seconds = {duration}
                WHERE session_id = '{session_id}'
            """)
        except Exception:
            pass
    
    def log_event(
        self,
        session_id: Optional[str],
        player_id: str,
        event_type: str,
        case_id: Optional[str] = None,
        event_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log a game event for analytics.
        
        Event types:
        - session_start: Player opened the app
        - session_end: Player closed/left
        - case_start: Started new case
        - case_win: Successfully arrested suspect
        - case_lose: Failed case
        - case_abandon: Left case incomplete
        - travel: Traveled to new city
        - investigate: Gathered clues
        - arrest_attempt: Tried to arrest
        - clue_view: Reviewed a clue
        """
        if not session_id:
            return
        
        event_id = f"event_{uuid.uuid4().hex[:12]}"
        event_data_json = json.dumps(event_data or {})
        
        case_clause = f"'{case_id}'" if case_id else "NULL"
        
        try:
            execute_write(f"""
                INSERT INTO game_events (event_id, session_id, player_id, case_id, event_type, event_data)
                VALUES (
                    '{event_id}',
                    '{session_id}',
                    '{player_id}',
                    {case_clause},
                    '{event_type}',
                    PARSE_JSON('{event_data_json}')
                )
            """)
        except Exception:
            # Telemetry should never break the game
            pass
    
    def record_case_analytics(
        self,
        case: Case,
        outcome: str,
        time_budget: int,
        time_used: int,
    ) -> None:
        """Record aggregated case outcome for analytics."""
        if not case or not case.progress:
            return
        
        try:
            execute_write(f"""
                INSERT INTO case_analytics (
                    case_id, player_id, difficulty, outcome,
                    total_locations_in_path, locations_visited,
                    correct_travels, wrong_travels, clues_gathered,
                    time_budget_hours, time_used_hours,
                    started_at, ended_at
                )
                VALUES (
                    '{case.id}',
                    '{case.player_id}',
                    {case.difficulty},
                    '{outcome}',
                    {len(case.location_path)},
                    {len(case.progress.locations_visited)},
                    {case.progress.correct_travels},
                    {case.progress.wrong_travels},
                    {len(case.progress.clues_gathered)},
                    {time_budget},
                    {time_used},
                    '{case.started_at}' if case.started_at else CURRENT_TIMESTAMP(),
                    CURRENT_TIMESTAMP()
                )
            """)
        except Exception:
            pass
    
    def record_friction_point(
        self,
        player_id: str,
        case_id: str,
        location_id: str,
        friction_type: str,
        attempts: int = 1,
        time_spent: int = 0,
    ) -> None:
        """
        Record a friction point where player got stuck.
        
        Friction types:
        - repeated_wrong_travel: Player went to wrong locations multiple times
        - time_expired_here: Time ran out at this location
        - abandoned_here: Player abandoned case at this location
        """
        friction_id = f"friction_{uuid.uuid4().hex[:12]}"
        
        try:
            execute_write(f"""
                INSERT INTO friction_points (
                    friction_id, player_id, case_id, location_id,
                    friction_type, attempts_at_location, time_spent_hours
                )
                VALUES (
                    '{friction_id}',
                    '{player_id}',
                    '{case_id}',
                    '{location_id}',
                    '{friction_type}',
                    {attempts},
                    {time_spent}
                )
            """)
        except Exception:
            pass
    
    def increment_session_cases(
        self, 
        session_id: str, 
        started: bool = False, 
        completed: bool = False
    ) -> None:
        """Increment case counters for a session."""
        if not session_id:
            return
        
        updates = []
        if started:
            updates.append("cases_started = cases_started + 1")
        if completed:
            updates.append("cases_completed = cases_completed + 1")
        
        if updates:
            try:
                execute_write(f"""
                    UPDATE game_sessions
                    SET {', '.join(updates)}
                    WHERE session_id = '{session_id}'
                """)
            except Exception:
                pass

