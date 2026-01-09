"""Suspect dossier component for displaying suspect information."""

import streamlit as st
from typing import Optional

from ...models import Suspect
from .art_placeholder import render_art, ArtType


def render_suspect_dossier(
    suspect: Suspect,
    show_full_details: bool = False,
    known_traits: Optional[dict[str, str]] = None,
) -> None:
    """
    Render a suspect dossier in the style of a classified file.
    
    Args:
        suspect: The suspect to display
        show_full_details: If True, show all details. If False, show only known traits.
        known_traits: Dict of trait names to values that have been discovered
    """
    known_traits = known_traits or {}
    
    st.markdown(f"""
    <div class="suspect-dossier" style="
        background: linear-gradient(145deg, #D4B896, #C4A35A);
        border: 3px solid #3D2817;
        border-radius: 8px;
        padding: 20px;
        position: relative;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        max-width: 300px;
    ">
        <div style="
            position: absolute;
            top: -10px;
            right: 10px;
            background: #5C1A1A;
            color: #F5E6D3;
            padding: 4px 12px;
            font-size: 10px;
            font-weight: bold;
            transform: rotate(3deg);
            box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            CLASSIFIED
        </div>
        
        <h3 style="
            color: #2A1810;
            font-family: 'Playfair Display', serif;
            margin-bottom: 16px;
            border-bottom: 2px solid #3D2817;
            padding-bottom: 8px;
        ">
            SUSPECT DOSSIER
        </h3>
    """, unsafe_allow_html=True)
    
    # Suspect photo
    render_art(
        suspect.mugshot_url,
        ArtType.SUSPECT,
        suspect.name,
    )
    
    st.markdown(f"""
        <div style="margin-top: 16px;">
            <strong style="color: #2A1810;">Name:</strong>
            <span style="color: #333;">{suspect.name if show_full_details else "???"}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Display traits
    traits = [
        ("Hair Color", suspect.hair_color),
        ("Eye Color", suspect.eye_color),
        ("Hobby", suspect.hobby),
        ("Vehicle", suspect.vehicle),
        ("Favorite Food", suspect.favorite_food),
        ("Distinguishing Feature", suspect.distinguishing_feature),
    ]
    
    for trait_name, trait_value in traits:
        if show_full_details:
            display_value = trait_value
        elif trait_name in known_traits:
            display_value = known_traits[trait_name]
        else:
            display_value = "???"
        
        st.markdown(f"""
        <div style="margin-top: 8px;">
            <strong style="color: #2A1810; font-size: 12px;">{trait_name}:</strong>
            <span style="color: #333; font-size: 13px;">{display_value}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_suspect_card(suspect: Suspect, is_selected: bool = False) -> bool:
    """
    Render a compact suspect card for selection.
    
    Returns True if this card was clicked.
    """
    border_color = "#C4A35A" if is_selected else "#3D2817"
    border_width = "4px" if is_selected else "2px"
    
    with st.container():
        st.markdown(f"""
        <div class="suspect-card" style="
            background: linear-gradient(145deg, #D4B896, #C9AD8A);
            border: {border_width} solid {border_color};
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            cursor: pointer;
            transition: all 0.2s ease;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 32px;">🕵️</div>
                <div>
                    <div style="
                        font-weight: bold;
                        color: #2A1810;
                        font-family: 'Playfair Display', serif;
                    ">
                        {suspect.name}
                    </div>
                    <div style="font-size: 11px; color: #555;">
                        {suspect.hair_color} hair • {suspect.hobby}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return st.button(
            f"Select {suspect.name}",
            key=f"select_suspect_{suspect.id}",
            use_container_width=True,
        )


def render_suspect_lineup(suspects: list[Suspect]) -> Optional[str]:
    """
    Render a lineup of suspects for the player to choose from.
    
    Returns the ID of the selected suspect, or None.
    """
    st.markdown("""
    <div style="
        background: #2A1810;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
    ">
        <h3 style="
            color: #C4A35A;
            font-family: 'Playfair Display', serif;
            text-align: center;
            margin: 0;
        ">
            👮 SUSPECT LINEUP 👮
        </h3>
        <p style="
            color: #D4B896;
            text-align: center;
            font-size: 12px;
            margin-top: 8px;
        ">
            Select the suspect you wish to arrest
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display suspects in a grid
    cols = st.columns(3)
    selected_id = None
    
    for i, suspect in enumerate(suspects):
        with cols[i % 3]:
            if render_suspect_card(suspect):
                selected_id = suspect.id
    
    return selected_id

