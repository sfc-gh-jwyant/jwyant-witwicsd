"""Investigation page - main gameplay screen."""

import streamlit as st
from typing import Optional

from ...models import Case, Location, Player, Clue
from ...game import GameController
from ..components.art_placeholder import render_art, render_placeholder, ArtType
from ..components.clue_notebook import render_clue_notebook, render_clue_popup
from ..components.suspect_dossier import render_suspect_dossier


def render_investigation(
    controller: GameController,
    case: Case,
    current_location: Location,
    player: Player,
) -> dict:
    """
    Render the main investigation screen.
    
    This is the primary gameplay view where players gather clues,
    travel, and attempt arrests.
    
    Returns dict with action taken:
    - {"action": "travel"}
    - {"action": "investigate"}
    - {"action": "arrest"}
    - {"action": "view_clues"}
    - {"action": None}
    """
    result = {"action": None}
    
    # Header bar with case info
    _render_header_bar(case, player, controller)
    
    # Main content area
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_main:
        # Location background
        st.markdown(f"""
        <div style="
            position: relative;
            min-height: 400px;
            background: linear-gradient(145deg, #3D2817, #2A1810);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        ">
        """, unsafe_allow_html=True)
        
        # Location art placeholder (full background)
        render_art(
            current_location.image_url,
            ArtType.LOCATION,
            f"{current_location.city}, {current_location.country}",
        )
        
        # Location name overlay
        st.markdown(f"""
        <div style="
            position: relative;
            background: rgba(0,0,0,0.7);
            padding: 16px 24px;
            border-radius: 8px;
            margin-top: 16px;
        ">
            <h2 style="
                color: #C4A35A;
                font-family: 'Playfair Display', serif;
                margin: 0;
            ">
                📍 {current_location.city}
            </h2>
            <p style="
                color: #D4B896;
                margin: 4px 0 0 0;
                font-size: 14px;
            ">
                {current_location.country} • {current_location.continent}
            </p>
            <p style="
                color: #999;
                margin: 12px 0 0 0;
                font-size: 13px;
                font-style: italic;
            ">
                {current_location.description or "A mysterious location awaits investigation..."}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Check if just investigated (show new clues)
        if "new_clues" in st.session_state and st.session_state.new_clues:
            render_clue_popup(st.session_state.new_clues)
            st.session_state.new_clues = None
        
        # Action buttons
        st.markdown("### 🎯 Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 INVESTIGATE", use_container_width=True, type="primary"):
                result = {"action": "investigate"}
        
        with col2:
            if st.button("✈️ TRAVEL", use_container_width=True):
                result = {"action": "travel"}
        
        with col3:
            if st.button("🚨 ARREST", use_container_width=True):
                result = {"action": "arrest"}
        
        # Clue notebook (collapsible)
        clues = controller.get_gathered_clues()
        render_clue_notebook(clues, expanded=False)
    
    with col_sidebar:
        # Suspect dossier
        st.markdown("### 🕵️ Suspect")
        render_suspect_dossier(case.suspect, show_full_details=False)
        
        # Landmark info if available
        if current_location.landmarks:
            st.markdown("### 🏛️ Landmarks")
            for landmark in current_location.landmarks[:2]:
                render_art(
                    landmark.image_url,
                    ArtType.LANDMARK,
                    landmark.name,
                )
                st.caption(landmark.name)
    
    return result


def _render_header_bar(case: Case, player: Player, controller: GameController) -> None:
    """Render the header bar with case info and time."""
    time_remaining = controller.get_time_remaining()
    time_pct = controller.get_time_percentage()
    urgency = controller.get_urgency_level()
    
    # Color based on urgency
    time_color = {
        "normal": "#4CAF50",
        "warning": "#FF9800",
        "critical": "#F44336",
    }.get(urgency, "#4CAF50")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #2A1810, #3D2817);
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        border: 2px solid #C4A35A;
    ">
        <div>
            <span style="color: #C4A35A; font-size: 12px;">CASE FILE</span>
            <div style="color: #F5E6D3; font-weight: bold;">
                {case.stolen_item}
            </div>
        </div>
        
        <div>
            <span style="color: #C4A35A; font-size: 12px;">DIFFICULTY</span>
            <div style="color: #F5E6D3;">
                {case.difficulty_name}
            </div>
        </div>
        
        <div>
            <span style="color: #C4A35A; font-size: 12px;">AGENT</span>
            <div style="color: #F5E6D3;">
                {player.rank_icon} {player.display_name}
            </div>
        </div>
        
        <div style="text-align: right;">
            <span style="color: #C4A35A; font-size: 12px;">⏱️ TIME REMAINING</span>
            <div style="
                color: {time_color};
                font-size: 20px;
                font-weight: bold;
            ">
                {time_remaining} hours
            </div>
            <div style="
                background: #1a1a1a;
                height: 6px;
                border-radius: 3px;
                overflow: hidden;
                margin-top: 4px;
            ">
                <div style="
                    background: {time_color};
                    height: 100%;
                    width: {time_pct}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_investigation_result(message: str, success: bool) -> None:
    """Render the result of an investigation action."""
    icon = "✅" if success else "⚠️"
    bg_color = "#2E7D32" if success else "#F57C00"
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        color: white;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
        text-align: center;
    ">
        <span style="font-size: 24px;">{icon}</span>
        <p style="margin: 8px 0 0 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

