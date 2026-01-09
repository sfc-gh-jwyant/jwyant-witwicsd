"""Art placeholder component for missing artwork."""

import streamlit as st
from typing import Optional
from enum import Enum


class ArtType(Enum):
    """Types of art in the game."""
    LOCATION = "location"
    LANDMARK = "landmark"
    SUSPECT = "suspect"
    CLUE = "clue"


# Placeholder configurations per art type
PLACEHOLDER_STYLES = {
    ArtType.LOCATION: {
        "width": "100%",
        "height": "400px",
        "icon": "🏙️",
        "bg_color": "#3D2817",
        "border": "2px dashed #C4A35A",
        "label": "Location",
    },
    ArtType.LANDMARK: {
        "width": "200px",
        "height": "150px",
        "icon": "🏛️",
        "bg_color": "#4A7C7C",
        "border": "2px dashed #D4B896",
        "label": "Landmark",
    },
    ArtType.SUSPECT: {
        "width": "150px",
        "height": "200px",
        "icon": "🕵️",
        "bg_color": "#5C1A1A",
        "border": "3px solid #C4A35A",
        "label": "Suspect",
    },
    ArtType.CLUE: {
        "width": "100px",
        "height": "100px",
        "icon": "🔍",
        "bg_color": "#D4B896",
        "border": "1px dashed #3D2817",
        "label": "Clue",
    },
}


def render_art(
    image_url: Optional[str],
    art_type: ArtType,
    alt_text: str,
    caption: Optional[str] = None,
    use_container_width: bool = False,
) -> None:
    """
    Render art with fallback to styled placeholder.
    
    Args:
        image_url: URL to the image, or None for placeholder
        art_type: Type of art being rendered
        alt_text: Alternative text for accessibility
        caption: Optional caption to display
        use_container_width: Whether to expand to container width
    """
    if image_url:
        st.image(
            image_url, 
            caption=caption or alt_text,
            use_container_width=use_container_width,
        )
    else:
        render_placeholder(art_type, alt_text)


def render_placeholder(art_type: ArtType, alt_text: str) -> None:
    """
    Render a styled placeholder for missing art.
    
    Creates a visually appealing placeholder that matches the 
    1992 Carmen Sandiego aesthetic.
    """
    style = PLACEHOLDER_STYLES.get(art_type, PLACEHOLDER_STYLES[ArtType.CLUE])
    
    placeholder_html = f"""
    <div class="art-placeholder art-{art_type.value}" style="
        width: {style['width']};
        height: {style['height']};
        background: linear-gradient(145deg, {style['bg_color']}, {_darken_color(style['bg_color'])});
        border: {style['border']};
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        color: #F5E6D3;
        font-family: 'Playfair Display', 'Georgia', serif;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3), 0 4px 8px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(0,0,0,0.03) 10px,
                rgba(0,0,0,0.03) 20px
            );
            pointer-events: none;
        "></div>
        <span style="font-size: 64px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            {style['icon']}
        </span>
        <span style="
            font-size: 14px; 
            margin-top: 12px; 
            text-align: center; 
            padding: 0 16px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            max-width: 90%;
            overflow: hidden;
            text-overflow: ellipsis;
        ">
            {alt_text}
        </span>
        <span style="
            font-size: 10px; 
            opacity: 0.6; 
            margin-top: 8px;
            font-style: italic;
        ">
            [{style['label']} Art Placeholder]
        </span>
    </div>
    """
    st.markdown(placeholder_html, unsafe_allow_html=True)


def render_location_background(
    image_url: Optional[str],
    location_name: str,
) -> None:
    """
    Render location art as a full-panel background.
    
    Other UI elements will overlay on top of this.
    """
    if image_url:
        # Use CSS to set as background
        st.markdown(f"""
        <style>
            .location-background {{
                background-image: url('{image_url}');
                background-size: cover;
                background-position: center;
                position: relative;
                min-height: 500px;
                border-radius: 8px;
                box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
            }}
            .location-background::after {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(
                    to bottom,
                    rgba(0,0,0,0.3) 0%,
                    rgba(0,0,0,0.1) 50%,
                    rgba(0,0,0,0.4) 100%
                );
                pointer-events: none;
            }}
        </style>
        <div class="location-background"></div>
        """, unsafe_allow_html=True)
    else:
        # Render placeholder as background
        render_placeholder(ArtType.LOCATION, location_name)


def _darken_color(hex_color: str, factor: float = 0.8) -> str:
    """Darken a hex color by a factor."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    darkened = tuple(int(c * factor) for c in rgb)
    return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

