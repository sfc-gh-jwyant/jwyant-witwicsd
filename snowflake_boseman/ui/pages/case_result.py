"""Case result page - win/lose screens."""

import streamlit as st
from typing import Optional

from ...models import Case, Player, Suspect


def render_case_result(
    won: bool,
    case: Case,
    player: Player,
    score: int = 0,
    message: str = "",
) -> dict:
    """
    Render the case result screen (win or lose).
    
    Returns dict with action:
    - {"action": "main_menu"}
    - {"action": "new_case"}
    - {"action": None}
    """
    result = {"action": None}
    
    if won:
        _render_victory_screen(case, player, score, message)
    else:
        _render_defeat_screen(case, player, message)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🏠 Return to Main Menu", use_container_width=True, type="primary"):
            result = {"action": "main_menu"}
        
        if st.button("🔍 Start New Case", use_container_width=True):
            result = {"action": "new_case"}
    
    return result


def _render_victory_screen(
    case: Case,
    player: Player,
    score: int,
    message: str,
) -> None:
    """Render the victory screen."""
    st.balloons()
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(180deg, #2E7D32, #1B5E20);
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        border: 4px solid #C4A35A;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    ">
        <div style="font-size: 64px; margin-bottom: 16px;">
            🎉🏆🎉
        </div>
        <h1 style="
            color: #C4A35A;
            font-family: 'Playfair Display', serif;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        ">
            CASE CLOSED!
        </h1>
        <p style="
            color: #F5E6D3;
            font-size: 20px;
            margin: 16px 0;
        ">
            {message}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats card
    st.markdown(f"""
    <div style="
        background: #D4B896;
        padding: 24px;
        border-radius: 8px;
        margin-top: 24px;
        border: 3px solid #3D2817;
    ">
        <h3 style="
            color: #2A1810;
            font-family: 'Playfair Display', serif;
            text-align: center;
            margin: 0 0 20px 0;
        ">
            📊 Case Summary
        </h3>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            text-align: center;
        ">
            <div>
                <div style="font-size: 32px; color: #C4A35A;">🎯</div>
                <div style="font-size: 28px; font-weight: bold; color: #2A1810;">
                    {score:,}
                </div>
                <div style="font-size: 12px; color: #555;">SCORE</div>
            </div>
            <div>
                <div style="font-size: 32px; color: #C4A35A;">{player.rank_icon}</div>
                <div style="font-size: 18px; font-weight: bold; color: #2A1810;">
                    {player.rank}
                </div>
                <div style="font-size: 12px; color: #555;">CURRENT RANK</div>
            </div>
            <div>
                <div style="font-size: 32px; color: #C4A35A;">📁</div>
                <div style="font-size: 28px; font-weight: bold; color: #2A1810;">
                    {player.cases_solved}
                </div>
                <div style="font-size: 12px; color: #555;">CASES SOLVED</div>
            </div>
        </div>
        
        <div style="
            margin-top: 20px;
            padding-top: 16px;
            border-top: 2px dashed #8B7355;
            text-align: center;
        ">
            <p style="color: #333; margin: 0;">
                <strong>Criminal Apprehended:</strong> {case.suspect.name}
            </p>
            <p style="color: #555; font-size: 13px; margin: 4px 0 0 0;">
                Recovered: {case.stolen_item}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for rank up
    cases_until_next = player.cases_until_next_rank()
    if cases_until_next:
        st.info(f"📈 {cases_until_next} more case(s) until next rank!")


def _render_defeat_screen(
    case: Case,
    player: Player,
    message: str,
) -> None:
    """Render the defeat screen."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(180deg, #5C1A1A, #3D1010);
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        border: 4px solid #8B0000;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    ">
        <div style="font-size: 64px; margin-bottom: 16px;">
            😔💨
        </div>
        <h1 style="
            color: #F44336;
            font-family: 'Playfair Display', serif;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        ">
            CASE CLOSED - UNSOLVED
        </h1>
        <p style="
            color: #F5E6D3;
            font-size: 20px;
            margin: 16px 0;
        ">
            {message}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Escape details
    st.markdown(f"""
    <div style="
        background: #D4B896;
        padding: 24px;
        border-radius: 8px;
        margin-top: 24px;
        border: 3px solid #3D2817;
    ">
        <h3 style="
            color: #2A1810;
            font-family: 'Playfair Display', serif;
            text-align: center;
            margin: 0 0 16px 0;
        ">
            📋 Case File
        </h3>
        
        <div style="text-align: center;">
            <p style="color: #333;">
                <strong>Escaped Criminal:</strong> {case.suspect.name}
            </p>
            <p style="color: #555; font-size: 13px;">
                Still missing: {case.stolen_item}
            </p>
            <p style="color: #666; font-size: 12px; font-style: italic; margin-top: 16px;">
                Don't give up! Every detective has cases that get away.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_arrest_screen(suspects: list[Suspect]) -> Optional[str]:
    """
    Render the arrest suspect selection screen.
    
    Returns the ID of the selected suspect, or None.
    """
    st.markdown("""
    <div style="
        background: linear-gradient(180deg, #1a1a2e, #16213e);
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
        border: 2px solid #C4A35A;
    ">
        <h2 style="
            color: #C4A35A;
            font-family: 'Playfair Display', serif;
            margin: 0;
        ">
            🚨 ARREST WARRANT 🚨
        </h2>
        <p style="color: #D4B896; margin: 12px 0 0 0;">
            Select the suspect you believe committed the crime
        </p>
        <p style="color: #F44336; font-size: 13px; margin: 8px 0 0 0;">
            ⚠️ Warning: Arresting the wrong suspect will end the case!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display suspects in a grid
    cols = st.columns(3)
    selected_id = None
    
    for i, suspect in enumerate(suspects):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                background: #D4B896;
                border: 2px solid #3D2817;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
                text-align: center;
            ">
                <div style="font-size: 48px;">🕵️</div>
                <div style="
                    font-weight: bold;
                    color: #2A1810;
                    margin: 8px 0;
                ">
                    {suspect.name}
                </div>
                <div style="font-size: 11px; color: #555;">
                    {suspect.hair_color} hair<br>
                    {suspect.hobby}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Arrest", key=f"arrest_{suspect.id}", use_container_width=True):
                selected_id = suspect.id
    
    return selected_id

