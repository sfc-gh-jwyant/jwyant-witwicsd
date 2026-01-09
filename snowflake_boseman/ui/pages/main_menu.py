"""Main menu page."""

import streamlit as st
from typing import Optional

from ...models import Player, DIFFICULTY_CONFIG


def render_main_menu(player: Player, has_active_case: bool = False) -> dict:
    """
    Render the main menu screen.
    
    Returns a dict with the action to take:
    - {"action": "new_case", "difficulty": int}
    - {"action": "continue"}
    - {"action": "high_scores"}
    - {"action": None} if no action taken
    """
    result = {"action": None}
    
    # Header with title
    st.markdown("""
    <div style="
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(180deg, #5C1A1A 0%, #3D2817 100%);
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    ">
        <h1 style="
            color: #C4A35A;
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        ">
            🔍 WHERE IN THE WORLD IS 🔍
        </h1>
        <h2 style="
            color: #F5E6D3;
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        ">
            ❄️ SNOWFLAKE BOSEMAN MONTANA? ❄️
        </h2>
        <p style="
            color: #D4B896;
            font-size: 14px;
            margin-top: 16px;
            font-style: italic;
        ">
            A geography mystery adventure
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Player info card
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
            <div style="font-size: 32px; margin-bottom: 8px;">
                {player.rank_icon}
            </div>
            <div style="
                color: #2A1810;
                font-family: 'Playfair Display', serif;
                font-size: 18px;
                font-weight: bold;
            ">
                Agent {player.display_name}
            </div>
            <div style="color: #555; font-size: 14px; margin-top: 4px;">
                Rank: {player.rank}
            </div>
            <div style="
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 16px;
                color: #3D2817;
            ">
                <div>
                    <div style="font-size: 24px; font-weight: bold;">{player.cases_solved}</div>
                    <div style="font-size: 11px;">Cases Solved</div>
                </div>
                <div>
                    <div style="font-size: 24px; font-weight: bold;">{player.total_score:,}</div>
                    <div style="font-size: 11px;">Total Score</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Menu buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Continue button (if active case)
        if has_active_case:
            st.markdown("""
            <div style="
                background: #C4A35A;
                color: #2A1810;
                padding: 8px;
                border-radius: 8px 8px 0 0;
                text-align: center;
                font-weight: bold;
            ">
                📋 Case in Progress
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶️ CONTINUE INVESTIGATION", use_container_width=True, type="primary"):
                result = {"action": "continue"}
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # New case section
        st.markdown("""
        <div style="
            background: #3D2817;
            color: #C4A35A;
            padding: 12px;
            border-radius: 8px 8px 0 0;
            text-align: center;
            font-family: 'Playfair Display', serif;
        ">
            🆕 START NEW CASE
        </div>
        """, unsafe_allow_html=True)
        
        # Difficulty selector
        difficulty = st.selectbox(
            "Select Difficulty",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{DIFFICULTY_CONFIG[x]['name']} - {DIFFICULTY_CONFIG[x]['description']}",
            index=0,
            label_visibility="collapsed",
        )
        
        if st.button("🔍 START NEW CASE", use_container_width=True):
            result = {"action": "new_case", "difficulty": difficulty}
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # High scores button
        if st.button("🏆 HIGH SCORES", use_container_width=True):
            result = {"action": "high_scores"}
    
    # Footer
    st.markdown("""
    <div style="
        text-align: center;
        margin-top: 50px;
        color: #666;
        font-size: 12px;
    ">
        <p>Powered by Snowflake ❄️ | Inspired by Carmen Sandiego</p>
        <p>Track criminals across the globe using your geography knowledge!</p>
    </div>
    """, unsafe_allow_html=True)
    
    return result


def render_difficulty_info() -> None:
    """Render information about difficulty levels."""
    st.markdown("### Difficulty Levels")
    
    for level, config in DIFFICULTY_CONFIG.items():
        with st.expander(f"{config['name']}"):
            st.write(f"**Description:** {config['description']}")
            st.write(f"**Time Budget:** {config['time_budget']} hours")
            st.write(f"**Locations:** {config['min_locations']}-{config['max_locations']}")
            st.write(f"**Red Herrings:** {config['red_herrings']}")

