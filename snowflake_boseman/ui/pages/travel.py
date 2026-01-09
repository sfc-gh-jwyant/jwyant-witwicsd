"""Travel page for destination selection."""

import streamlit as st
from typing import Optional

from ...models import Location, Case
from ...game import GameController
from ..components.world_map import render_world_map, render_travel_options


def render_travel(
    controller: GameController,
    case: Case,
    current_location: Location,
) -> dict:
    """
    Render the travel destination selection screen.
    
    Returns dict with action:
    - {"action": "travel_to", "destination_id": str}
    - {"action": "back"}
    - {"action": None}
    """
    result = {"action": None}
    
    # Header
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #2A1810, #3D2817);
        padding: 16px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 2px solid #C4A35A;
    ">
        <h2 style="
            color: #C4A35A;
            font-family: 'Playfair Display', serif;
            margin: 0;
        ">
            ✈️ TRAVEL DESK
        </h2>
        <p style="
            color: #D4B896;
            margin: 8px 0 0 0;
        ">
            Currently in: <strong>{current_location.city}, {current_location.country}</strong>
        </p>
        <p style="
            color: #999;
            font-size: 13px;
            margin: 4px 0 0 0;
        ">
            ⏱️ Time remaining: {controller.get_time_remaining()} hours
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Investigation"):
        result = {"action": "back"}
        return result
    
    # Get available destinations
    destinations = controller.get_available_destinations()
    visited = case.progress.locations_visited if case.progress else []
    
    if not destinations:
        st.warning("No destinations available with your remaining time!")
        return result
    
    # Layout with map and list
    col_map, col_list = st.columns([2, 1])
    
    with col_map:
        st.markdown("### 🗺️ World Map")
        render_world_map(
            current_location=current_location,
            available_destinations=destinations,
            visited_locations=visited,
        )
    
    with col_list:
        selected_id = render_travel_options(
            current_location=current_location,
            destinations=destinations,
            visited_locations=visited,
        )
        
        if selected_id:
            result = {"action": "travel_to", "destination_id": selected_id}
    
    # Travel info
    st.markdown("""
    <div style="
        background: #D4B896;
        padding: 16px;
        border-radius: 8px;
        margin-top: 20px;
    ">
        <h4 style="color: #2A1810; margin: 0 0 8px 0;">💡 Travel Tips</h4>
        <ul style="color: #333; margin: 0; padding-left: 20px;">
            <li>Travel time depends on distance - nearby cities are faster</li>
            <li>Gray destinations have already been visited</li>
            <li>Follow the clues to track the suspect's path!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    return result


def render_travel_confirmation(
    destination: Location,
    travel_time: int,
    time_remaining: int,
) -> bool:
    """
    Render a confirmation dialog for travel.
    
    Returns True if confirmed, False if cancelled.
    """
    st.markdown(f"""
    <div style="
        background: #3D2817;
        padding: 24px;
        border-radius: 8px;
        border: 2px solid #C4A35A;
        text-align: center;
    ">
        <h3 style="color: #C4A35A; margin: 0;">
            Confirm Travel
        </h3>
        <p style="color: #F5E6D3; font-size: 18px; margin: 16px 0;">
            ✈️ Fly to <strong>{destination.city}, {destination.country}</strong>?
        </p>
        <p style="color: #D4B896;">
            Travel time: <strong>{travel_time} hours</strong>
        </p>
        <p style="color: #999; font-size: 13px;">
            Time after arrival: {time_remaining - travel_time} hours remaining
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✈️ Confirm Travel", use_container_width=True, type="primary"):
            return True
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            return False
    
    return False


def render_travel_result(
    destination: Location,
    hours_spent: int,
    arrived_at_suspect: bool,
) -> None:
    """Render the result of travel."""
    if arrived_at_suspect:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #C4A35A, #8B7355);
            padding: 24px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        ">
            <h2 style="color: #2A1810; margin: 0;">
                🎯 SUSPECT SPOTTED!
            </h2>
            <p style="color: #333; margin: 12px 0 0 0;">
                You've arrived in {destination.city} and the suspect is here!
            </p>
            <p style="color: #555; font-size: 14px;">
                You can now attempt an arrest!
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"✈️ Arrived in {destination.city}, {destination.country} ({hours_spent} hours)")

