"""
WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?

A geography mystery adventure game inspired by Carmen Sandiego.
Built with Streamlit in Snowflake.

Main entry point for the application.
"""

import streamlit as st
from enum import Enum

# Import game components
from game import GameController
from ui import apply_theme
from ui.pages import (
    render_main_menu,
    render_investigation,
    render_travel,
    render_case_result,
    render_high_scores,
)
from ui.pages.case_result import render_arrest_screen


class GameState(Enum):
    """Current state of the game UI."""
    MAIN_MENU = "main_menu"
    INVESTIGATION = "investigation"
    TRAVEL = "travel"
    ARREST = "arrest"
    CASE_RESULT = "case_result"
    HIGH_SCORES = "high_scores"


def init_session_state():
    """Initialize session state variables."""
    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState.MAIN_MENU
    
    if "controller" not in st.session_state:
        st.session_state.controller = GameController()
    
    if "new_clues" not in st.session_state:
        st.session_state.new_clues = None
    
    if "case_result" not in st.session_state:
        st.session_state.case_result = None


def main():
    """Main application entry point."""
    # Page config
    st.set_page_config(
        page_title="Where is Snowflake Boseman Montana?",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Apply custom theme
    apply_theme()
    
    # Initialize session state
    init_session_state()
    
    controller: GameController = st.session_state.controller
    
    # Get or create player
    try:
        player = controller.get_or_create_player()
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.info("Make sure you're running this app in Snowflake with proper database access.")
        return
    
    # Route to appropriate page based on game state
    current_state = st.session_state.game_state
    
    if current_state == GameState.MAIN_MENU:
        _handle_main_menu(controller, player)
    
    elif current_state == GameState.INVESTIGATION:
        _handle_investigation(controller, player)
    
    elif current_state == GameState.TRAVEL:
        _handle_travel(controller, player)
    
    elif current_state == GameState.ARREST:
        _handle_arrest(controller, player)
    
    elif current_state == GameState.CASE_RESULT:
        _handle_case_result(controller, player)
    
    elif current_state == GameState.HIGH_SCORES:
        _handle_high_scores(controller, player)


def _handle_main_menu(controller: GameController, player):
    """Handle main menu state."""
    has_active_case = controller.get_current_case() is not None
    
    result = render_main_menu(player, has_active_case)
    
    if result["action"] == "new_case":
        difficulty = result.get("difficulty", 1)
        controller.start_new_case(difficulty)
        st.session_state.game_state = GameState.INVESTIGATION
        st.rerun()
    
    elif result["action"] == "continue":
        st.session_state.game_state = GameState.INVESTIGATION
        st.rerun()
    
    elif result["action"] == "high_scores":
        st.session_state.game_state = GameState.HIGH_SCORES
        st.rerun()


def _handle_investigation(controller: GameController, player):
    """Handle investigation state."""
    case = controller.get_current_case()
    current_location = controller.get_current_location()
    
    if not case or not current_location:
        st.session_state.game_state = GameState.MAIN_MENU
        st.rerun()
        return
    
    result = render_investigation(controller, case, current_location, player)
    
    if result["action"] == "investigate":
        clues = controller.investigate()
        st.session_state.new_clues = clues
        
        # Check if time ran out
        if controller.get_time_remaining() <= 0:
            st.session_state.case_result = {
                "won": False,
                "message": "Time ran out! The suspect escaped.",
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


def _handle_travel(controller: GameController, player):
    """Handle travel state."""
    case = controller.get_current_case()
    current_location = controller.get_current_location()
    
    if not case or not current_location:
        st.session_state.game_state = GameState.MAIN_MENU
        st.rerun()
        return
    
    from ui.pages.travel import render_travel
    result = render_travel(controller, case, current_location)
    
    if result["action"] == "back":
        st.session_state.game_state = GameState.INVESTIGATION
        st.rerun()
    
    elif result["action"] == "travel_to":
        destination_id = result.get("destination_id")
        travel_result = controller.travel_to(destination_id)
        
        if travel_result.get("game_over"):
            st.session_state.case_result = {
                "won": False,
                "message": travel_result.get("message", "The suspect escaped!"),
                "score": 0,
            }
            st.session_state.game_state = GameState.CASE_RESULT
        else:
            st.success(travel_result.get("message", "Traveled successfully!"))
            
            if travel_result.get("arrived_at_suspect"):
                st.info("🎯 The suspect is here! You can attempt an arrest!")
            
            st.session_state.game_state = GameState.INVESTIGATION
        
        st.rerun()


def _handle_arrest(controller: GameController, player):
    """Handle arrest state."""
    case = controller.get_current_case()
    
    if not case:
        st.session_state.game_state = GameState.MAIN_MENU
        st.rerun()
        return
    
    suspects = controller.get_all_suspects()
    
    # Back button
    if st.button("← Back to Investigation"):
        st.session_state.game_state = GameState.INVESTIGATION
        st.rerun()
        return
    
    selected_suspect_id = render_arrest_screen(suspects)
    
    if selected_suspect_id:
        arrest_result = controller.attempt_arrest(selected_suspect_id)
        
        st.session_state.case_result = {
            "won": arrest_result.get("won", False),
            "message": arrest_result.get("message", ""),
            "score": arrest_result.get("score", 0),
        }
        st.session_state.game_state = GameState.CASE_RESULT
        st.rerun()


def _handle_case_result(controller: GameController, player):
    """Handle case result state."""
    case_result = st.session_state.case_result or {}
    
    # Get the case info (might be None if already cleared)
    case = controller._current_case or controller.get_current_case()
    
    if not case:
        # Create a dummy case for display if none available
        from models import Case, Suspect
        from models.case import CaseStatus
        case = Case(
            id="unknown",
            player_id=player.id,
            suspect=Suspect(
                id="unknown",
                name="Unknown Suspect",
                hair_color="Unknown",
                eye_color="Unknown",
                hobby="Unknown",
                vehicle="Unknown",
                favorite_food="Unknown",
            ),
            stolen_item="Unknown Item",
            difficulty=1,
            location_path=[],
            status=CaseStatus.ACTIVE,
        )
    
    # Refresh player to get updated stats
    player = controller.get_or_create_player()
    
    result = render_case_result(
        won=case_result.get("won", False),
        case=case,
        player=player,
        score=case_result.get("score", 0),
        message=case_result.get("message", ""),
    )
    
    if result["action"] == "main_menu":
        st.session_state.case_result = None
        st.session_state.game_state = GameState.MAIN_MENU
        st.rerun()
    
    elif result["action"] == "new_case":
        st.session_state.case_result = None
        st.session_state.game_state = GameState.MAIN_MENU
        st.rerun()


def _handle_high_scores(controller: GameController, player):
    """Handle high scores state."""
    try:
        leaderboard = controller.get_leaderboard(limit=10)
    except Exception:
        leaderboard = []
    
    result = render_high_scores(leaderboard)
    
    if result["action"] == "back":
        st.session_state.game_state = GameState.MAIN_MENU
        st.rerun()


if __name__ == "__main__":
    main()

