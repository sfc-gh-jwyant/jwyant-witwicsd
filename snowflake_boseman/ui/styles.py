"""Custom CSS theming for 1992 Carmen Sandiego aesthetic."""

import streamlit as st


# Color palette from 1992 Deluxe Edition
COLORS = {
    "primary_bg": "#5C1A1A",      # Deep burgundy/maroon
    "panel_bg": "#D4B896",         # Warm tan/parchment
    "accent_border": "#3D2817",    # Dark wood brown
    "text_dark": "#2A1810",        # Dark brown on light
    "text_light": "#F5E6D3",       # Cream on dark
    "highlight": "#C4A35A",        # Gold/amber
    "map_ocean": "#4A7C7C",        # Muted teal
    "map_land": "#8B7355",         # Tan/olive
    "success": "#2E7D32",          # Green
    "warning": "#FF9800",          # Orange
    "danger": "#F44336",           # Red
}


def get_css() -> str:
    """Get the complete CSS for the game theme."""
    return f"""
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@400;600&family=IBM+Plex+Mono&display=swap');
    
    /* Global styles */
    .stApp {{
        background: linear-gradient(180deg, {COLORS["primary_bg"]} 0%, #2A1810 100%);
    }}
    
    /* Main content area */
    .main .block-container {{
        padding-top: 2rem;
        max-width: 1200px;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        font-family: 'Playfair Display', Georgia, serif !important;
        color: {COLORS["highlight"]} !important;
    }}
    
    h1 {{
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    
    /* Body text */
    p, li, span {{
        font-family: 'Source Sans Pro', sans-serif;
    }}
    
    /* Buttons - brass/gold style */
    .stButton > button {{
        background: linear-gradient(180deg, {COLORS["highlight"]} 0%, #8B7355 100%) !important;
        color: {COLORS["text_dark"]} !important;
        border: 2px solid {COLORS["accent_border"]} !important;
        border-radius: 8px !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: bold !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 
            inset 0 1px 0 rgba(255,255,255,0.3),
            0 4px 8px rgba(0,0,0,0.3) !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 
            inset 0 1px 0 rgba(255,255,255,0.3),
            0 6px 12px rgba(0,0,0,0.4) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(1px);
        box-shadow: 
            inset 0 2px 4px rgba(0,0,0,0.3),
            0 2px 4px rgba(0,0,0,0.3) !important;
    }}
    
    /* Primary button variant */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(180deg, #4CAF50 0%, #2E7D32 100%) !important;
        color: white !important;
    }}
    
    /* Select boxes */
    .stSelectbox > div > div {{
        background: {COLORS["panel_bg"]} !important;
        border: 2px solid {COLORS["accent_border"]} !important;
        border-radius: 8px !important;
        color: {COLORS["text_dark"]} !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {COLORS["panel_bg"]} !important;
        border: 2px solid {COLORS["accent_border"]} !important;
        border-radius: 8px !important;
        font-family: 'Playfair Display', serif !important;
        color: {COLORS["text_dark"]} !important;
    }}
    
    .streamlit-expanderContent {{
        background: {COLORS["panel_bg"]} !important;
        border: 2px solid {COLORS["accent_border"]} !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-family: 'Playfair Display', serif !important;
        color: {COLORS["highlight"]} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {COLORS["text_light"]} !important;
    }}
    
    /* Info/Warning/Error boxes */
    .stAlert {{
        border-radius: 8px !important;
        border-width: 2px !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS["accent_border"]} 0%, #1a1a1a 100%) !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS["text_light"]} !important;
    }}
    
    /* Parchment panel class */
    .parchment-panel {{
        background: linear-gradient(145deg, {COLORS["panel_bg"]}, #C9AD8A);
        border: 3px solid {COLORS["accent_border"]};
        border-radius: 8px;
        padding: 20px;
        box-shadow: 
            inset 0 2px 4px rgba(255,255,255,0.2),
            0 4px 8px rgba(0,0,0,0.3);
    }}
    
    /* Notebook lines effect */
    .notebook {{
        background: 
            repeating-linear-gradient(
                transparent,
                transparent 28px,
                #ccc 28px,
                #ccc 29px
            ),
            linear-gradient(to bottom, #FFFEF0, #F5E6D3);
        padding: 20px 20px 20px 40px;
        border-left: 4px solid #d44;
        position: relative;
    }}
    
    .notebook::before {{
        content: '';
        position: absolute;
        left: 35px;
        top: 0;
        bottom: 0;
        width: 1px;
        background: #d44;
        opacity: 0.5;
    }}
    
    /* Crime computer terminal effect */
    .terminal {{
        background: #0a0a0a;
        border: 3px solid #333;
        border-radius: 8px;
        padding: 20px;
        font-family: 'IBM Plex Mono', monospace;
        color: #33ff33;
        text-shadow: 0 0 5px #33ff33;
        position: relative;
        overflow: hidden;
    }}
    
    .terminal::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            rgba(0, 0, 0, 0.15),
            rgba(0, 0, 0, 0.15) 1px,
            transparent 1px,
            transparent 2px
        );
        pointer-events: none;
    }}
    
    /* Stamp effect */
    .stamp {{
        display: inline-block;
        padding: 8px 16px;
        border: 3px solid currentColor;
        border-radius: 4px;
        font-weight: bold;
        text-transform: uppercase;
        transform: rotate(-5deg);
        opacity: 0.8;
    }}
    
    .stamp.classified {{
        color: #c00;
    }}
    
    .stamp.solved {{
        color: #2E7D32;
    }}
    
    /* Animation for typewriter effect */
    @keyframes typewriter {{
        from {{ width: 0; }}
        to {{ width: 100%; }}
    }}
    
    .typewriter {{
        overflow: hidden;
        white-space: nowrap;
        animation: typewriter 2s steps(40) forwards;
    }}
    
    /* Pulsing time warning */
    @keyframes pulse-warning {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    .time-critical {{
        animation: pulse-warning 1s infinite;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    </style>
    """


def apply_theme() -> None:
    """Apply the custom theme to the Streamlit app."""
    st.markdown(get_css(), unsafe_allow_html=True)


def render_terminal(content: str, title: str = "SNOWFLAKE CRIMENET") -> None:
    """Render content in a retro terminal style."""
    st.markdown(f"""
    <div class="terminal">
        <div style="
            color: #33ff33;
            font-size: 12px;
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid #33ff33;
        ">
            > {title} v2.0 <span style="float: right;">CONNECTED</span>
        </div>
        <div style="line-height: 1.6;">
            {content}
        </div>
        <div style="margin-top: 12px; opacity: 0.7;">
            > _<span class="blink">|</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stamp(text: str, stamp_type: str = "classified") -> None:
    """Render a rubber stamp effect."""
    st.markdown(f"""
    <span class="stamp {stamp_type}">
        {text}
    </span>
    """, unsafe_allow_html=True)

