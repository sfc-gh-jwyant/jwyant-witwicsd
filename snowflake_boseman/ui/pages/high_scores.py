"""High scores leaderboard page."""

import streamlit as st
from typing import Optional

from ...models import DIFFICULTY_CONFIG


def render_high_scores(leaderboard: list[dict]) -> dict:
    """
    Render the high scores leaderboard.
    
    Returns dict with action:
    - {"action": "back"}
    - {"action": None}
    """
    result = {"action": None}
    
    # Header
    st.markdown("""
    <div style="
        background: linear-gradient(180deg, #C4A35A, #8B7355);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
        border: 4px solid #3D2817;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    ">
        <div style="font-size: 48px; margin-bottom: 8px;">🏆</div>
        <h1 style="
            color: #2A1810;
            font-family: 'Playfair Display', serif;
            margin: 0;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.3);
        ">
            HALL OF FAME
        </h1>
        <p style="
            color: #3D2817;
            margin: 8px 0 0 0;
        ">
            Top Detectives Around the World
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Main Menu"):
        result = {"action": "back"}
        return result
    
    if not leaderboard:
        st.info("No high scores yet! Be the first to solve a case!")
        return result
    
    # Leaderboard table
    st.markdown("""
    <div style="
        background: #D4B896;
        border: 3px solid #3D2817;
        border-radius: 8px;
        overflow: hidden;
    ">
        <table style="
            width: 100%;
            border-collapse: collapse;
            font-family: 'Georgia', serif;
        ">
            <thead>
                <tr style="background: #3D2817; color: #C4A35A;">
                    <th style="padding: 12px; text-align: center;">#</th>
                    <th style="padding: 12px; text-align: left;">Agent</th>
                    <th style="padding: 12px; text-align: center;">Rank</th>
                    <th style="padding: 12px; text-align: center;">Difficulty</th>
                    <th style="padding: 12px; text-align: right;">Score</th>
                    <th style="padding: 12px; text-align: right;">Time</th>
                </tr>
            </thead>
            <tbody>
    """, unsafe_allow_html=True)
    
    for i, entry in enumerate(leaderboard[:10], 1):
        # Medal for top 3
        if i == 1:
            medal = "🥇"
            row_bg = "#FFD700"
        elif i == 2:
            medal = "🥈"
            row_bg = "#C0C0C0"
        elif i == 3:
            medal = "🥉"
            row_bg = "#CD7F32"
        else:
            medal = str(i)
            row_bg = "#D4B896" if i % 2 == 0 else "#C9AD8A"
        
        # Get difficulty name
        difficulty = entry.get("DIFFICULTY", 1)
        diff_name = DIFFICULTY_CONFIG.get(difficulty, {}).get("name", "Unknown")
        
        username = entry.get("SNOWFLAKE_USER", "Anonymous")
        if "@" in username:
            username = username.split("@")[0]
        
        st.markdown(f"""
            <tr style="background: {row_bg};">
                <td style="padding: 12px; text-align: center; font-size: 18px;">
                    {medal}
                </td>
                <td style="padding: 12px; font-weight: bold; color: #2A1810;">
                    {username}
                </td>
                <td style="padding: 12px; text-align: center; color: #555;">
                    {entry.get("RANK", "Rookie")}
                </td>
                <td style="padding: 12px; text-align: center; font-size: 11px; color: #333;">
                    {diff_name}
                </td>
                <td style="padding: 12px; text-align: right; font-weight: bold; color: #2A1810;">
                    {entry.get("SCORE", 0):,}
                </td>
                <td style="padding: 12px; text-align: right; color: #555;">
                    {entry.get("COMPLETION_TIME_HOURS", 0)}h
                </td>
            </tr>
        """, unsafe_allow_html=True)
    
    st.markdown("""
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats summary
    if leaderboard:
        total_games = len(leaderboard)
        avg_score = sum(e.get("SCORE", 0) for e in leaderboard) // max(total_games, 1)
        
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 24px;
            color: #666;
            font-size: 13px;
        ">
            <div>Total Games: <strong>{total_games}</strong></div>
            <div>Average Score: <strong>{avg_score:,}</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    return result


def render_personal_stats(player_stats: dict) -> None:
    """Render personal statistics for the current player."""
    st.markdown("### 📊 Your Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cases Solved", player_stats.get("cases_solved", 0))
    
    with col2:
        st.metric("Total Score", f"{player_stats.get('total_score', 0):,}")
    
    with col3:
        st.metric("Best Score", f"{player_stats.get('best_score', 0):,}")
    
    with col4:
        st.metric("Current Rank", player_stats.get("rank", "Rookie"))

