"""Clue notebook component for displaying gathered clues."""

import streamlit as st
from typing import Optional

from ...models import Clue
from ...models.clue import ClueType


def render_clue_notebook(clues: list[Clue], expanded: bool = True) -> None:
    """
    Render the detective's notebook with all gathered clues.
    
    Styled like a classic lined notebook with handwritten-style text.
    """
    if not clues:
        st.markdown("""
        <div class="notebook empty-notebook">
            <div class="notebook-content">
                <p style="font-style: italic; color: #666;">
                    📓 Your notebook is empty. Investigate locations to gather clues!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    with st.expander("📓 Detective's Notebook", expanded=expanded):
        # Group clues by type
        destination_clues = [c for c in clues if c.clue_type == ClueType.DESTINATION]
        suspect_clues = [c for c in clues if c.clue_type == ClueType.SUSPECT]
        other_clues = [c for c in clues if c.clue_type == ClueType.RED_HERRING]
        
        if destination_clues:
            st.markdown("### 🗺️ Destination Clues")
            for clue in destination_clues:
                render_single_clue(clue)
        
        if suspect_clues:
            st.markdown("### 🕵️ Suspect Descriptions")
            for clue in suspect_clues:
                render_single_clue(clue)
        
        if other_clues:
            st.markdown("### 📝 Other Information")
            for clue in other_clues:
                render_single_clue(clue)


def render_single_clue(clue: Clue, show_source: bool = True) -> None:
    """Render a single clue entry."""
    source_text = f" — {clue.source}" if show_source and clue.source else ""
    
    st.markdown(f"""
    <div class="clue-entry" style="
        background: linear-gradient(to bottom, #FFFEF0, #F5E6D3);
        border-left: 4px solid #C4A35A;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        font-family: 'Georgia', serif;
    ">
        <div style="
            color: #2A1810;
            font-size: 15px;
            line-height: 1.6;
        ">
            "{clue.text}"
        </div>
        <div style="
            color: #666;
            font-size: 12px;
            margin-top: 6px;
            font-style: italic;
        ">
            {clue.icon}{source_text}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_clue_popup(clues: list[Clue]) -> None:
    """
    Render newly discovered clues in a popup-style display.
    
    Used when player investigates and receives new clues.
    """
    st.markdown("""
    <div style="
        background: #D4B896;
        border: 3px solid #3D2817;
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    ">
        <h3 style="
            color: #2A1810;
            font-family: 'Playfair Display', serif;
            margin-bottom: 16px;
            text-align: center;
        ">
            🔍 Investigation Results
        </h3>
    """, unsafe_allow_html=True)
    
    for clue in clues:
        render_single_clue(clue)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_notebook_summary(clues: list[Clue]) -> None:
    """Render a compact summary of clue counts."""
    destination_count = sum(1 for c in clues if c.clue_type == ClueType.DESTINATION)
    suspect_count = sum(1 for c in clues if c.clue_type == ClueType.SUSPECT)
    other_count = sum(1 for c in clues if c.clue_type == ClueType.RED_HERRING)
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("🗺️ Destination", destination_count)
    with cols[1]:
        st.metric("🕵️ Suspect", suspect_count)
    with cols[2]:
        st.metric("📝 Other", other_count)

