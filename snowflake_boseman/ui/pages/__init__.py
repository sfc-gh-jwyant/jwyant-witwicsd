"""Page modules for the Streamlit app."""

from .main_menu import render_main_menu
from .investigation import render_investigation
from .travel import render_travel
from .case_result import render_case_result
from .high_scores import render_high_scores

__all__ = [
    "render_main_menu",
    "render_investigation",
    "render_travel",
    "render_case_result",
    "render_high_scores",
]

