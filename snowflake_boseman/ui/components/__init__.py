"""UI components for the game."""

from .art_placeholder import render_art, render_placeholder, ArtType
from .clue_notebook import render_clue_notebook, render_single_clue
from .suspect_dossier import render_suspect_dossier, render_suspect_card

__all__ = [
    "render_art",
    "render_placeholder",
    "ArtType",
    "render_clue_notebook",
    "render_single_clue",
    "render_suspect_dossier",
    "render_suspect_card",
]

